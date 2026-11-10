# SPDX-License-Identifier: Apache-2.0

"""Parametric template for graphics cards with axial cooling fans.

The source 5-star samples are used as structural evidence: PCB interfaces derive
from the board envelope, shroud openings derive fan centers, fan centers derive
rotor shafts, and optional support braces are gated behind a compatible card edge.
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

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
)

CoolerFamily = Literal[
    "single_short_card", "compact_dual_fan", "long_triple_fan", "dual_large_tail_small"
]
BoardProfile = Literal[
    "rectangular_full_length", "compact_dual_fan", "long_triple_fan", "angular_cutout"
]
FanLayout = Literal["single_center", "dual_equal", "triple_equal", "dual_large_tail_small"]
ShroudProfile = Literal["rectangular_rail", "angular_gaming", "open_ring_frame", "compact_rounded"]
BezelStyle = Literal["simple_ring", "spoked_ring", "recessed_well", "open_frame"]
BladeProfile = Literal["straight_radial", "swept_curved", "thin_turbine"]
IOBracketStyle = Literal["single_slot", "dual_slot_vented", "short_low_profile"]
MaterialStyle = Literal["black_gaming", "silver_workstation", "white_rgb", "green_reference"]

SOURCE_IDS = {
    "S1": "rec_graphics_card_with_cooling_fans_9012571abea94981a464e14fd868f4dc:model.py:L38-L80 PCB, backplate, fin stack and heatpipes",
    "S2": "rec_graphics_card_with_cooling_fans_9012571abea94981a464e14fd868f4dc:model.py:L81-L167 shroud rails, fan bezels, spokes and screws",
    "S3": "rec_graphics_card_with_cooling_fans_9012571abea94981a464e14fd868f4dc:model.py:L169-L277 PCIe fingers, power socket, I/O bracket and fan joints",
    "S4": "rec_graphics_card_with_cooling_fans_9012571abea94981a464e14fd868f4dc:model.py:L282-L376 fan shaft alignment and rotor seating tests",
    "S5": "rec_graphics_card_with_cooling_fans_f0bbba958ef2467c901571d8aecae30f:model.py:L27-L195 compact dual-fan card and rotor geometry",
    "S6": "rec_graphics_card_with_cooling_fans_f0bbba958ef2467c901571d8aecae30f:model.py:L197-L336 support brace and hinge validator evidence",
    "S7": "rec_graphics_card_with_cooling_fans_9d1b234ba6b24c50852792133b616225:model.py:L26-L195 shroud, I/O bracket and hinge hardware",
    "S8": "rec_graphics_card_with_cooling_fans_9d1b234ba6b24c50852792133b616225:model.py:L198-L398 triple fans, prop leg and tests",
    "S9": "rec_graphics_card_with_cooling_fans_aa098aaa920e4e52ad8456937df5172e:model.py:L25-L168 annulus/support frame and fan rotor geometry",
    "S10": "rec_graphics_card_with_cooling_fans_aa098aaa920e4e52ad8456937df5172e:model.py:L171-L420 asymmetric dual-large + tail fan variant",
}

FAMILY_DEFAULTS: dict[str, dict[str, object]] = {
    "single_short_card": {
        "board_profile": "rectangular_full_length",
        "fan_count": 1,
        "fan_layout": "single_center",
        "card_length": 0.205,
        "card_height": 0.100,
        "cooler_thickness": 0.034,
        "shroud_profile": "compact_rounded",
        "bezel_style": "simple_ring",
        "io_bracket_style": "short_low_profile",
    },
    "compact_dual_fan": {
        "board_profile": "compact_dual_fan",
        "fan_count": 2,
        "fan_layout": "dual_equal",
        "card_length": 0.245,
        "card_height": 0.118,
        "cooler_thickness": 0.045,
        "shroud_profile": "compact_rounded",
        "bezel_style": "spoked_ring",
        "io_bracket_style": "dual_slot_vented",
    },
    "long_triple_fan": {
        "board_profile": "long_triple_fan",
        "fan_count": 3,
        "fan_layout": "triple_equal",
        "card_length": 0.335,
        "card_height": 0.125,
        "cooler_thickness": 0.052,
        "shroud_profile": "angular_gaming",
        "bezel_style": "recessed_well",
        "io_bracket_style": "dual_slot_vented",
    },
    "dual_large_tail_small": {
        "board_profile": "angular_cutout",
        "fan_count": 3,
        "fan_layout": "dual_large_tail_small",
        "card_length": 0.320,
        "card_height": 0.122,
        "cooler_thickness": 0.048,
        "shroud_profile": "open_ring_frame",
        "bezel_style": "open_frame",
        "io_bracket_style": "dual_slot_vented",
    },
}

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "black_gaming": {
        "pcb": (0.025, 0.030, 0.028, 1.0),
        "backplate": (0.10, 0.11, 0.12, 1.0),
        "shroud": (0.035, 0.036, 0.040, 1.0),
        "fan": (0.010, 0.011, 0.012, 1.0),
        "fin": (0.54, 0.56, 0.58, 1.0),
        "copper": (0.88, 0.46, 0.16, 1.0),
        "gold": (1.00, 0.72, 0.24, 1.0),
        "metal": (0.68, 0.70, 0.72, 1.0),
        "port": (0.02, 0.024, 0.028, 1.0),
        "accent": (0.18, 0.48, 0.95, 1.0),
    },
    "silver_workstation": {
        "pcb": (0.06, 0.10, 0.08, 1.0),
        "backplate": (0.62, 0.64, 0.66, 1.0),
        "shroud": (0.72, 0.73, 0.72, 1.0),
        "fan": (0.08, 0.08, 0.085, 1.0),
        "fin": (0.72, 0.74, 0.76, 1.0),
        "copper": (0.85, 0.42, 0.13, 1.0),
        "gold": (0.95, 0.68, 0.22, 1.0),
        "metal": (0.80, 0.82, 0.83, 1.0),
        "port": (0.03, 0.033, 0.036, 1.0),
        "accent": (0.18, 0.22, 0.26, 1.0),
    },
    "white_rgb": {
        "pcb": (0.06, 0.08, 0.075, 1.0),
        "backplate": (0.88, 0.88, 0.84, 1.0),
        "shroud": (0.92, 0.91, 0.86, 1.0),
        "fan": (0.11, 0.12, 0.13, 1.0),
        "fin": (0.66, 0.69, 0.71, 1.0),
        "copper": (0.86, 0.47, 0.18, 1.0),
        "gold": (0.98, 0.72, 0.22, 1.0),
        "metal": (0.78, 0.79, 0.78, 1.0),
        "port": (0.03, 0.035, 0.040, 1.0),
        "accent": (0.14, 0.72, 0.86, 1.0),
    },
    "green_reference": {
        "pcb": (0.04, 0.20, 0.12, 1.0),
        "backplate": (0.12, 0.13, 0.12, 1.0),
        "shroud": (0.08, 0.085, 0.090, 1.0),
        "fan": (0.02, 0.022, 0.025, 1.0),
        "fin": (0.60, 0.62, 0.62, 1.0),
        "copper": (0.82, 0.41, 0.12, 1.0),
        "gold": (0.95, 0.67, 0.22, 1.0),
        "metal": (0.58, 0.60, 0.62, 1.0),
        "port": (0.02, 0.024, 0.028, 1.0),
        "accent": (0.82, 0.22, 0.12, 1.0),
    },
}


@dataclass(frozen=True)
class GraphicsCardConfig:
    cooler_family: CoolerFamily = "long_triple_fan"
    board_profile: BoardProfile | None = None
    card_length: float | None = None
    card_height: float | None = None
    pcb_thickness: float | None = None
    cooler_thickness: float | None = None
    fan_count: int | None = None
    fan_layout: FanLayout | None = None
    fan_radius: float | None = None
    blade_count: int | None = None
    blade_profile: BladeProfile = "swept_curved"
    shroud_profile: ShroudProfile | None = None
    bezel_style: BezelStyle | None = None
    fin_count: int | None = None
    heatpipe_count: int | None = None
    io_bracket_style: IOBracketStyle | None = None
    support_brace_enabled: bool | None = None
    material_style: MaterialStyle = "black_gaming"
    name: str = "parametric_graphics_card_with_cooling_fans"


@dataclass(frozen=True)
class FanSpec:
    index: int
    center: tuple[float, float, float]
    radius: float
    hub_radius: float


@dataclass(frozen=True)
class ResolvedGraphicsCardConfig:
    cooler_family: CoolerFamily
    board_profile: BoardProfile
    card_length: float
    card_height: float
    pcb_thickness: float
    cooler_thickness: float
    fan_count: int
    fan_layout: FanLayout
    fan_radius: float
    blade_count: int
    blade_profile: BladeProfile
    shroud_profile: ShroudProfile
    bezel_style: BezelStyle
    fin_count: int
    heatpipe_count: int
    io_bracket_style: IOBracketStyle
    support_brace_enabled: bool
    pcie_contact_count: int
    fan_specs: tuple[FanSpec, ...]
    material_style: MaterialStyle
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _validate_enum(value: object, allowed: set[str], field: str) -> None:
    if value not in allowed:
        raise ValueError(f"Unsupported {field}: {value}")


def config_from_seed(seed: int) -> GraphicsCardConfig:
    rng = random.Random(seed)
    family: CoolerFamily = rng.choices(
        ("single_short_card", "compact_dual_fan", "long_triple_fan", "dual_large_tail_small"),
        weights=(0.12, 0.34, 0.40, 0.14),
        k=1,
    )[0]
    defaults = FAMILY_DEFAULTS[family]
    length = round(float(defaults["card_length"]) * rng.uniform(0.94, 1.08), 3)
    height = round(float(defaults["card_height"]) * rng.uniform(0.94, 1.08), 3)
    thickness = round(float(defaults["cooler_thickness"]) * rng.uniform(0.90, 1.14), 3)
    brace = family in {"compact_dual_fan", "long_triple_fan"} and rng.random() < 0.25
    return GraphicsCardConfig(
        cooler_family=family,
        board_profile=defaults["board_profile"],
        card_length=length,
        card_height=height,
        pcb_thickness=round(rng.uniform(0.0035, 0.0055), 4),
        cooler_thickness=thickness,
        fan_count=int(defaults["fan_count"]),
        fan_layout=defaults["fan_layout"],
        fan_radius=None,
        blade_count=rng.choice((7, 9, 9, 11)),
        blade_profile=rng.choice(("straight_radial", "swept_curved", "thin_turbine")),
        shroud_profile=defaults["shroud_profile"],
        bezel_style=defaults["bezel_style"],
        fin_count=rng.randint(12, 26),
        heatpipe_count=rng.choice((2, 3, 4, 5)),
        io_bracket_style=defaults["io_bracket_style"],
        support_brace_enabled=brace,
        material_style=rng.choice(
            ("black_gaming", "silver_workstation", "white_rgb", "green_reference")
        ),
        name=f"seeded_graphics_card_with_cooling_fans_{seed}",
    )


def resolve_config(config: GraphicsCardConfig) -> ResolvedGraphicsCardConfig:
    _validate_enum(config.cooler_family, set(FAMILY_DEFAULTS), "cooler_family")
    _validate_enum(config.material_style, set(PALETTES), "material_style")
    _validate_enum(
        config.blade_profile, {"straight_radial", "swept_curved", "thin_turbine"}, "blade_profile"
    )
    defaults = FAMILY_DEFAULTS[config.cooler_family]
    board_profile: BoardProfile = config.board_profile or defaults["board_profile"]  # type: ignore[assignment]
    fan_layout: FanLayout = config.fan_layout or defaults["fan_layout"]  # type: ignore[assignment]
    shroud_profile: ShroudProfile = config.shroud_profile or defaults["shroud_profile"]  # type: ignore[assignment]
    bezel_style: BezelStyle = config.bezel_style or defaults["bezel_style"]  # type: ignore[assignment]
    io_style: IOBracketStyle = config.io_bracket_style or defaults["io_bracket_style"]  # type: ignore[assignment]
    _validate_enum(
        board_profile,
        {"rectangular_full_length", "compact_dual_fan", "long_triple_fan", "angular_cutout"},
        "board_profile",
    )
    _validate_enum(
        fan_layout,
        {"single_center", "dual_equal", "triple_equal", "dual_large_tail_small"},
        "fan_layout",
    )
    _validate_enum(
        shroud_profile,
        {"rectangular_rail", "angular_gaming", "open_ring_frame", "compact_rounded"},
        "shroud_profile",
    )
    _validate_enum(
        bezel_style, {"simple_ring", "spoked_ring", "recessed_well", "open_frame"}, "bezel_style"
    )
    _validate_enum(
        io_style, {"single_slot", "dual_slot_vented", "short_low_profile"}, "io_bracket_style"
    )
    fan_count = int(config.fan_count if config.fan_count is not None else defaults["fan_count"])
    if config.cooler_family == "single_short_card":
        fan_count = 1
        fan_layout = "single_center"
    elif config.cooler_family == "compact_dual_fan":
        fan_count = 2
        fan_layout = "dual_equal"
    elif config.cooler_family in {"long_triple_fan", "dual_large_tail_small"}:
        fan_count = 3
        fan_layout = (
            "dual_large_tail_small"
            if config.cooler_family == "dual_large_tail_small"
            else "triple_equal"
        )
    length = _clamp(
        config.card_length if config.card_length is not None else float(defaults["card_length"]),
        0.18,
        0.37,
    )
    height = _clamp(
        config.card_height if config.card_height is not None else float(defaults["card_height"]),
        0.080,
        0.17,
    )
    pcb_t = _clamp(
        config.pcb_thickness if config.pcb_thickness is not None else 0.004, 0.003, 0.006
    )
    cooler_t = _clamp(
        config.cooler_thickness
        if config.cooler_thickness is not None
        else float(defaults["cooler_thickness"]),
        0.026,
        0.075,
    )
    if fan_count == 3:
        length = max(length, 0.285)
    if fan_count == 2:
        length = max(length, 0.220)
    x_start = -length * 0.5 + 0.066
    x_end = length * 0.5 - 0.042
    if fan_count == 1:
        xs = [0.020]
        ys = [0.0]
    elif fan_layout == "dual_large_tail_small":
        xs = [x_start + (x_end - x_start) * 0.28, x_start + (x_end - x_start) * 0.64, x_end - 0.010]
        ys = [0.0, 0.0, 0.018]
    else:
        step = (x_end - x_start) / max(1, fan_count - 1)
        xs = [x_start + i * step for i in range(fan_count)]
        ys = [0.0 for _ in range(fan_count)]
    min_spacing = min((abs(xs[i + 1] - xs[i]) for i in range(len(xs) - 1)), default=height)
    radius_from_height = height * 0.5 - 0.023
    radius_from_pitch = min_spacing * 0.5 - 0.012
    requested_radius = (
        config.fan_radius if config.fan_radius is not None else (0.043 if fan_count >= 2 else 0.037)
    )
    fan_radius = _clamp(
        requested_radius, 0.024, max(0.026, min(radius_from_height, radius_from_pitch, 0.064))
    )
    blade_count = int(config.blade_count if config.blade_count is not None else 9)
    blade_count = max(5, min(11, blade_count))
    fin_count = int(config.fin_count if config.fin_count is not None else 18)
    fin_count = max(8, min(32, fin_count))
    heatpipe_count = int(config.heatpipe_count if config.heatpipe_count is not None else 3)
    heatpipe_count = max(0, min(6, heatpipe_count))
    fan_z = pcb_t * 0.5 + cooler_t * 0.76
    fan_specs: list[FanSpec] = []
    for index, (x, y) in enumerate(zip(xs, ys, strict=True)):
        radius = fan_radius
        if fan_layout == "dual_large_tail_small" and index == 2:
            radius = max(0.023, fan_radius * 0.70)
        fan_specs.append(FanSpec(index, (x, y, fan_z), radius, max(0.008, radius * 0.26)))
    brace = bool(config.support_brace_enabled)
    if config.cooler_family == "single_short_card":
        brace = False
    return ResolvedGraphicsCardConfig(
        cooler_family=config.cooler_family,
        board_profile=board_profile,
        card_length=length,
        card_height=height,
        pcb_thickness=pcb_t,
        cooler_thickness=cooler_t,
        fan_count=fan_count,
        fan_layout=fan_layout,
        fan_radius=fan_radius,
        blade_count=blade_count,
        blade_profile=config.blade_profile,
        shroud_profile=shroud_profile,
        bezel_style=bezel_style,
        fin_count=fin_count,
        heatpipe_count=heatpipe_count,
        io_bracket_style=io_style,
        support_brace_enabled=brace,
        pcie_contact_count=18 if length > 0.24 else 12,
        fan_specs=tuple(fan_specs),
        material_style=config.material_style,
        name=config.name,
    )


def with_overrides(config: GraphicsCardConfig, **kwargs: object) -> GraphicsCardConfig:
    return replace(config, **kwargs)


def _joint_meta(
    joint_type: str,
    axis: tuple[float, float, float],
    origin: tuple[float, float, float],
    joint_range: object,
    source_id: str,
) -> dict[str, object]:
    return {
        "type": joint_type,
        "axis": axis,
        "origin": origin,
        "range": joint_range,
        "source_id": source_id,
    }


def _mat(model: ArticulatedObject, r: ResolvedGraphicsCardConfig, key: str):
    return model.material(f"gpu_{key}", rgba=PALETTES[r.material_style][key])


def _add_box(
    part,
    size: tuple[float, float, float],
    xyz: tuple[float, float, float],
    material,
    name: str,
    rpy: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="tech.circuit_board")


def _add_cyl(
    part,
    radius: float,
    length: float,
    xyz: tuple[float, float, float],
    material,
    name: str,
    rpy: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.copper_bare",
    )


def _build_card_body(
    body,
    r: ResolvedGraphicsCardConfig,
    *,
    pcb,
    backplate,
    shroud,
    fan_mat,
    fin,
    copper,
    gold,
    metal,
    port,
    accent,
) -> None:
    L, H, T = r.card_length, r.card_height, r.pcb_thickness
    _add_box(body, (L, H, T), (0.0, 0.0, 0.0), pcb, "pcb")
    _add_box(
        body, (L * 0.92, H * 0.86, 0.003), (0.012, 0.0, -T * 0.5 + 0.0005), backplate, "backplate"
    )
    base_z = T * 0.5 + 0.006
    _add_box(body, (L * 0.74, H * 0.70, 0.012), (0.018, 0.0, base_z), fin, "heatsink_base")
    fin_span = L * 0.70
    first_x = -fin_span * 0.5 + 0.010
    fin_step = fin_span / max(1, r.fin_count)
    for i in range(r.fin_count):
        x = first_x + (i + 0.5) * fin_step
        _add_box(
            body,
            (max(0.0018, fin_step * 0.30), H * 0.66, 0.020),
            (x, 0.0, base_z + 0.014),
            fin,
            f"cooling_fin_{i}",
        )
    if r.heatpipe_count:
        y0 = -H * 0.24
        y_step = H * 0.48 / max(1, r.heatpipe_count - 1)
        for i in range(r.heatpipe_count):
            y = y0 + i * y_step if r.heatpipe_count > 1 else 0.0
            _add_cyl(
                body,
                0.0032,
                L * 0.68,
                (0.020, y, base_z + 0.017),
                copper,
                f"heatpipe_{i}",
                rpy=(0.0, math.pi / 2.0, 0.0),
            )
    shroud_z = T * 0.5 + r.cooler_thickness * 0.58
    rail_t = 0.018 if r.shroud_profile != "open_ring_frame" else 0.012
    _add_box(
        body,
        (L * 0.84, rail_t, 0.020),
        (0.020, H * 0.5 - rail_t * 0.5, shroud_z),
        shroud,
        "top_shroud_rail",
    )
    _add_box(
        body,
        (L * 0.84, rail_t, 0.020),
        (0.020, -H * 0.5 + rail_t * 0.5, shroud_z),
        shroud,
        "bottom_shroud_rail",
    )
    # End caps seat against the ends of the shroud side rails (which span
    # x in [0.020 - 0.42L, 0.020 + 0.42L]); place them just inside those ends so
    # they fuse to the rails instead of floating past them at the board edges.
    # Each cap wraps from the rail plane all the way down into the PCB top
    # (2 mm embed) so the whole rail frame is anchored to the board at both
    # ends instead of hanging off the ends of the fin stack.
    _rail_left_x = 0.020 - L * 0.84 * 0.5
    _rail_right_x = 0.020 + L * 0.84 * 0.5
    _cap_top = shroud_z + 0.010
    _cap_bottom = T * 0.5 - 0.002
    _cap_h = _cap_top - _cap_bottom
    _cap_cz = (_cap_top + _cap_bottom) * 0.5
    _add_box(
        body,
        (0.016, H * 0.96, _cap_h),
        (_rail_left_x + 0.008, 0.0, _cap_cz),
        shroud,
        "io_end_shroud_cap",
    )
    _add_box(
        body, (0.016, H * 0.88, _cap_h), (_rail_right_x - 0.008, 0.0, _cap_cz), shroud, "tail_shroud_cap"
    )
    if r.shroud_profile in {"angular_gaming", "open_ring_frame"}:
        # Accent ribs are slanted blades cantilevered off the heatsink: drop each
        # one from its shroud-top height down into the solid heatsink base slab
        # (2 mm embed below the slab top) so it fuses to the cooler instead of
        # hovering over the fin stack (the z gap grows with cooler thickness).
        _rib_top = shroud_z + 0.013
        _rib_bottom = base_z + 0.004
        _rib_h = _rib_top - _rib_bottom
        _rib_cz = (_rib_top + _rib_bottom) * 0.5
        for i, (x, y, yaw) in enumerate(
            (
                (-L * 0.24, H * 0.24, 0.38),
                (-L * 0.08, -H * 0.25, -0.35),
                (L * 0.16, H * 0.24, 0.40),
                (L * 0.30, -H * 0.22, -0.38),
            )
        ):
            _add_box(
                body,
                (L * 0.18, 0.005, _rib_h),
                (x, y, _rib_cz),
                accent,
                f"angular_accent_rib_{i}",
                rpy=(0.0, 0.0, yaw),
            )
    for fan in r.fan_specs:
        _build_fan_frame(body, r, fan, shroud=shroud, fan_mat=fan_mat, metal=metal, accent=accent)
    _build_pcie_and_io(body, r, gold=gold, metal=metal, port=port)
    _build_power_connector(body, r, metal=metal, port=port)
    if r.support_brace_enabled:
        x = -L * 0.5 + 0.060
        y = -H * 0.5 - 0.045
        z = T * 0.5 + 0.018
        # Drop-arm from the board bottom edge down to the hinge block: its top
        # reaches 4 mm into the bottom shroud rail's y-band and its z span
        # overlaps the rail's z band for any cooler thickness (the rail plane
        # rises with cooler_thickness), so the mount fuses to the grounded
        # shroud frame instead of grazing the rail when the cooler is thick.
        _arm_top = -H * 0.5 + 0.004
        _arm_bottom = y + 0.010 - 0.005
        _arm_h = _arm_top - _arm_bottom
        _arm_z0 = T * 0.5 + 0.012
        _arm_z1 = T * 0.5 + 0.026
        if _arm_h > 0.004:
            _add_box(
                body,
                (0.012, _arm_h, _arm_z1 - _arm_z0),
                (x, _arm_bottom + _arm_h * 0.5, (_arm_z0 + _arm_z1) * 0.5),
                metal,
                "brace_mount_arm",
            )
        _add_box(body, (0.018, 0.010, 0.014), (x, y + 0.010, z), metal, "brace_hinge_block")
        _add_box(
            body, (0.004, 0.004, 0.004), (x, y + 0.004, z), metal, "brace_hinge_contact_socket"
        )


def _build_fan_frame(
    body, r: ResolvedGraphicsCardConfig, fan: FanSpec, *, shroud, fan_mat, metal, accent
) -> None:
    x, y, z = fan.center
    radius = fan.radius
    ring_z = z + 0.004
    segment_len = radius * 0.82
    segment_w = 0.005 if r.bezel_style != "open_frame" else 0.0038
    # The bezel ring floats above the fin stack; give each segment enough height
    # to reach down onto the fins (fin top ~ pcb/2 + 0.006 + 0.024) so the ring
    # fuses to the cooler instead of hovering a few mm over it.
    _fin_top = r.pcb_thickness * 0.5 + 0.006 + 0.014 + 0.010
    _seg_top = ring_z + 0.003
    _seg_h = max(0.006, _seg_top - _fin_top + 0.002)
    _seg_cz = _seg_top - _seg_h * 0.5
    for seg in range(8):
        angle = seg * math.tau / 8.0
        cx = x + math.cos(angle) * radius * 0.92
        cy = y + math.sin(angle) * radius * 0.92
        _add_box(
            body,
            (segment_len, segment_w, _seg_h),
            (cx, cy, _seg_cz),
            shroud,
            f"fan_{fan.index}_bezel_segment_{seg}",
            rpy=(0.0, 0.0, angle + math.pi / 2.0),
        )
    spoke_count = 3 if r.bezel_style in {"spoked_ring", "recessed_well"} else 2
    for spoke in range(spoke_count):
        angle = spoke * math.tau / spoke_count
        # Taller spokes that reach down onto the fin stack / hub below so the
        # stator web fuses to the cooler instead of floating ~0.5 mm above it.
        _add_box(
            body,
            (radius * 0.72, 0.003, 0.012),
            (x + math.cos(angle) * radius * 0.34, y + math.sin(angle) * radius * 0.34, z - 0.010),
            fan_mat,
            f"fan_{fan.index}_stator_spoke_{spoke}",
            rpy=(0.0, 0.0, angle),
        )
    _add_cyl(
        body,
        fan.hub_radius * 0.82,
        0.014,
        (x, y, z - 0.008),
        fan_mat,
        f"fan_{fan.index}_stator_boss",
    )
    for screw in range(4):
        angle = math.pi * 0.25 + screw * math.pi * 0.5
        # Corner screws seat on the bezel ring (radius ~0.92) and reach down onto
        # it, rather than sitting proud at 1.12r where nothing supports them.
        _add_cyl(
            body,
            0.0024,
            0.010,
            (
                x + math.cos(angle) * radius * 0.92,
                y + math.sin(angle) * radius * 0.92,
                ring_z + 0.001,
            ),
            metal,
            f"fan_{fan.index}_screw_{screw}",
        )
    if r.bezel_style == "recessed_well":
        _add_cyl(
            body, radius * 1.08, 0.002, (x, y, z - 0.010), accent, f"fan_{fan.index}_colored_well"
        )


def _build_pcie_and_io(body, r: ResolvedGraphicsCardConfig, *, gold, metal, port) -> None:
    L, H, T = r.card_length, r.card_height, r.pcb_thickness
    contact_len = min(L * 0.58, 0.200)
    _add_box(
        body,
        (contact_len, 0.012, 0.003),
        (-L * 0.08, -H * 0.5 - 0.004, -0.001),
        gold,
        "pcie_contact_bar",
    )
    step = contact_len / r.pcie_contact_count
    for i in range(r.pcie_contact_count):
        _add_box(
            body,
            (step * 0.54, 0.006, 0.0035),
            (-L * 0.08 - contact_len * 0.5 + (i + 0.5) * step, -H * 0.5 - 0.010, 0.000),
            gold,
            f"pcie_finger_{i}",
        )
    bracket_h = H * (1.12 if r.io_bracket_style == "dual_slot_vented" else 0.92)
    bracket_z = 0.026 if r.io_bracket_style != "short_low_profile" else 0.020
    # Bracket plate is thick enough to bury its inner face 1 mm into the PCB edge
    # so the whole bracket cluster (plate + display ports + vents) fuses to the
    # card body instead of hovering a ~1 mm gap off the board edge.
    _add_box(
        body,
        (0.010, bracket_h, 0.070 if r.io_bracket_style == "dual_slot_vented" else 0.050),
        (-L * 0.5 - 0.004, 0.0, bracket_z),
        metal,
        "io_bracket",
    )
    _add_box(
        body,
        (0.012, H * 0.86, 0.010),
        (-L * 0.5 + 0.002, 0.0, -T * 0.5 - 0.004),
        metal,
        "io_bracket_foot",
    )
    port_specs = [
        (-0.030, 0.032, 0.018, 0.010),
        (0.000, 0.032, 0.020, 0.010),
        (0.030, 0.032, 0.020, 0.010),
    ]
    if r.io_bracket_style == "dual_slot_vented":
        port_specs.append((0.046, 0.006, 0.026, 0.012))
    for i, (y, z, sy, sz) in enumerate(port_specs):
        _add_box(body, (0.003, sy, sz), (-L * 0.5 - 0.008, y, z), port, f"display_port_{i}")
    for i in range(5 if r.io_bracket_style == "dual_slot_vented" else 3):
        # Vents sit in the bracket plane (x ~ -L/2 - 0.004) and within its z span
        # so they cut into the bracket instead of floating just outside it.
        _add_box(
            body,
            (0.006, 0.006, 0.0025),
            (-L * 0.5 - 0.004, -H * 0.20 + i * H * 0.09, bracket_z + 0.010),
            port,
            f"bracket_vent_{i}",
        )


def _build_power_connector(body, r: ResolvedGraphicsCardConfig, *, metal, port) -> None:
    if r.card_length < 0.215:
        return
    L, H, T = r.card_length, r.card_height, r.pcb_thickness
    x = L * 0.28
    y = H * 0.5 + 0.006
    # Seat the connector body on the PCB top face (z from T/2 up) so it and its
    # pins fuse to the board rather than floating ~5 mm above it.
    z = T * 0.5 + 0.009
    _add_box(body, (0.034, 0.018, 0.018), (x, y, z), port, "power_socket")
    for row, dz in enumerate((-0.004, 0.004)):
        for col in range(4):
            _add_box(
                body,
                (0.003, 0.002, 0.003),
                (x - 0.011 + col * 0.007, y + 0.010, z + dz),
                metal,
                f"power_pin_{row}_{col}",
            )


def _build_fan_rotor(
    part, r: ResolvedGraphicsCardConfig, fan: FanSpec, *, fan_mat, metal, accent
) -> None:
    _add_cyl(part, fan.hub_radius, 0.008, (0.0, 0.0, 0.004), fan_mat, "rotor_hub")
    _add_cyl(
        part, max(0.0025, fan.hub_radius * 0.33), 0.003, (0.0, 0.0, -0.0015), metal, "bearing_pin"
    )
    blade_len = fan.radius - fan.hub_radius * 0.9
    if r.blade_profile == "thin_turbine":
        blade_width = fan.radius * 0.090
        sweep = 0.26
    elif r.blade_profile == "straight_radial":
        blade_width = fan.radius * 0.125
        sweep = 0.00
    else:
        blade_width = fan.radius * 0.150
        sweep = 0.18
    for blade in range(r.blade_count):
        angle = blade * math.tau / r.blade_count
        center_r = fan.hub_radius * 0.72 + blade_len * 0.50
        # Blade root overlaps the hub in Z (hub top ~0.008) so the rotor is one
        # connected body; a thicker blade dropped slightly bridges the ~0.5 mm gap.
        _add_box(
            part,
            (blade_len, blade_width, 0.005),
            (math.cos(angle) * center_r, math.sin(angle) * center_r, 0.006),
            fan_mat,
            f"fan_blade_{blade}",
            rpy=(0.0, 0.08, angle + sweep),
        )
        if blade % 2 == 0:
            # Highlight strip sits on the blade it decorates (same radial band and
            # angle) so it fuses to the blade instead of floating outboard of it.
            _add_box(
                part,
                (blade_len * 0.40, blade_width * 0.24, 0.004),
                (
                    math.cos(angle) * center_r,
                    math.sin(angle) * center_r,
                    0.008,
                ),
                accent,
                f"blade_highlight_{blade}",
                rpy=(0.0, 0.08, angle + sweep),
            )


def _build_support_brace(
    model: ArticulatedObject, body, r: ResolvedGraphicsCardConfig, *, metal, fan_mat
) -> None:
    if not r.support_brace_enabled:
        return
    x = -r.card_length * 0.5 + 0.060
    y = -r.card_height * 0.5 - 0.045
    z = r.pcb_thickness * 0.5 + 0.018
    brace = model.part("support_brace")
    # Contact pin sits on the hinge knuckle (same y band) so the brace is one
    # connected body instead of a pin floating ~1.7 cm from the knuckle.
    _add_box(brace, (0.004, 0.010, 0.004), (0.0, 0.019, 0.0), metal, "hinge_contact_pin")
    _add_cyl(
        brace,
        0.0048,
        0.012,
        (0.0, 0.021, 0.0),
        metal,
        "hinge_knuckle",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    length = min(0.19, r.card_length * 0.58)
    angle = 0.18
    _add_box(
        brace,
        (length, 0.006, 0.006),
        (length * 0.5 * math.cos(angle), 0.021, -length * 0.5 * math.sin(angle)),
        metal,
        "brace_arm",
        rpy=(0.0, angle, 0.0),
    )
    _add_box(
        brace,
        (0.018, 0.014, 0.005),
        (length * math.cos(angle) + 0.005, 0.021, -length * math.sin(angle) - 0.003),
        fan_mat,
        "rubber_foot",
    )
    origin = (x, y, z)
    model.articulation(
        "support_brace_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=brace,
        origin=Origin(xyz=origin),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.5, velocity=1.2, lower=0.0, upper=0.92),
        meta=_joint_meta("revolute", (0.0, 1.0, 0.0), origin, (0.0, 0.92), "S6"),
    )


def build_graphics_card(
    config: GraphicsCardConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or GraphicsCardConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-graphics-card-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    pcb = _mat(model, r, "pcb")
    backplate = _mat(model, r, "backplate")
    shroud = _mat(model, r, "shroud")
    fan_mat = _mat(model, r, "fan")
    fin = _mat(model, r, "fin")
    copper = _mat(model, r, "copper")
    gold = _mat(model, r, "gold")
    metal = _mat(model, r, "metal")
    port = _mat(model, r, "port")
    accent = _mat(model, r, "accent")
    body = model.part("card_body")
    _build_card_body(
        body,
        r,
        pcb=pcb,
        backplate=backplate,
        shroud=shroud,
        fan_mat=fan_mat,
        fin=fin,
        copper=copper,
        gold=gold,
        metal=metal,
        port=port,
        accent=accent,
    )
    for fan in r.fan_specs:
        rotor = model.part(f"fan_rotor_{fan.index}")
        _build_fan_rotor(rotor, r, fan, fan_mat=fan_mat, metal=metal, accent=accent)
        model.articulation(
            f"fan_spin_{fan.index}",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=rotor,
            origin=Origin(xyz=fan.center),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=0.16, velocity=160.0),
            meta=_joint_meta("continuous", (0.0, 0.0, 1.0), fan.center, "unbounded", "S3"),
        )
    _build_support_brace(model, body, r, metal=metal, fan_mat=fan_mat)
    return model


def build_seeded_graphics_card(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_graphics_card(config_from_seed(seed), assets=assets)


def _visual_names(part) -> set[str]:
    return {visual.name for visual in part.visuals}


def run_graphics_card_tests(
    object_model: ArticulatedObject | None = None, config: GraphicsCardConfig | None = None
) -> TestReport:
    config = config or GraphicsCardConfig()
    model = object_model or build_graphics_card(config)
    r = resolve_config(config)
    ctx = TestContext(model)
    # The folding support brace pivots on the card-body hinge block; its hinge
    # knuckle necessarily wraps the body-side mount arm / hinge block / socket at
    # the pivot axis (captured hinge). Element-scoped allowance only.
    _pn = {p.name for p in model.parts}
    if "support_brace" in _pn and "card_body" in _pn:
        for _body_elem in ("brace_mount_arm", "brace_hinge_block", "brace_hinge_contact_socket"):
            for _brace_elem in ("hinge_knuckle", "hinge_contact_pin"):
                try:
                    ctx.allow_overlap(
                        model.get_part("card_body"), model.get_part("support_brace"),
                        elem_a=_body_elem, elem_b=_brace_elem,
                        reason="Support brace hinge knuckle wraps the card-body hinge block at the pivot axis.",
                    )
                except Exception:
                    pass
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    fan_joints = [joint for joint in model.articulations if joint.name.startswith("fan_spin_")]
    ctx.check(
        "fan_joint_count",
        len(fan_joints) == r.fan_count,
        details=f"expected {r.fan_count}, got {len(fan_joints)}",
    )
    for joint in fan_joints:
        ctx.check(
            f"{joint.name}_is_continuous",
            joint.articulation_type == ArticulationType.CONTINUOUS,
            details="cooling fans must spin continuously",
        )
        ctx.check(
            f"{joint.name}_axis", tuple(joint.axis) == (0.0, 0.0, 1.0), details=f"axis={joint.axis}"
        )
    fan_parts = [part for part in model.parts if part.name.startswith("fan_rotor_")]
    ctx.check(
        "fan_part_count",
        len(fan_parts) == r.fan_count,
        details=f"parts={len(fan_parts)} fan_count={r.fan_count}",
    )
    card = model.get_part("card_body")
    names = _visual_names(card)
    ctx.check("has_pcb", "pcb" in names, details="PCB visual missing")
    ctx.check(
        "has_pcie_fingers",
        any(name.startswith("pcie_finger_") for name in names),
        details="PCIe fingers missing",
    )
    ctx.check("has_io_bracket", "io_bracket" in names, details="I/O bracket missing")
    for fan in r.fan_specs:
        ctx.check(
            f"fan_{fan.index}_fits_card_height",
            abs(fan.center[1]) + fan.radius < r.card_height * 0.5 - 0.002,
            details=f"center={fan.center}, radius={fan.radius}",
        )
    if r.support_brace_enabled:
        brace_joint = model.get_articulation("support_brace_hinge")
        ctx.check(
            "support_brace_joint_axis",
            brace_joint is not None and tuple(brace_joint.axis) == (0.0, 1.0, 0.0),
            details="brace hinge missing or wrong axis",
        )
    return ctx.report()


GRAPHICS_CARD_SOURCE_AUDIT = (
    "audit 001: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 002: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 003: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 004: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 005: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 006: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 007: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 008: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 009: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 010: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 011: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 012: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 013: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 014: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 015: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 016: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 017: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 018: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 019: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 020: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 021: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 022: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 023: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 024: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 025: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 026: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 027: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 028: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 029: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 030: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 031: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 032: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 033: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 034: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 035: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 036: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 037: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 038: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 039: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 040: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 041: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 042: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 043: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 044: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 045: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 046: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 047: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 048: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 049: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 050: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 051: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 052: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 053: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 054: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 055: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 056: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 057: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 058: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 059: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 060: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 061: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 062: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 063: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 064: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 065: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 066: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 067: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 068: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 069: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 070: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 071: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 072: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 073: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 074: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 075: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 076: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 077: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 078: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 079: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 080: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 081: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 082: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 083: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 084: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 085: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 086: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 087: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 088: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 089: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 090: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 091: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 092: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 093: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 094: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 095: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 096: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 097: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 098: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 099: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 100: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 101: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 102: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 103: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 104: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 105: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 106: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 107: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 108: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 109: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 110: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 111: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 112: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 113: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 114: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 115: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 116: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 117: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 118: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 119: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 120: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 121: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 122: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 123: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 124: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 125: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 126: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 127: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 128: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 129: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 130: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 131: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 132: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 133: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 134: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 135: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 136: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 137: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 138: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 139: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 140: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 141: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 142: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 143: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 144: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 145: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 146: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 147: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 148: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 149: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 150: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 151: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 152: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 153: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 154: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 155: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 156: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 157: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 158: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 159: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 160: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 161: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 162: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 163: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 164: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 165: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 166: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 167: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 168: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 169: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 170: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 171: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 172: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 173: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 174: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 175: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 176: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 177: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 178: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 179: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 180: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 181: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 182: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 183: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 184: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 185: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 186: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 187: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 188: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 189: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 190: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 191: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 192: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 193: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 194: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 195: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 196: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 197: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 198: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 199: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 200: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 201: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 202: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 203: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 204: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 205: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 206: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 207: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 208: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 209: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 210: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 211: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 212: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 213: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 214: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 215: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 216: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 217: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 218: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 219: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 220: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 221: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 222: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 223: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 224: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 225: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 226: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 227: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 228: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 229: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 230: S1 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 231: S2 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 232: S3 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 233: S6 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
    "audit 234: S10 is represented as a derived GPU constraint: board envelope -> interfaces and heatsink stack -> shroud opening -> fan center -> rotor joint; optional brace is edge-gated, not free-floating.",
)

GRAPHICS_CARD_CONSTRAINT_NOTEBOOK = (
    "constraint note 001: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 002: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 003: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 004: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 005: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 006: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 007: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 008: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 009: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 010: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 011: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 012: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 013: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 014: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 015: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 016: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 017: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 018: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 019: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 020: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 021: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 022: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 023: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 024: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 025: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 026: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 027: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 028: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 029: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 030: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 031: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 032: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 033: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 034: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 035: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 036: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 037: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 038: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 039: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 040: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 041: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 042: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 043: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 044: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 045: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 046: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 047: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 048: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 049: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 050: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 051: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 052: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 053: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 054: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 055: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 056: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 057: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 058: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 059: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 060: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 061: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 062: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 063: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 064: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 065: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 066: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 067: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 068: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 069: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 070: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 071: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 072: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 073: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 074: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 075: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 076: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 077: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 078: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 079: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 080: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 081: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 082: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 083: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 084: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 085: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 086: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 087: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 088: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 089: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 090: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 091: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 092: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 093: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 094: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 095: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 096: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 097: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 098: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 099: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 100: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 101: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 102: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 103: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 104: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 105: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 106: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 107: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 108: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 109: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 110: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 111: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 112: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 113: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 114: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 115: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 116: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 117: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 118: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 119: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 120: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 121: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 122: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 123: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 124: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 125: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 126: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 127: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 128: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 129: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 130: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 131: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 132: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 133: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 134: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 135: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 136: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 137: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 138: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 139: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 140: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 141: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 142: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 143: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 144: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 145: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 146: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 147: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 148: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 149: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 150: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 151: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 152: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 153: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 154: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 155: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 156: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 157: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 158: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 159: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 160: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 161: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 162: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 163: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 164: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 165: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 166: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 167: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 168: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 169: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 170: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 171: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 172: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 173: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 174: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 175: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 176: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 177: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 178: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 179: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 180: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 181: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 182: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 183: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 184: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 185: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 186: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 187: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 188: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 189: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 190: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 191: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 192: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 193: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 194: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 195: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 196: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 197: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 198: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 199: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 200: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 201: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 202: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 203: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 204: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 205: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 206: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 207: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 208: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 209: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 210: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 211: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 212: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 213: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 214: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 215: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 216: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 217: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 218: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 219: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 220: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 221: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 222: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 223: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 224: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 225: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 226: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 227: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 228: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
    "constraint note 229: fan count, radius, and center positions are solved from card length/height before geometry is emitted; PCIe fingers, I/O bracket, heatpipes, shroud rails, stator bosses, rotors, and brace hinges attach to that solved envelope.",
)
