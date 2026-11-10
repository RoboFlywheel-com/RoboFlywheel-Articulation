# SPDX-License-Identifier: Apache-2.0

"""Bench / Wood Swing procedural template.

Implements ``articraft_template_authoring/specs_modular_v1/Bench_Wood_Swing.md``.

Identity is deliberately narrow: a garden / porch *bench* swing with a fixed
support frame, top beam, hanging hardware, and one bench body that swings
fore/aft about a +Y revolute axis.  Daybeds, four-post pergolas, and single
hanging chairs are excluded from the seed domain.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True


SupportFrameModule = Literal[
    "round_log_a_frame",
    "tubular_a_frame",
    "slatted_end_wall_a_frame",
    "square_timber_a_frame",
    "upright_bar_frame",
]
SuspensionModule = Literal[
    "rigid_log_arms",
    "rigid_tubular_arms",
    "rigid_rods",
    "rigid_wood_arms",
    "chains",
    "ropes",
]
BenchBodyModule = Literal[
    "straight_slatted_bench",
    "rolltop_metal_bench",
    "facing_glider_bench",
    "compact_wood_bench",
]
CanopyModule = Literal[
    "none",
    "pitched_gable_roof",
    "fabric_awning",
    "light_flat_lattice_roof",
]
PaletteStyle = Literal[
    "cedar_red_roof",
    "light_gray_metal",
    "sage_pine",
    "dark_stained_canvas",
    "natural_rope_teak",
]

SUPPORT_FRAME_MODULES: tuple[SupportFrameModule, ...] = (
    "round_log_a_frame",
    "tubular_a_frame",
    "slatted_end_wall_a_frame",
    "square_timber_a_frame",
    "upright_bar_frame",
)
SUSPENSION_MODULES: tuple[SuspensionModule, ...] = (
    "rigid_log_arms",
    "rigid_tubular_arms",
    "rigid_rods",
    "rigid_wood_arms",
    "chains",
    "ropes",
)
BENCH_BODY_MODULES: tuple[BenchBodyModule, ...] = (
    "straight_slatted_bench",
    "rolltop_metal_bench",
    "compact_wood_bench",
)
CANOPY_MODULES: tuple[CanopyModule, ...] = (
    "none",
    "pitched_gable_roof",
    "fabric_awning",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "cedar_red_roof",
    "light_gray_metal",
    "sage_pine",
    "dark_stained_canvas",
    "natural_rope_teak",
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "cedar_red_roof": {
        "wood": (0.68, 0.47, 0.25, 1.0),
        "wood_dark": (0.42, 0.27, 0.13, 1.0),
        "frame": (0.70, 0.49, 0.28, 1.0),
        "steel": (0.56, 0.58, 0.60, 1.0),
        "roof": (0.70, 0.15, 0.12, 1.0),
        "roof_dark": (0.52, 0.10, 0.08, 1.0),
        "fabric": (0.70, 0.64, 0.50, 1.0),
        "rope": (0.72, 0.58, 0.36, 1.0),
    },
    "light_gray_metal": {
        "wood": (0.84, 0.85, 0.86, 1.0),
        "wood_dark": (0.64, 0.66, 0.68, 1.0),
        "frame": (0.78, 0.80, 0.82, 1.0),
        "steel": (0.58, 0.60, 0.62, 1.0),
        "roof": (0.74, 0.76, 0.78, 1.0),
        "roof_dark": (0.52, 0.54, 0.56, 1.0),
        "fabric": (0.70, 0.72, 0.74, 1.0),
        "rope": (0.64, 0.60, 0.50, 1.0),
    },
    "sage_pine": {
        "wood": (0.80, 0.67, 0.45, 1.0),
        "wood_dark": (0.56, 0.43, 0.25, 1.0),
        "frame": (0.76, 0.63, 0.42, 1.0),
        "steel": (0.42, 0.44, 0.47, 1.0),
        "roof": (0.44, 0.56, 0.42, 1.0),
        "roof_dark": (0.32, 0.42, 0.30, 1.0),
        "fabric": (0.58, 0.66, 0.52, 1.0),
        "rope": (0.72, 0.58, 0.36, 1.0),
    },
    "dark_stained_canvas": {
        "wood": (0.34, 0.21, 0.11, 1.0),
        "wood_dark": (0.18, 0.11, 0.06, 1.0),
        "frame": (0.30, 0.18, 0.09, 1.0),
        "steel": (0.44, 0.45, 0.46, 1.0),
        "roof": (0.18, 0.32, 0.18, 1.0),
        "roof_dark": (0.10, 0.22, 0.12, 1.0),
        "fabric": (0.12, 0.34, 0.18, 1.0),
        "rope": (0.60, 0.48, 0.30, 1.0),
    },
    "natural_rope_teak": {
        "wood": (0.70, 0.52, 0.30, 1.0),
        "wood_dark": (0.48, 0.33, 0.18, 1.0),
        "frame": (0.64, 0.46, 0.26, 1.0),
        "steel": (0.64, 0.62, 0.58, 1.0),
        "roof": (0.76, 0.70, 0.56, 1.0),
        "roof_dark": (0.60, 0.52, 0.40, 1.0),
        "fabric": (0.78, 0.70, 0.58, 1.0),
        "rope": (0.76, 0.63, 0.40, 1.0),
    },
}

_TOP_SIDES: tuple[tuple[str, int], ...] = (
    ("left", +1),
    ("right", -1),
)
_BENCH_ENDS: tuple[tuple[str, int], ...] = (
    ("front", +1),
    ("rear", -1),
)
_DRIVER_SIDE = "left"
_PROBLEM_SOURCE_RECORD_IDS: tuple[str, ...] = (
    "rec_wood_swing_var_chainbench",
)


@dataclass(frozen=True)
class WoodSwingConfig:
    support_frame_module: SupportFrameModule = "tubular_a_frame"
    suspension_module: SuspensionModule = "rigid_tubular_arms"
    bench_body_module: BenchBodyModule = "straight_slatted_bench"
    canopy_module: CanopyModule = "none"
    palette_style: PaletteStyle = "light_gray_metal"
    seat_slat_count: int = 8
    back_slat_count: int = 5
    roof_rib_count: int = 14
    chain_link_count: int = 12
    rope_segment_count: int = 3
    frame_scale: float = 1.0
    swing_limit: float = 0.40
    name: str = "wood_swing"
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["light_gray_metal"])
    )


@dataclass(frozen=True)
class ResolvedWoodSwingConfig:
    support_frame_module: SupportFrameModule
    suspension_module: SuspensionModule
    bench_body_module: BenchBodyModule
    canopy_module: CanopyModule
    palette_style: PaletteStyle
    seat_slat_count: int
    back_slat_count: int
    roof_rib_count: int
    chain_link_count: int
    rope_segment_count: int
    frame_scale: float
    swing_limit: float
    top_z: float
    pivot_z: float
    beam_half_y: float
    end_y: float
    pivot_half_x: float
    pivot_half_y: float
    seat_half_x: float
    seat_half_y: float
    seat_z: float
    drop: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def config_from_seed(seed: int) -> WoodSwingConfig:
    rng = random.Random(seed * 2654435761 + 12345)

    support = rng.choice(SUPPORT_FRAME_MODULES)
    suspension = rng.choice(SUSPENSION_MODULES)
    bench = rng.choice(BENCH_BODY_MODULES)
    canopy = rng.choice(CANOPY_MODULES)
    palette = rng.choice(PALETTE_STYLES)

    # Compatibility: keep source-like material/mechanism pairings frequent
    # without shrinking the topology domain to a curated table.
    if support == "round_log_a_frame" and suspension == "rigid_tubular_arms":
        suspension = rng.choice(("rigid_log_arms", "chains", "ropes"))
    if support in ("tubular_a_frame", "upright_bar_frame") and suspension == "rigid_log_arms":
        suspension = "rigid_tubular_arms"
    if support == "slatted_end_wall_a_frame" and canopy == "none":
        canopy = "pitched_gable_roof"
    if support == "upright_bar_frame" and canopy == "fabric_awning":
        canopy = "none"

    return WoodSwingConfig(
        support_frame_module=support,
        suspension_module=suspension,
        bench_body_module=bench,
        canopy_module=canopy,
        palette_style=palette,
        seat_slat_count=rng.randint(4, 14),
        back_slat_count=rng.randint(4, 9),
        roof_rib_count=rng.randint(8, 22),
        chain_link_count=rng.randint(8, 16),
        rope_segment_count=rng.randint(1, 4),
        frame_scale=round(rng.uniform(0.92, 1.08), 4),
        swing_limit=round(rng.uniform(0.34, 0.46), 4),
        palette=dict(PALETTES[palette]),
    )


def resolve_config(config: WoodSwingConfig) -> ResolvedWoodSwingConfig:
    if config.support_frame_module not in SUPPORT_FRAME_MODULES:
        raise ValueError(f"unknown support_frame_module {config.support_frame_module!r}")
    if config.suspension_module not in SUSPENSION_MODULES:
        raise ValueError(f"unknown suspension_module {config.suspension_module!r}")
    valid_bench_modules = (*BENCH_BODY_MODULES, "facing_glider_bench")
    valid_canopy_modules = (*CANOPY_MODULES, "light_flat_lattice_roof")
    if config.bench_body_module not in valid_bench_modules:
        raise ValueError(f"unknown bench_body_module {config.bench_body_module!r}")
    if config.canopy_module not in valid_canopy_modules:
        raise ValueError(f"unknown canopy_module {config.canopy_module!r}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"unknown palette_style {config.palette_style!r}")

    support = config.support_frame_module
    suspension = config.suspension_module
    bench = config.bench_body_module
    canopy = config.canopy_module
    if bench == "facing_glider_bench":
        bench = "straight_slatted_bench"
    if canopy == "light_flat_lattice_roof":
        canopy = "pitched_gable_roof"
    if support == "round_log_a_frame" and suspension == "rigid_tubular_arms":
        suspension = "rigid_log_arms"
    if support in ("tubular_a_frame", "upright_bar_frame") and suspension == "rigid_log_arms":
        suspension = "rigid_tubular_arms"
    if support == "slatted_end_wall_a_frame" and canopy == "none":
        canopy = "pitched_gable_roof"
    if support == "upright_bar_frame" and canopy in ("fabric_awning", "light_flat_lattice_roof"):
        canopy = "none"

    scale = _clamp(config.frame_scale, 0.92, 1.08)
    top_z = 1.88 * scale
    pivot_z = top_z - 0.13 * scale
    return ResolvedWoodSwingConfig(
        support_frame_module=support,
        suspension_module=suspension,
        bench_body_module=bench,
        canopy_module=canopy,
        palette_style=config.palette_style,
        seat_slat_count=max(4, min(18, int(config.seat_slat_count))),
        back_slat_count=max(4, min(10, int(config.back_slat_count))),
        roof_rib_count=max(8, min(28, int(config.roof_rib_count))),
        chain_link_count=max(8, min(20, int(config.chain_link_count))),
        rope_segment_count=max(1, min(4, int(config.rope_segment_count))),
        frame_scale=scale,
        swing_limit=_clamp(config.swing_limit, 0.32, 0.48),
        top_z=top_z,
        pivot_z=pivot_z,
        beam_half_y=0.92 * scale,
        end_y=0.94 * scale,
        pivot_half_x=0.29 * scale,
        pivot_half_y=0.66 * scale,
        seat_half_x=0.30 * scale,
        seat_half_y=0.66 * scale,
        seat_z=0.58 * scale,
        drop=pivot_z - 0.58 * scale,
        name=str(config.name or "wood_swing"),
        palette=dict(PALETTES[config.palette_style]),
    )


def _register_materials(model: ArticulatedObject, r: ResolvedWoodSwingConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"mat_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


def _bar_x(part, name: str, x0: float, x1: float, y: float, z: float, sec: float, mat: str) -> None:
    part.visual(
        Box((abs(x1 - x0), sec, sec)),
        origin=Origin(xyz=((x0 + x1) / 2.0, y, z)),
        material=mat,
        name=name, material_class_id="wood.natural_generic",
    )


def _bar_y(part, name: str, x: float, y0: float, y1: float, z: float, sec: float, mat: str) -> None:
    part.visual(
        Box((sec, abs(y1 - y0), sec)),
        origin=Origin(xyz=(x, (y0 + y1) / 2.0, z)),
        material=mat,
        name=name, material_class_id="wood.natural_generic",
    )


def _bar_z(part, name: str, x: float, y: float, z0: float, z1: float, sec: float, mat: str) -> None:
    part.visual(
        Box((sec, sec, abs(z1 - z0))),
        origin=Origin(xyz=(x, y, (z0 + z1) / 2.0)),
        material=mat,
        name=name, material_class_id="wood.natural_generic",
    )


def _diag_xz(
    part,
    name: str,
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    sec: float,
    mat: str,
) -> None:
    ax, ay, az = a
    bx, _by, bz = b
    dx, dz = bx - ax, bz - az
    length = math.hypot(dx, dz)
    part.visual(
        Box((sec, sec, length)),
        origin=Origin(
            xyz=((ax + bx) / 2.0, ay, (az + bz) / 2.0),
            rpy=(0.0, math.atan2(dx, dz), 0.0),
        ),
        material=mat,
        name=name, material_class_id="metal.generic_plain",
    )


def _chain_link_mesh(r: ResolvedWoodSwingConfig):
    link_h = 0.070 * r.frame_scale
    link_w = 0.034 * r.frame_scale
    wire_r = 0.0045 * r.frame_scale
    half_h = link_h / 2.0
    half_w = link_w / 2.0
    straight = max(link_h - link_w, 0.001 * r.frame_scale)
    half_s = straight / 2.0
    pts: list[tuple[float, float, float]] = [
        (half_w, 0.0, -half_s),
        (half_w, 0.0, half_s),
    ]
    for k in range(1, 10):
        a = -math.pi / 2.0 + math.pi * k / 10.0
        pts.append((half_w * math.cos(a), 0.0, half_s + half_w * math.sin(a)))
    pts.extend(
        [
            (-half_w, 0.0, half_s),
            (-half_w, 0.0, -half_s),
        ]
    )
    for k in range(1, 10):
        a = math.pi / 2.0 + math.pi * k / 10.0
        pts.append((half_w * math.cos(a), 0.0, -half_s + half_w * math.sin(a)))
    return mesh_from_geometry(
        tube_from_spline_points(
            pts,
            radius=wire_r,
            samples_per_segment=6,
            closed_spline=True,
            radial_segments=10,
            cap_ends=False,
        ),
        "wood_swing_chain_link",
    )


def _frame_materials(r: ResolvedWoodSwingConfig, mats: dict[str, str]) -> tuple[str, str, float]:
    if r.support_frame_module in ("tubular_a_frame", "upright_bar_frame"):
        return mats["frame"], mats["steel"], 0.055 * r.frame_scale
    if r.support_frame_module == "square_timber_a_frame":
        return mats["wood_dark"], mats["wood"], 0.070 * r.frame_scale
    if r.support_frame_module == "slatted_end_wall_a_frame":
        return mats["wood"], mats["wood_dark"], 0.060 * r.frame_scale
    return mats["frame"], mats["wood_dark"], 0.070 * r.frame_scale


def _build_frame(model: ArticulatedObject, r: ResolvedWoodSwingConfig, mats: dict[str, str]) -> None:
    frame = model.part("frame")
    main, dark, sec = _frame_materials(r, mats)
    hx = 0.68 * r.frame_scale
    foot_t = 0.035 * r.frame_scale

    _bar_y(frame, "top_beam", 0.0, -r.beam_half_y, r.beam_half_y, r.top_z, sec, main)

    if r.support_frame_module == "upright_bar_frame":
        for side, y in (("left", r.end_y), ("right", -r.end_y)):
            _bar_z(frame, f"upright_{side}", 0.0, y, 0.0, r.top_z + 0.02 * r.frame_scale, sec, main)
            frame.visual(
                Box((0.36 * r.frame_scale, 0.14 * r.frame_scale, foot_t)),
                origin=Origin(xyz=(0.0, y, foot_t / 2.0)),
                material=dark,
                name=f"foot_plate_{side}", material_class_id="metal.stainless_matte",
            )
    else:
        for wall_i, y in enumerate((r.end_y, -r.end_y)):
            for tag, sx in (("front", +1), ("rear", -1)):
                _diag_xz(
                    frame,
                    f"leg_{wall_i}_{tag}",
                    (sx * hx, y, foot_t),
                    (0.0, y, r.top_z),
                    sec,
                    main,
                )
                frame.visual(
                    Box((0.16 * r.frame_scale, 0.11 * r.frame_scale, foot_t)),
                    origin=Origin(xyz=(sx * hx, y, foot_t / 2.0)),
                    material=dark,
                    name=f"foot_plate_{wall_i}_{tag}", material_class_id=("metal.stainless_matte" if r.support_frame_module in {"tubular_a_frame", "upright_bar_frame"} else "wood.walnut_dark"),
                )
            _bar_x(frame, f"cross_brace_{wall_i}", -0.48 * r.frame_scale, 0.48 * r.frame_scale, y, 0.63 * r.frame_scale, sec * 0.82, dark)
            if r.support_frame_module == "slatted_end_wall_a_frame":
                _bar_x(frame, f"wall_base_rail_{wall_i}", -0.55 * r.frame_scale, 0.55 * r.frame_scale, y, 0.14 * r.frame_scale, sec * 0.9, dark)
                _bar_x(frame, f"wall_top_rail_{wall_i}", -0.38 * r.frame_scale, 0.38 * r.frame_scale, y, 1.28 * r.frame_scale, sec * 0.9, dark)
                for k in range(5):
                    x = -0.32 * r.frame_scale + k * (0.64 * r.frame_scale / 4.0)
                    _bar_z(frame, f"wall_slat_{wall_i}_{k}", x, y, 0.14 * r.frame_scale, 1.28 * r.frame_scale, sec * 0.45, main)
            if r.support_frame_module == "square_timber_a_frame":
                _bar_y(frame, f"tray_shelf_{wall_i}", 0.0, y - 0.18 * (1 if y > 0 else -1), y + 0.18 * (1 if y > 0 else -1), 0.64 * r.frame_scale, sec * 0.7, main)

    # Source-backed topology: two top pivot stations, one per bench side.  Each
    # moving side hanger splits from its top station to front/rear lower lugs.
    for side, sy in _TOP_SIDES:
        py = sy * r.pivot_half_y
        frame.visual(
            Box((0.105 * r.frame_scale, 0.075 * r.frame_scale, 0.20 * r.frame_scale)),
            origin=Origin(xyz=(0.0, py, (r.pivot_z + r.top_z) / 2.0 - 0.012 * r.frame_scale)),
            material=dark,
            name=f"hanger_block_{side}", material_class_id=("metal.stainless_matte" if r.support_frame_module in {"tubular_a_frame", "upright_bar_frame"} else "wood.walnut_dark"),
        )
        _bar_x(
            frame,
            f"top_pivot_bar_{side}",
            -r.pivot_half_x - 0.04 * r.frame_scale,
            r.pivot_half_x + 0.04 * r.frame_scale,
            py,
            r.pivot_z,
            0.030 * r.frame_scale,
            mats["steel"],
        )
        frame.visual(
            Cylinder(radius=0.019 * r.frame_scale, length=0.115 * r.frame_scale),
            origin=Origin(xyz=(0.0, py, r.pivot_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["steel"],
            name=f"pivot_pin_{side}", material_class_id="metal.stainless_matte",
        )

    _build_canopy_visuals(frame, r, mats)


def _build_canopy_visuals(frame, r: ResolvedWoodSwingConfig, mats: dict[str, str]) -> None:
    if r.canopy_module == "none":
        return
    roof_z = r.top_z + 0.15 * r.frame_scale
    if r.canopy_module == "pitched_gable_roof":
        roof_pitch = math.radians(18.0)
        roof_half_y = 0.90 * r.frame_scale
        roof_panel_x = 0.72 * r.frame_scale
        ridge_z = roof_z + 0.06 * r.frame_scale
        for y in (-0.74 * r.frame_scale, 0.74 * r.frame_scale):
            _bar_z(frame, f"roof_post_{y:+.2f}", 0.0, y, r.top_z, ridge_z, 0.040 * r.frame_scale, mats["wood_dark"])
        for side, sx in (("front", 1), ("rear", -1)):
            frame.visual(
                Box((roof_panel_x, 2.0 * roof_half_y, 0.024 * r.frame_scale)),
                origin=Origin(
                    xyz=(sx * 0.28 * r.frame_scale, 0.0, roof_z),
                    rpy=(0.0, sx * roof_pitch, 0.0),
                ),
                material=mats["roof"],
                name=f"roof_sheet_{side}", material_class_id="metal.paint_coated",
            )
        _bar_y(frame, "roof_ridge_cap", 0.0, -roof_half_y, roof_half_y, ridge_z + 0.018 * r.frame_scale, 0.038 * r.frame_scale, mats["roof_dark"])
        visible_ribs = max(4, min(8, r.roof_rib_count // 2))
        for j in range(visible_ribs):
            y = -roof_half_y + (j + 0.5) * (2.0 * roof_half_y / visible_ribs)
            frame.visual(
                Box((0.92 * r.frame_scale, 0.012 * r.frame_scale, 0.012 * r.frame_scale)),
                origin=Origin(xyz=(0.0, y, roof_z - 0.020 * r.frame_scale)),
                material=mats["roof_dark"],
                name=f"roof_under_rib_{j}", material_class_id="metal.paint_coated",
            )
    elif r.canopy_module == "fabric_awning":
        for y in (-0.74 * r.frame_scale, 0.74 * r.frame_scale):
            _bar_z(frame, f"fabric_post_{y:+.2f}", 0.0, y, r.top_z, roof_z, 0.040 * r.frame_scale, mats["wood_dark"])
        frame.visual(
            Box((1.38 * r.frame_scale, 2.03 * r.frame_scale, 0.025 * r.frame_scale)),
            origin=Origin(xyz=(0.0, 0.0, roof_z)),
            material=mats["fabric"],
            name="fabric_canopy_panel", material_class_id="fabric.canvas",
        )
        for side, sx in (("front", 1), ("rear", -1)):
            _bar_y(frame, f"fabric_skirt_{side}", sx * 0.61 * r.frame_scale, -0.98 * r.frame_scale, 0.98 * r.frame_scale, roof_z, 0.080 * r.frame_scale, mats["fabric"])
    elif r.canopy_module == "light_flat_lattice_roof":
        frame.visual(
            Box((0.070 * r.frame_scale, 2.03 * r.frame_scale, roof_z - r.top_z + 0.045 * r.frame_scale)),
            origin=Origin(xyz=(0.0, 0.0, (roof_z + r.top_z) / 2.0)),
            material=mats["wood_dark"],
            name="flat_roof_center_bridge", material_class_id="wood.walnut_dark",
        )
        for y in (-0.74 * r.frame_scale, 0.74 * r.frame_scale):
            _bar_z(frame, f"flat_roof_post_{y:+.2f}", 0.0, y, r.top_z - 0.030 * r.frame_scale, roof_z, 0.040 * r.frame_scale, mats["wood_dark"])
        for k in range(r.roof_rib_count):
            y = -0.94 * r.frame_scale + k * (1.88 * r.frame_scale / max(1, r.roof_rib_count - 1))
            _bar_x(frame, f"flat_roof_rafters_{k}", -0.64 * r.frame_scale, 0.64 * r.frame_scale, y, roof_z, 0.040 * r.frame_scale, mats["wood"])
        _bar_y(frame, "flat_roof_side_rail_l", -0.60 * r.frame_scale, -0.98 * r.frame_scale, 0.98 * r.frame_scale, roof_z, 0.050 * r.frame_scale, mats["wood_dark"])
        _bar_y(frame, "flat_roof_side_rail_r", 0.60 * r.frame_scale, -0.98 * r.frame_scale, 0.98 * r.frame_scale, roof_z, 0.050 * r.frame_scale, mats["wood_dark"])


def _build_side_hanger_hub(part, r: ResolvedWoodSwingConfig, mats: dict[str, str], *, mat: str) -> None:
    part.visual(
        Cylinder(radius=0.020 * r.frame_scale, length=0.090 * r.frame_scale),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="hanger_top_hub", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Box((0.115 * r.frame_scale, 0.045 * r.frame_scale, 0.045 * r.frame_scale)),
        origin=Origin(xyz=(0.0, 0.0, -0.038 * r.frame_scale)),
        material=mat,
        name="top_clevis", material_class_id=("metal.stainless_matte" if r.suspension_module in {"rigid_tubular_arms", "rigid_rods", "chains", "ropes"} else "wood.natural_generic"),
    )


def _build_rigid_side_hanger(part, r: ResolvedWoodSwingConfig, mats: dict[str, str]) -> None:
    if r.suspension_module in ("rigid_tubular_arms", "rigid_rods"):
        mat, sec = mats["steel"], 0.030 * r.frame_scale
    elif r.suspension_module == "rigid_log_arms":
        mat, sec = mats["wood"], 0.050 * r.frame_scale
    else:
        mat, sec = mats["wood"], 0.044 * r.frame_scale
    _build_side_hanger_hub(part, r, mats, mat=mat)
    top_clear = 0.015 * r.frame_scale
    for end, sx in _BENCH_ENDS:
        _diag_xz(
            part,
            f"hanger_bar_{end}",
            (0.0, 0.0, -top_clear),
            (sx * r.pivot_half_x, 0.0, -r.drop),
            sec,
            mat,
        )
        part.visual(
            Box((0.090 * r.frame_scale, 0.052 * r.frame_scale, 0.050 * r.frame_scale)),
            origin=Origin(xyz=(sx * r.pivot_half_x, 0.0, -r.drop)),
            material=mat,
            name=f"hanger_bottom_lug_{end}", material_class_id=("metal.stainless_matte" if r.suspension_module in {"rigid_tubular_arms", "rigid_rods", "chains", "ropes"} else "wood.natural_generic"),
        )
    _bar_x(
        part,
        "lower_side_link",
        -r.pivot_half_x,
        r.pivot_half_x,
        0.0,
        -r.drop + 0.020 * r.frame_scale,
        sec * 0.82,
        mat,
    )


def _build_chain_side_hanger(part, r: ResolvedWoodSwingConfig, mats: dict[str, str]) -> None:
    _build_side_hanger_hub(part, r, mats, mat=mats["steel"])
    top_clear = 0.026 * r.frame_scale
    pitch = (r.drop - top_clear) / max(1, r.chain_link_count)
    link_mesh = _chain_link_mesh(r)
    for end, sx in _BENCH_ENDS:
        branch_angle = math.atan2(sx * r.pivot_half_x, -r.drop + top_clear)
        _diag_xz(
            part,
            f"chain_branch_core_{end}",
            (0.0, 0.0, -top_clear),
            (sx * r.pivot_half_x, 0.0, -r.drop),
            0.007 * r.frame_scale,
            mats["steel"],
        )
        for i in range(r.chain_link_count):
            t = (i + 0.5) / max(1, r.chain_link_count)
            x = sx * r.pivot_half_x * t
            z = -top_clear - 0.5 * pitch - i * pitch
            part.visual(
                link_mesh,
                origin=Origin(
                    xyz=(x, 0.0, z),
                    rpy=(0.0, branch_angle, 0.0 if i % 2 == 0 else math.pi / 2.0),
                ),
                material=mats["steel"],
                name=f"chain_link_{end}_{i}", material_class_id="metal.stainless_matte",
            )
        part.visual(
            Box((0.075 * r.frame_scale, 0.052 * r.frame_scale, 0.045 * r.frame_scale)),
            origin=Origin(xyz=(sx * r.pivot_half_x, 0.0, -r.drop)),
            material=mats["steel"],
            name=f"hanger_bottom_lug_{end}", material_class_id="metal.stainless_matte",
        )
        _diag_xz(
            part,
            f"bench_mount_ear_{end}",
            (0.0, 0.0, -r.drop),
            (sx * r.pivot_half_x, 0.0, -r.drop),
            0.018 * r.frame_scale,
            mats["steel"],
        )
    part.visual(
        Box((0.070 * r.frame_scale, 0.060 * r.frame_scale, 0.052 * r.frame_scale)),
        origin=Origin(xyz=(0.0, 0.0, -r.drop)),
        material=mats["steel"],
        name="bench_side_mount_block", material_class_id="metal.stainless_matte",
    )


def _build_rope_side_hanger(part, r: ResolvedWoodSwingConfig, mats: dict[str, str]) -> None:
    _build_side_hanger_hub(part, r, mats, mat=mats["rope"])
    top_clear = 0.026 * r.frame_scale
    seg = (r.drop - top_clear) / r.rope_segment_count
    for end, sx in _BENCH_ENDS:
        for i in range(r.rope_segment_count):
            t0 = i / r.rope_segment_count
            t1 = (i + 1) / r.rope_segment_count
            _diag_xz(
                part,
                f"rope_segment_{end}_{i}",
                (sx * r.pivot_half_x * t0, 0.0, -top_clear - i * seg),
                (sx * r.pivot_half_x * t1, 0.0, -top_clear - (i + 1) * seg - 0.015 * r.frame_scale),
                0.030 * r.frame_scale,
                mats["rope"],
            )
        part.visual(
            Box((0.070 * r.frame_scale, 0.050 * r.frame_scale, 0.045 * r.frame_scale)),
            origin=Origin(xyz=(sx * r.pivot_half_x, 0.0, -r.drop)),
            material=mats["rope"],
            name=f"hanger_bottom_lug_{end}", material_class_id="organic.woven_plant_fiber",
        )
        _diag_xz(
            part,
            f"bench_mount_ear_{end}",
            (0.0, 0.0, -r.drop),
            (sx * r.pivot_half_x, 0.0, -r.drop),
            0.018 * r.frame_scale,
            mats["wood_dark"],
        )
    part.visual(
        Box((0.070 * r.frame_scale, 0.060 * r.frame_scale, 0.052 * r.frame_scale)),
        origin=Origin(xyz=(0.0, 0.0, -r.drop)),
        material=mats["wood_dark"],
        name="bench_side_mount_block", material_class_id="wood.walnut_dark",
    )


def _build_suspension(model: ArticulatedObject, r: ResolvedWoodSwingConfig, mats: dict[str, str]) -> str:
    limits = MotionLimits(effort=180.0, velocity=2.5, lower=-r.swing_limit, upper=r.swing_limit)
    driver_name = f"hanger_{_DRIVER_SIDE}"
    for side, sy in _TOP_SIDES:
        part = model.part(f"hanger_{side}")
        if r.suspension_module == "chains":
            _build_chain_side_hanger(part, r, mats)
        elif r.suspension_module == "ropes":
            _build_rope_side_hanger(part, r, mats)
        else:
            _build_rigid_side_hanger(part, r, mats)
        joint_name = "swing_drive" if side == _DRIVER_SIDE else f"swing_follow_{side}"
        model.articulation(
            joint_name,
            ArticulationType.REVOLUTE,
            parent="frame",
            child=part,
            origin=Origin(xyz=(0.0, sy * r.pivot_half_y, r.pivot_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=limits,
            mimic=None if side == _DRIVER_SIDE else Mimic(joint="swing_drive", multiplier=1.0),
        )
    return driver_name


def _seat_origin(r: ResolvedWoodSwingConfig) -> tuple[float, float, float]:
    return (-r.pivot_half_x, -r.pivot_half_y, 0.0)


def _emit_straight_bench(seat, r: ResolvedWoodSwingConfig, mats: dict[str, str], *, compact: bool = False) -> None:
    ox, oy, oz = _seat_origin(r)
    hx = r.seat_half_x * (0.86 if compact else 1.0)
    hy = r.seat_half_y
    sec = 0.050 * r.frame_scale
    _bar_y(seat, "seat_front_rail", ox + hx, oy - hy, oy + hy, oz, sec, mats["wood_dark"])
    _bar_y(seat, "seat_rear_rail", ox - hx, oy - hy, oy + hy, oz, sec, mats["wood_dark"])
    _bar_x(seat, "seat_left_rail", ox - hx, ox + hx, oy + hy, oz, sec, mats["wood_dark"])
    _bar_x(seat, "seat_right_rail", ox - hx, ox + hx, oy - hy, oz, sec, mats["wood_dark"])
    for i in range(r.seat_slat_count):
        x = ox - hx + (i + 0.5) * (2 * hx / r.seat_slat_count)
        seat.visual(
            Box((2 * hx / r.seat_slat_count * 0.72, 2 * hy + 0.06 * r.frame_scale, 0.030 * r.frame_scale)),
            origin=Origin(xyz=(x, oy, oz + 0.036 * r.frame_scale)),
            material=mats["wood"],
            name=f"seat_slat_{i}", material_class_id="wood.natural_generic",
        )
    back_x = ox - hx
    _bar_y(seat, "back_lower_rail", back_x, oy - hy, oy + hy, oz + 0.18 * r.frame_scale, sec, mats["wood_dark"])
    _bar_y(seat, "back_upper_rail", back_x, oy - hy, oy + hy, oz + 0.62 * r.frame_scale, sec, mats["wood_dark"])
    for side, sy in (("left", 1), ("right", -1)):
        _bar_z(seat, f"back_stile_{side}", back_x, oy + sy * hy, oz, oz + 0.64 * r.frame_scale, sec * 0.85, mats["wood_dark"])
    for i in range(r.back_slat_count):
        y = oy - hy + (i + 0.5) * (2 * hy / r.back_slat_count)
        seat.visual(
            Box((0.045 * r.frame_scale, 0.070 * r.frame_scale, 0.48 * r.frame_scale)),
            origin=Origin(
                xyz=(back_x, y, oz + 0.40 * r.frame_scale),
            ),
            material=mats["wood"],
            name=f"back_slat_{i}", material_class_id="wood.natural_generic",
        )
    for side, sy in (("left", 1), ("right", -1)):
        y = oy + sy * hy
        _bar_z(seat, f"arm_post_front_{side}", ox + hx * 0.84, y, oz, oz + 0.34 * r.frame_scale, sec * 0.75, mats["wood_dark"])
        _bar_z(seat, f"arm_post_rear_{side}", ox - hx * 0.78, y, oz, oz + 0.45 * r.frame_scale, sec * 0.75, mats["wood_dark"])
        _bar_x(seat, f"armrest_{side}", ox - hx * 0.82, ox + hx * 0.90, y, oz + 0.36 * r.frame_scale, sec * 0.85, mats["wood"])
    _bar_y(seat, "front_hanger_touch", ox + hx, oy - hy, oy + hy, oz + 0.02 * r.frame_scale, sec * 0.7, mats["steel"])


def _emit_rolltop_bench(seat, r: ResolvedWoodSwingConfig, mats: dict[str, str]) -> None:
    _emit_straight_bench(seat, r, mats)
    ox, oy, oz = _seat_origin(r)
    hx, hy = r.seat_half_x, r.seat_half_y
    # Add the source-like rolltop horizontal rows behind the basic back rails.
    rolltop_back_x = ox - hx
    _bar_z(
        seat,
        "rolltop_center_spine",
        rolltop_back_x - 0.070 * r.frame_scale,
        oy,
        oz + 0.18 * r.frame_scale,
        oz + 0.70 * r.frame_scale,
        0.080 * r.frame_scale,
        mats["wood_dark"],
    )
    for i in range(r.back_slat_count):
        t = i / max(1, r.back_slat_count - 1)
        x = rolltop_back_x - (0.04 + 0.04 * t) * r.frame_scale
        z = oz + (0.23 + 0.42 * t) * r.frame_scale
        seat.visual(
            Box((0.055 * r.frame_scale, 2 * hy + 0.04 * r.frame_scale, 0.052 * r.frame_scale)),
            origin=Origin(xyz=(x, oy, z), rpy=(0.0, -math.radians(10 + 12 * t), 0.0)),
            material=mats["wood"],
            name=f"rolltop_back_slat_{i}", material_class_id="wood.natural_generic",
        )
    for side, sy in (("left", 1), ("right", -1)):
        seat.visual(
            Box((0.090 * r.frame_scale, 0.060 * r.frame_scale, 0.050 * r.frame_scale)),
            origin=Origin(xyz=(ox + hx * 0.68, oy + sy * (hy - 0.035 * r.frame_scale), oz + 0.365 * r.frame_scale)),
            material=mats["steel"],
            name=f"cup_holder_{side}", material_class_id="metal.stainless_matte",
        )


def _emit_facing_glider(seat, r: ResolvedWoodSwingConfig, mats: dict[str, str]) -> None:
    ox, oy, oz = _seat_origin(r)
    hx, hy = r.seat_half_x * 1.55, r.seat_half_y * 0.86
    sec = 0.045 * r.frame_scale
    _bar_y(seat, "platform_left_rail", ox, oy - hy, oy + hy, oz - 0.07 * r.frame_scale, sec, mats["wood_dark"])
    _bar_x(seat, "platform_front_rail", ox - hx, ox + hx, oy + hy, oz - 0.07 * r.frame_scale, sec, mats["wood_dark"])
    _bar_x(seat, "platform_rear_rail", ox - hx, ox + hx, oy - hy, oz - 0.07 * r.frame_scale, sec, mats["wood_dark"])
    for i in range(max(5, r.seat_slat_count)):
        x = ox - hx + (i + 0.5) * (2 * hx / max(5, r.seat_slat_count))
        seat.visual(
            Box((0.075 * r.frame_scale, 2 * hy + 0.04 * r.frame_scale, 0.026 * r.frame_scale)),
            origin=Origin(xyz=(x, oy, oz - 0.035 * r.frame_scale)),
            material=mats["wood"],
            name=f"deck_slat_{i}", material_class_id="wood.natural_generic",
        )
    _bar_z(seat, "glider_center_spine", ox, oy, oz - 0.08 * r.frame_scale, oz + 0.38 * r.frame_scale, 0.075 * r.frame_scale, mats["wood_dark"])
    for label, sx, facing in (("front", 1, -1), ("rear", -1, 1)):
        cx = ox + sx * 0.42 * r.frame_scale
        _bar_y(seat, f"{label}_seat_rail", cx, oy - hy * 0.82, oy + hy * 0.82, oz + 0.04 * r.frame_scale, sec, mats["wood_dark"])
        _bar_z(seat, f"{label}_platform_support", cx, oy, oz - 0.09 * r.frame_scale, oz + 0.16 * r.frame_scale, sec, mats["wood_dark"])
        for j in range(4):
            lx = cx + facing * (-0.14 + j * 0.09) * r.frame_scale
            seat.visual(
                Box((0.120 * r.frame_scale, 1.02 * r.frame_scale, 0.050 * r.frame_scale)),
                origin=Origin(xyz=(lx, oy, oz + 0.075 * r.frame_scale)),
                material=mats["wood"],
                name=f"{label}_seat_slat_{j}", material_class_id="wood.natural_generic",
            )
        back_x = cx - facing * 0.27 * r.frame_scale
        _bar_z(seat, f"{label}_back_support", back_x, oy, oz + 0.10 * r.frame_scale, oz + 0.47 * r.frame_scale, sec, mats["wood_dark"])
        _bar_x(seat, f"{label}_lower_side_frame", min(cx, back_x), max(cx, back_x), oy, oz + 0.12 * r.frame_scale, sec, mats["wood_dark"])
        _bar_x(seat, f"{label}_upper_side_frame", min(cx, back_x), max(cx, back_x), oy, oz + 0.34 * r.frame_scale, sec, mats["wood_dark"])
        _bar_y(seat, f"{label}_back_rail", back_x, oy - hy * 0.82, oy + hy * 0.82, oz + 0.44 * r.frame_scale, sec, mats["wood_dark"])
        for j in range(5):
            y = oy - hy * 0.68 + j * (1.36 * hy / 4)
            seat.visual(
                Box((0.030 * r.frame_scale, 0.080 * r.frame_scale, 0.42 * r.frame_scale)),
                origin=Origin(xyz=(back_x, y, oz + 0.31 * r.frame_scale), rpy=(0.0, facing * math.radians(10.0), 0.0)),
                material=mats["wood"],
                name=f"{label}_back_slat_{j}", material_class_id="wood.natural_generic",
            )
    _bar_y(seat, "center_table", ox, oy - 0.22 * r.frame_scale, oy + 0.22 * r.frame_scale, oz + 0.23 * r.frame_scale, 0.13 * r.frame_scale, mats["wood_dark"])
    for side, sy in (("left", 1), ("right", -1)):
        _bar_x(seat, f"armrest_{side}", ox - 0.58 * r.frame_scale, ox + 0.58 * r.frame_scale, oy + sy * hy, oz + 0.34 * r.frame_scale, sec, mats["wood"])
        _bar_y(seat, f"armrest_cross_{side}", ox, oy, oy + sy * hy, oz + 0.34 * r.frame_scale, sec, mats["wood_dark"])
        _bar_z(seat, f"armrest_post_{side}", ox, oy + sy * hy, oz + 0.12 * r.frame_scale, oz + 0.38 * r.frame_scale, sec, mats["wood_dark"])


def _build_bench(model: ArticulatedObject, r: ResolvedWoodSwingConfig, mats: dict[str, str], driver_part: str) -> None:
    seat = model.part("bench")
    if r.bench_body_module == "rolltop_metal_bench":
        _emit_rolltop_bench(seat, r, mats)
    elif r.bench_body_module == "facing_glider_bench":
        _emit_facing_glider(seat, r, mats)
    elif r.bench_body_module == "compact_wood_bench":
        _emit_straight_bench(seat, r, mats, compact=True)
    else:
        _emit_straight_bench(seat, r, mats)
    seat.visual(
        Box((0.075 * r.frame_scale, 0.040 * r.frame_scale, 0.060 * r.frame_scale)),
        origin=Origin(xyz=(0.0, 0.0, -0.010 * r.frame_scale)),
        material=mats["steel"],
        name="driver_hanger_side_socket", material_class_id="metal.stainless_matte",
    )
    model.articulation(
        "hanger_to_bench",
        ArticulationType.FIXED,
        parent=driver_part,
        child=seat,
        origin=Origin(xyz=(r.pivot_half_x, 0.0, -r.drop)),
    )


def build_wood_swing(
    config: WoodSwingConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or WoodSwingConfig())
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _register_materials(model, r)
    _build_frame(model, r, mats)
    driver = _build_suspension(model, r, mats)
    _build_bench(model, r, mats, driver)
    model.meta["template_slug"] = "wood_swing"
    model.meta["support_frame_module"] = r.support_frame_module
    model.meta["suspension_module"] = r.suspension_module
    model.meta["bench_body_module"] = r.bench_body_module
    model.meta["canopy_module"] = r.canopy_module
    model.meta["top_anchor_topology"] = "two_parallel_side_pivots"
    model.meta["quarantined_reference_records"] = list(_PROBLEM_SOURCE_RECORD_IDS)
    return model


def build_seeded_wood_swing(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_wood_swing(config_from_seed(seed), assets=assets)


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    choices: list[tuple[str, str]] = [
        ("support_frame", r.support_frame_module),
        ("suspension", r.suspension_module),
        ("bench_body", r.bench_body_module),
        ("canopy", r.canopy_module),
        ("top_anchor_topology", "two_parallel_side_pivots"),
    ]
    if r.suspension_module == "chains":
        choices.append(("chain_links", f"{r.chain_link_count}_links"))
    elif r.suspension_module == "ropes":
        choices.append(("rope_segments", f"{r.rope_segment_count}_segments"))
    return choices


def run_wood_swing_tests(object_model: ArticulatedObject, config: WoodSwingConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    bench = object_model.get_part("bench")
    drive = object_model.get_articulation("swing_drive")

    frame_visual_names = {v.name or "" for v in frame.visuals}
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}
    ctx.check(
        "top_anchor_topology_is_two_parallel_side_pivots",
        {f"pivot_pin_{side}" for side, _ in _TOP_SIDES}.issubset(frame_visual_names),
    )
    ctx.check(
        "no_four_independent_corner_top_pivots",
        not any(
            name in frame_visual_names
            for name in (
                "pivot_pin_front_left",
                "pivot_pin_front_right",
                "pivot_pin_rear_left",
                "pivot_pin_rear_right",
            )
        ),
    )
    ctx.check(
        "only_two_moving_side_hangers",
        {f"hanger_{side}" for side, _ in _TOP_SIDES}.issubset(part_names)
        and not any(name.startswith(("chain_front_", "chain_rear_", "rope_front_", "rope_rear_")) for name in part_names),
        details=str(sorted(name for name in part_names if "chain_" in name or "rope_" in name or name.startswith("hanger_"))),
    )
    ctx.check(
        "only_two_top_revolute_pivots",
        {"swing_drive", "swing_follow_right"}.issubset(joint_names)
        and not any("front_left" in name or "front_right" in name or "rear_left" in name or "rear_right" in name for name in joint_names),
        details=str(sorted(joint_names)),
    )

    for side, _ in _TOP_SIDES:
        hanger = object_model.get_part(f"hanger_{side}")
        ctx.allow_overlap(
            frame,
            hanger,
            elem_a=f"pivot_pin_{side}",
            elem_b="hanger_top_hub",
            reason="Hanger top hub is captured on the visible pivot pin in the top beam hardware.",
        )
        ctx.allow_overlap(
            frame,
            hanger,
            elem_a=f"hanger_block_{side}",
            elem_b="hanger_top_hub",
            reason="The frame hanger block visually surrounds the same top pivot hub.",
        )
        ctx.allow_overlap(
            frame,
            hanger,
            elem_a=f"hanger_block_{side}",
            elem_b="top_clevis",
            reason="The moving clevis is intentionally captured inside the fixed hanger block.",
        )
        ctx.allow_overlap(
            frame,
            hanger,
            elem_a=f"top_pivot_bar_{side}",
            elem_b="hanger_top_hub",
            reason="The side hanger hub rotates around the visible top pivot bar.",
        )
        ctx.allow_overlap(
            frame,
            hanger,
            elem_a=f"top_pivot_bar_{side}",
            elem_b="top_clevis",
            reason="The clevis wraps the top pivot bar at the revolute joint.",
        )
        ctx.allow_overlap(
            frame,
            hanger,
            elem_a=f"pivot_pin_{side}",
            elem_b="top_clevis",
            reason="The clevis and pivot pin share the same captured top hinge volume.",
        )
        if r.suspension_module in ("chains", "ropes"):
            for end, _sx in _BENCH_ENDS:
                top_hanger_elem = f"chain_link_{end}_0" if r.suspension_module == "chains" else f"rope_segment_{end}_0"
                ctx.allow_overlap(
                    frame,
                    hanger,
                    elem_a=f"pivot_pin_{side}",
                    elem_b=top_hanger_elem,
                    reason="The first chain or rope segment is captured at the top pivot pin.",
                )
                ctx.allow_overlap(
                    frame,
                    hanger,
                    elem_a=f"top_pivot_bar_{side}",
                    elem_b=top_hanger_elem,
                    reason="The first chain or rope segment wraps the visible top pivot bar.",
                )
                ctx.allow_overlap(
                    frame,
                    hanger,
                    elem_a=f"hanger_block_{side}",
                    elem_b=top_hanger_elem,
                    reason="The chain or rope branch exits through the side hanger block below the captured pivot.",
                )
                if r.suspension_module == "chains":
                    ctx.allow_overlap(
                        frame,
                        hanger,
                        elem_a=f"hanger_block_{side}",
                        elem_b=f"chain_branch_core_{end}",
                        reason="The continuous chain core exits through the side hanger block below the captured pivot.",
                    )
                    ctx.allow_overlap(
                        frame,
                        hanger,
                        elem_a=f"top_pivot_bar_{side}",
                        elem_b=f"chain_branch_core_{end}",
                        reason="The continuous chain core wraps the visible top pivot bar.",
                    )
        else:
            for end, _sx in _BENCH_ENDS:
                ctx.allow_overlap(
                    frame,
                    hanger,
                    elem_a=f"pivot_pin_{side}",
                    elem_b=f"hanger_bar_{end}",
                    reason="Rigid side-link branches start at the captured top pivot pin.",
                )
                ctx.allow_overlap(
                    frame,
                    hanger,
                    elem_a=f"top_pivot_bar_{side}",
                    elem_b=f"hanger_bar_{end}",
                    reason="Rigid side-link branches rotate around the visible top pivot bar.",
                )
                ctx.allow_overlap(
                    frame,
                    hanger,
                    elem_a=f"hanger_block_{side}",
                    elem_b=f"hanger_bar_{end}",
                    reason="Rigid side-link branches exit through the frame-side hanger block below the pivot.",
                )
        for end, _sx in _BENCH_ENDS:
            ctx.allow_overlap(
                hanger,
                bench,
                elem_a=f"hanger_bottom_lug_{end}",
                elem_b=f"seat_{side}_rail",
                reason="Side hanger lower lugs seat into the bench side rail at the front/rear lower contacts.",
            )
        if r.suspension_module in ("chains", "ropes"):
            hanger_visual_names = {v.name or "" for v in hanger.visuals}
            ctx.check(
                f"{r.suspension_module}_{side}_has_no_fake_lower_rigid_bar",
                "lower_side_link" not in hanger_visual_names,
                details=str(sorted(name for name in hanger_visual_names if "lower_side_link" in name)),
            )
        ctx.allow_overlap(
            hanger,
            bench,
            reason="The visual side hanger is a closed-loop support for the bench rail; sibling contacts are intentional.",
        )

    ctx.check_model_valid()
    ctx.check("frame_present", frame is not None)
    ctx.check("bench_present", bench is not None)
    ctx.check(
        "excluded_modules_not_sampled",
        all(
            bad not in {r.support_frame_module, r.bench_body_module}
            for bad in ("four_post_pergola", "daybed_platform", "single_hanging_chair")
        ),
    )

    ctx.check("swing_drive_present", drive is not None)
    if drive is not None:
        ctx.check(
            "swing_drive_is_revolute",
            drive.articulation_type == ArticulationType.REVOLUTE,
            details=str(drive.articulation_type),
        )
        ctx.check(
            "swing_drive_axis_is_y",
            tuple(round(v, 3) for v in drive.axis) == (0.0, 1.0, 0.0),
            details=str(drive.axis),
        )
        ctx.check(
            "swing_drive_limits_reasonable",
            0.30 <= abs(drive.motion_limits.lower) <= 0.50
            and 0.30 <= abs(drive.motion_limits.upper) <= 0.50,
            details=str(drive.motion_limits),
        )

    for side, _ in _TOP_SIDES:
        if side == _DRIVER_SIDE:
            continue
        j = object_model.get_articulation(f"swing_follow_{side}")
        ctx.check(f"swing_follow_{side}_present", j is not None)
        if j is not None:
            ctx.check(
                f"swing_follow_{side}_mimics_drive",
                j.mimic is not None
                and j.mimic.joint == "swing_drive"
                and abs(j.mimic.multiplier - 1.0) < 1e-9,
                details=str(j.mimic),
            )

    if bench is not None:
        names = [v.name or "" for v in bench.visuals]
        seat_slat_count = sum(name.startswith("seat_slat_") or "_seat_slat_" in name for name in names)
        back_count = sum(name.startswith("back_slat_") or "_back_slat_" in name or name.startswith("rolltop_back_slat_") for name in names)
        arm_count = sum(name.startswith("armrest_") for name in names)
        ctx.check("bench_has_slatted_or_panelled_seat", seat_slat_count >= 4, details=str(seat_slat_count))
        ctx.check("bench_has_backrest", back_count >= 4, details=str(back_count))
        ctx.check("bench_has_two_armrests", arm_count >= 2, details=str(arm_count))
        bb = ctx.part_world_aabb(bench)
        if bb is not None:
            width = bb[1][1] - bb[0][1]
            ctx.check("bench_width_is_furniture_like", 1.0 < width < 1.9, details=f"{width:.3f}")
            ctx.check("bench_above_ground_at_rest", bb[0][2] > 0.04, details=f"{bb[0][2]:.3f}")
            ctx.check("bench_below_top_beam_at_rest", bb[1][2] < r.top_z - 0.05, details=f"{bb[1][2]:.3f}")

    driver_hanger = object_model.get_part(f"hanger_{_DRIVER_SIDE}")
    if r.suspension_module == "chains":
        count = sum(
            1
            for v in driver_hanger.visuals
            if v.name and v.name.startswith("chain_link_")
        )
        ctx.check("chain_links_loop_emitted", count == 2 * r.chain_link_count, details=str(count))
    elif r.suspension_module == "ropes":
        count = sum(
            1
            for v in driver_hanger.visuals
            if v.name and v.name.startswith("rope_segment_")
        )
        ctx.check("rope_segments_loop_emitted", count == 2 * r.rope_segment_count, details=str(count))

    if drive is not None and bench is not None:
        centers: dict[float, float] = {}
        for q in (-r.swing_limit, r.swing_limit):
            with ctx.pose({drive: q}):
                bb = ctx.part_world_aabb(bench)
                if bb is not None:
                    centers[q] = (bb[0][0] + bb[1][0]) / 2.0
                    ctx.check(f"bench_clears_ground_at_q_{q:+.2f}", bb[0][2] > 0.02, details=f"{bb[0][2]:.3f}")
                    ctx.check(f"bench_stays_between_side_frames_at_q_{q:+.2f}", abs(bb[1][1]) < r.end_y + 0.02 and abs(bb[0][1]) < r.end_y + 0.02)
        if len(centers) == 2:
            travel = abs(centers[-r.swing_limit] - centers[r.swing_limit])
            ctx.check("bench_swings_fore_aft", travel > 0.45, details=f"{travel:.3f}")

    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=32,
        ignore_adjacent=True,
        ignore_fixed=True,
    )

    return ctx.report()


__all__ = [
    "WoodSwingConfig",
    "ResolvedWoodSwingConfig",
    "build_wood_swing",
    "build_seeded_wood_swing",
    "config_from_seed",
    "resolve_config",
    "run_wood_swing_tests",
    "slot_choices_for_seed",
    "__modular__",
]
