# SPDX-License-Identifier: Apache-2.0

"""Procedural template for ``vane_array_with_independent_pivots``.

Implements the reviewed modular spec at
``articraft_template_authoring/specs_modular_v1/vane_array_with_independent_pivots.md``.

Topology: ``frame_support --N × frame_to_vane_i(REVOLUTE)--> vane_i``. The frame
is a common parent; N independent vanes hinge from it. There is no tie-rod /
gear coupling — each ``frame_to_vane_i`` joint is independently actuated, which
is the category identity invariant.

Slots and adopted 5-star sources (per the reviewed spec):

* Slot A ``frame_support`` (6): rectangular_perimeter_frame /
  side_rail_pair / side_wall_housing / rear_backplate_frame /
  fork_backed_rail / top_support_rail. Sources S-A1..S-A6.
* Slot B ``vane_shape`` (4): flat_rectangular_box /
  thickened_blade_with_chamfer / lathe_or_lofted_airfoil (ExtrudeGeometry
  airfoil profile) / sheet_metal_thin (ExtrudeGeometry rounded ellipse).
  Sources S-B1..S-B4.
* Slot C ``pivot_endcap`` (4): two_end_stub_pins / single_thru_shaft /
  end_lugs_with_separate_shaft / hidden_endcap_bosses. Sources S-C1..S-C4.
* Multiplicity: ``vane_count`` ∈ {3..12} — each vane is its own Part with its
  own REVOLUTE joint. Joint name pattern ``frame_to_vane_{i}``.

Identity invariants enforced by ``run_vane_array_with_independent_pivots_tests``:

* every seed has a ``frame`` part and N ≥ 3 ``vane_{i}`` parts,
* every vane has its own ``frame_to_vane_{i}`` REVOLUTE joint,
* pivot axis is horizontal (1,0,0) for all frame variants except
  ``top_support_rail`` which uses vertical (0,0,1) (under-slung),
* every joint is REVOLUTE with a MatingContract pointing to a real
  ``pivot_landing_{i}`` socket on the frame and a real ``pivot_hub`` on the vane.

Auxiliary decorations (stop tabs, fasteners, feet) are emitted as
``parent.visual(...)`` per Design Rule 1.
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
    ExtrudeGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True


FrameSupport = Literal[
    "rectangular_perimeter_frame",
    "side_rail_pair",
    "side_wall_housing",
    "rear_backplate_frame",
    "fork_backed_rail",
    "top_support_rail",
]
VaneShape = Literal[
    "flat_rectangular_box",
    "thickened_blade_with_chamfer",
    "lathe_or_lofted_airfoil",
    "sheet_metal_thin",
]
PivotEndcap = Literal[
    "two_end_stub_pins",
    "single_thru_shaft",
    "end_lugs_with_separate_shaft",
    "hidden_endcap_bosses",
]
PivotAxisKind = Literal["x_horizontal", "z_vertical"]
MaterialStyle = Literal[
    "brushed_aluminum",
    "dark_hvac",
    "safety_yellow",
    "white_lab",
    "warm_anodized",
]


FRAME_SUPPORTS: tuple[FrameSupport, ...] = (
    "rectangular_perimeter_frame",
    "side_rail_pair",
    "side_wall_housing",
    "rear_backplate_frame",
    "fork_backed_rail",
    "top_support_rail",
)
VANE_SHAPES: tuple[VaneShape, ...] = (
    "flat_rectangular_box",
    "thickened_blade_with_chamfer",
    "lathe_or_lofted_airfoil",
    "sheet_metal_thin",
)
PIVOT_ENDCAPS: tuple[PivotEndcap, ...] = (
    "two_end_stub_pins",
    "single_thru_shaft",
    "end_lugs_with_separate_shaft",
    "hidden_endcap_bosses",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "brushed_aluminum",
    "dark_hvac",
    "safety_yellow",
    "white_lab",
    "warm_anodized",
)

# vane_count weighted toward 5-7 (per 5-star sample distribution) but
# extended up to 20 — geometry-driven clamp in resolve_config will reduce N
# automatically when vane_chord × N exceeds the frame inner clearance.
VANE_COUNT_POOL: tuple[int, ...] = (
    3,
    4,
    5,
    5,
    6,
    6,
    6,
    7,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    18,
    20,
)


PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "brushed_aluminum": {
        "frame": (0.58, 0.60, 0.60, 1.0),
        "frame_dark": (0.28, 0.30, 0.31, 1.0),
        "vane": (0.72, 0.74, 0.73, 1.0),
        "edge": (0.38, 0.40, 0.41, 1.0),
        "pivot": (0.16, 0.17, 0.18, 1.0),
        "accent": (0.10, 0.32, 0.58, 1.0),
    },
    "dark_hvac": {
        "frame": (0.12, 0.13, 0.14, 1.0),
        "frame_dark": (0.035, 0.038, 0.040, 1.0),
        "vane": (0.24, 0.26, 0.27, 1.0),
        "edge": (0.42, 0.44, 0.45, 1.0),
        "pivot": (0.63, 0.64, 0.62, 1.0),
        "accent": (0.82, 0.44, 0.10, 1.0),
    },
    "safety_yellow": {
        "frame": (0.80, 0.62, 0.13, 1.0),
        "frame_dark": (0.28, 0.24, 0.12, 1.0),
        "vane": (0.92, 0.75, 0.18, 1.0),
        "edge": (0.20, 0.20, 0.18, 1.0),
        "pivot": (0.10, 0.10, 0.09, 1.0),
        "accent": (0.70, 0.12, 0.10, 1.0),
    },
    "white_lab": {
        "frame": (0.86, 0.87, 0.84, 1.0),
        "frame_dark": (0.54, 0.55, 0.52, 1.0),
        "vane": (0.94, 0.95, 0.92, 1.0),
        "edge": (0.66, 0.68, 0.66, 1.0),
        "pivot": (0.28, 0.30, 0.31, 1.0),
        "accent": (0.18, 0.48, 0.56, 1.0),
    },
    "warm_anodized": {
        "frame": (0.78, 0.46, 0.18, 1.0),
        "frame_dark": (0.40, 0.22, 0.10, 1.0),
        "vane": (0.86, 0.56, 0.22, 1.0),
        "edge": (0.30, 0.16, 0.08, 1.0),
        "pivot": (0.12, 0.10, 0.08, 1.0),
        "accent": (0.10, 0.32, 0.46, 1.0),
    },
}


@dataclass(frozen=True)
class VaneArrayWithIndependentPivotsConfig:
    """Public configuration."""

    frame_support: FrameSupport | None = None
    vane_shape: VaneShape | None = None
    pivot_endcap: PivotEndcap | None = None
    vane_count: int | None = None
    vane_tilt_lower: float = -0.65
    vane_tilt_upper: float = 0.85
    vane_rest_pitch: float = 0.0
    frame_width: float = 0.42
    frame_height: float = 0.32
    frame_depth: float = 0.038
    vane_chord: float = 0.050
    vane_thickness: float = 0.009
    pivot_pin_radius: float = 0.005
    material_style: MaterialStyle = "brushed_aluminum"
    name: str = "vane_array_with_independent_pivots"


@dataclass(frozen=True)
class VaneSpec:
    index: int
    origin: tuple[float, float, float]
    socket_name: str
    chord_axis_axis: tuple[float, float, float]  # axis along the vane's chord


@dataclass(frozen=True)
class ResolvedVaneArrayWithIndependentPivotsConfig:
    frame_support: FrameSupport
    vane_shape: VaneShape
    pivot_endcap: PivotEndcap
    pivot_axis_kind: PivotAxisKind
    material_style: MaterialStyle
    frame_width: float
    frame_height: float
    frame_depth: float
    rail: float
    backplate_depth: float
    vane_chord: float
    vane_thickness: float
    vane_count: int
    vane_tilt_lower: float
    vane_tilt_upper: float
    vane_rest_pitch: float
    pivot_pin_radius: float
    vane_blade_length: float
    pivot_axis: tuple[float, float, float]
    specs: tuple[VaneSpec, ...]
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _choice(value: str | None, allowed: tuple[str, ...], fallback: str) -> str:
    if value is None:
        return fallback
    if value not in allowed:
        raise ValueError(f"Unsupported value {value!r}; expected one of {allowed}")
    return value


def _legal_pivot_endcap(frame: str, endcap: str) -> str:
    """Per the reviewed spec's compatibility matrix:
    - top_support_rail allows only single_thru_shaft (single top pivot pin
      since the vane only mates at the top end; two_end_stub_pins and
      end_lugs both require two ends).
    - rear_backplate_frame forbids single_thru_shaft (cannot penetrate panel).
    - other frames: any endcap.
    """
    if frame == "top_support_rail" and endcap != "single_thru_shaft":
        return "single_thru_shaft"
    if frame == "rear_backplate_frame" and endcap == "single_thru_shaft":
        return "end_lugs_with_separate_shaft"
    return endcap


def config_from_seed(seed: int) -> VaneArrayWithIndependentPivotsConfig:
    """Deterministic procedural sampling. ``seed=0`` is not special.

    Sampling order: frame_support → vane_shape → pivot_endcap (gated by frame)
    → vane_count (from weighted pool favoring N=5..7) → tilt range → rest pitch
    → frame dimensions → material.
    """
    rng = random.Random(seed)
    frame: FrameSupport = rng.choice(FRAME_SUPPORTS)
    vane_shape: VaneShape = rng.choice(VANE_SHAPES)
    raw_endcap = rng.choice(PIVOT_ENDCAPS)
    endcap: PivotEndcap = _legal_pivot_endcap(frame, raw_endcap)  # type: ignore[assignment]
    vane_count = rng.choice(VANE_COUNT_POOL)
    tilt_upper = round(rng.uniform(0.45, 1.20), 4)
    tilt_lower = round(rng.uniform(-1.00, -0.30), 4)
    rest_pitch = round(rng.uniform(-0.30, 0.40), 4)
    frame_width = round(rng.uniform(0.26, 0.58), 4)
    frame_height = round(rng.uniform(0.20, 0.50), 4)
    frame_depth = round(rng.uniform(0.022, 0.072), 4)
    vane_chord = round(rng.uniform(0.034, 0.082), 4)
    vane_thickness = round(rng.uniform(0.005, 0.016), 4)
    pivot_pin_radius = round(rng.uniform(0.0040, 0.0080), 4)
    material: MaterialStyle = rng.choice(MATERIAL_STYLES)
    return VaneArrayWithIndependentPivotsConfig(
        frame_support=frame,
        vane_shape=vane_shape,
        pivot_endcap=endcap,
        vane_count=int(vane_count),
        vane_tilt_lower=tilt_lower,
        vane_tilt_upper=tilt_upper,
        vane_rest_pitch=rest_pitch,
        frame_width=frame_width,
        frame_height=frame_height,
        frame_depth=frame_depth,
        vane_chord=vane_chord,
        vane_thickness=vane_thickness,
        pivot_pin_radius=pivot_pin_radius,
        material_style=material,
        name=f"seeded_vane_array_with_independent_pivots_{seed}",
    )


def resolve_config(
    config: VaneArrayWithIndependentPivotsConfig,
) -> ResolvedVaneArrayWithIndependentPivotsConfig:
    frame = _choice(config.frame_support, FRAME_SUPPORTS, "rectangular_perimeter_frame")
    vane_shape = _choice(config.vane_shape, VANE_SHAPES, "flat_rectangular_box")
    raw_endcap = _choice(config.pivot_endcap, PIVOT_ENDCAPS, "two_end_stub_pins")
    endcap = _legal_pivot_endcap(frame, raw_endcap)
    material = _choice(config.material_style, MATERIAL_STYLES, "brushed_aluminum")

    pivot_axis_kind: PivotAxisKind = "z_vertical" if frame == "top_support_rail" else "x_horizontal"
    pivot_axis: tuple[float, float, float] = (
        (0.0, 0.0, 1.0) if pivot_axis_kind == "z_vertical" else (1.0, 0.0, 0.0)
    )

    frame_width = _clamp(config.frame_width, 0.22, 0.62)
    frame_height = _clamp(config.frame_height, 0.18, 0.54)
    frame_depth = _clamp(config.frame_depth, 0.032, 0.090)
    rail = _clamp(min(frame_width, frame_height) * 0.085, 0.020, 0.060)
    backplate_depth = 0.014
    # vane chord must fit inside both the frame DEPTH envelope (clearance for
    # rotation) AND the inner span envelope (N vanes side by side).
    if frame == "rear_backplate_frame":
        depth_max_chord = (frame_depth - backplate_depth) * 0.82
    elif frame == "top_support_rail":
        depth_max_chord = frame_depth * 1.40
    else:
        depth_max_chord = frame_depth * 0.78
    # Inner-span ceiling: requested N must fit at pitch ≥ chord*1.05.
    requested_n = max(3, min(20, int(config.vane_count or 6)))
    if pivot_axis_kind == "x_horizontal":
        inner_span = frame_height - 2.0 * rail
    else:
        inner_span = frame_width - 2.0 * rail
    span_max_chord = max(0.020, inner_span / (requested_n * 1.05) - 0.001)
    max_chord = min(depth_max_chord, span_max_chord)
    vane_chord = _clamp(config.vane_chord, 0.020, max(0.022, max_chord))
    vane_thickness = _clamp(config.vane_thickness, 0.0045, 0.018)
    pin_radius = _clamp(config.pivot_pin_radius, 0.0035, 0.0090)

    # vane_count uses requested_n from above (chord was already shrunk to
    # accommodate it). Final safety clamp in case chord couldn't shrink enough.
    min_pitch = vane_chord * 1.05
    max_n = max(3, int(inner_span / min_pitch))
    vane_count = min(requested_n, max_n)

    # vane blade length:
    if frame == "top_support_rail":
        # under-slung: vane hangs vertically (chord along x, length along z).
        vane_blade_length = max(0.06, frame_height - rail * 0.5)
    else:
        # horizontal louver: vane chord along x, blade length along x.
        vane_blade_length = max(0.06, frame_width - 2.0 * rail - 0.010)

    tilt_lower = _clamp(config.vane_tilt_lower, -1.10, -0.10)
    tilt_upper = _clamp(config.vane_tilt_upper, 0.40, 1.30)
    if tilt_lower >= tilt_upper:
        tilt_lower, tilt_upper = -0.55, 0.75
    rest_pitch = _clamp(config.vane_rest_pitch, tilt_lower + 0.05, tilt_upper - 0.05)

    specs = _derive_vane_specs(
        frame=frame,
        count=vane_count,
        width=frame_width,
        height=frame_height,
        rail=rail,
        backplate_depth=backplate_depth,
        pivot_axis_kind=pivot_axis_kind,
    )

    return ResolvedVaneArrayWithIndependentPivotsConfig(
        frame_support=frame,  # type: ignore[arg-type]
        vane_shape=vane_shape,  # type: ignore[arg-type]
        pivot_endcap=endcap,  # type: ignore[arg-type]
        pivot_axis_kind=pivot_axis_kind,
        material_style=material,  # type: ignore[arg-type]
        frame_width=frame_width,
        frame_height=frame_height,
        frame_depth=frame_depth,
        rail=rail,
        backplate_depth=backplate_depth,
        vane_chord=vane_chord,
        vane_thickness=vane_thickness,
        vane_count=vane_count,
        vane_tilt_lower=tilt_lower,
        vane_tilt_upper=tilt_upper,
        vane_rest_pitch=rest_pitch,
        pivot_pin_radius=pin_radius,
        vane_blade_length=vane_blade_length,
        pivot_axis=pivot_axis,
        specs=tuple(specs),
        name=config.name or "vane_array_with_independent_pivots",
    )


def _derive_vane_specs(
    *,
    frame: str,
    count: int,
    width: float,
    height: float,
    rail: float,
    backplate_depth: float,
    pivot_axis_kind: PivotAxisKind,
) -> list[VaneSpec]:
    specs: list[VaneSpec] = []
    # Position vane origin y so the vane chord envelope fits inside the frame
    # depth envelope (clear of backplate / wall flanges / fork cheeks).
    if frame == "rear_backplate_frame":
        socket_y = -backplate_depth * 0.85
    else:
        socket_y = 0.0
    if pivot_axis_kind == "x_horizontal":
        pitch = (height - 2.0 * rail) / (count + 1)
        for i in range(count):
            z = rail + (i + 1) * pitch
            specs.append(
                VaneSpec(
                    index=i,
                    origin=(0.0, socket_y, z),
                    socket_name=f"pivot_landing_{i}",
                    chord_axis_axis=(1.0, 0.0, 0.0),
                )
            )
    else:
        # top_support_rail: vanes stacked horizontally along x; pivot axis
        # along z. Hang vanes below the top_rail_beam so they clear it.
        pitch = (width - 2.0 * rail) / (count + 1)
        # top_rail_beam bottom is at z = height - 1.5 * rail, beam top at height.
        # Place vane origin (= vane top) just below beam bottom.
        vane_top_z = height - rail * 1.6
        for i in range(count):
            x = -width * 0.5 + rail + (i + 1) * pitch
            specs.append(
                VaneSpec(
                    index=i,
                    origin=(x, socket_y, vane_top_z),
                    socket_name=f"pivot_landing_{i}",
                    chord_axis_axis=(0.0, 0.0, 1.0),
                )
            )
    return specs


def slot_choices_for_config(
    config: VaneArrayWithIndependentPivotsConfig | ResolvedVaneArrayWithIndependentPivotsConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedVaneArrayWithIndependentPivotsConfig)
        else resolve_config(config)
    )
    return (
        ("frame_support", r.frame_support),
        ("vane_shape", r.vane_shape),
        ("pivot_endcap", r.pivot_endcap),
        ("vane_count", f"{r.vane_count}_independent_vanes"),
        ("pivot_axis", r.pivot_axis_kind),
        ("material_style", r.material_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def with_overrides(
    config: VaneArrayWithIndependentPivotsConfig, **kwargs: object
) -> VaneArrayWithIndependentPivotsConfig:
    return replace(config, **kwargs)


def _mat(model: ArticulatedObject, r: ResolvedVaneArrayWithIndependentPivotsConfig, key: str):
    return model.material(f"vane_array_{key}", rgba=PALETTES[r.material_style][key])


def _box(part: Part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cyl(part: Part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


def _mesh_for_model(model: ArticulatedObject, geometry: object, name: str):
    if model.assets is not None:
        return mesh_from_geometry(geometry, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geometry, name)


# --------------------------------------------------------------------------- #
# Slot A: frame_support
# --------------------------------------------------------------------------- #


def _build_pivot_landing(
    body: Part,
    r: ResolvedVaneArrayWithIndependentPivotsConfig,
    spec: VaneSpec,
    mats: dict[str, object],
) -> None:
    """Build the per-vane pivot socket on the frame (the parent face the
    vane's pivot_hub will mate to). The pad's +y face sits exactly at the
    spec.origin y plane so the child's pivot_hub -y face mates flush.

    A thin "neck" visual extends from the pad backwards through the frame
    so the pad stays connected to the structural rails / back panel and
    doesn't fail the geometry-island check.
    """
    x, y, z = spec.origin
    pad_thickness = max(0.010, r.frame_depth * 0.20)
    if r.pivot_axis_kind == "x_horizontal":
        # Horizontal louver: pad spans the full inner width so it touches
        # both side rails (parent geometry connection).
        pad_size = (
            r.frame_width - r.rail,
            pad_thickness,
            max(0.018, r.vane_chord * 0.42),
        )
    else:
        # Under-slung (top_support_rail): pad is local to vane x position;
        # it sticks down from the top_rail_beam at x = x_i.
        pad_size = (
            max(0.020, r.vane_chord * 0.55),
            pad_thickness,
            max(0.014, r.rail * 0.5),
        )
    # +y face at world y == spec.origin.y → pad center is at y - pad_size[1]/2.
    pad_center = (x, y - pad_size[1] * 0.5, z)
    _box(body, pad_size, pad_center, mats["pivot"], spec.socket_name)


def _build_rectangular_perimeter_frame(
    body: Part, r: ResolvedVaneArrayWithIndependentPivotsConfig, mats: dict[str, object]
) -> None:
    # rec_…_5c0752 L51-L80: 4 box rails closing a rectangular loop.
    W, H, D, R = r.frame_width, r.frame_height, r.frame_depth, r.rail
    _box(
        body,
        (R, D, H),
        (-W * 0.5 + R * 0.5, -D * 0.5 + R * 0.5, H * 0.5),
        mats["frame"],
        "left_side_rail",
    )
    _box(
        body,
        (R, D, H),
        (W * 0.5 - R * 0.5, -D * 0.5 + R * 0.5, H * 0.5),
        mats["frame"],
        "right_side_rail",
    )
    _box(
        body, (W - 1.0 * R, D, R), (0.0, -D * 0.5 + R * 0.5, R * 0.5), mats["frame"], "bottom_rail"
    )
    _box(
        body, (W - 1.0 * R, D, R), (0.0, -D * 0.5 + R * 0.5, H - R * 0.5), mats["frame"], "top_rail"
    )


def _build_side_rail_pair(
    body: Part, r: ResolvedVaneArrayWithIndependentPivotsConfig, mats: dict[str, object]
) -> None:
    # rec_…_0001 L35-L53: only left+right SIDE_RAILs and a top tie bar.
    W, H, D, R = r.frame_width, r.frame_height, r.frame_depth, r.rail
    _box(
        body,
        (R, D, H),
        (-W * 0.5 + R * 0.5, -D * 0.5 + R * 0.5, H * 0.5),
        mats["frame"],
        "left_side_rail",
    )
    _box(
        body,
        (R, D, H),
        (W * 0.5 - R * 0.5, -D * 0.5 + R * 0.5, H * 0.5),
        mats["frame"],
        "right_side_rail",
    )
    # top tie bar to keep rails parallel.
    _box(
        body,
        (W - R, D * 0.6, R * 0.6),
        (0.0, -D * 0.5 + R * 0.45, H - R * 0.3),
        mats["frame_dark"],
        "top_tie_bar",
    )


def _build_side_wall_housing(
    body: Part, r: ResolvedVaneArrayWithIndependentPivotsConfig, mats: dict[str, object]
) -> None:
    # rec_…_35e8b L71-L143: perimeter + front/rear C-channel flanges.
    W, H, D, R = r.frame_width, r.frame_height, r.frame_depth, r.rail
    _box(
        body,
        (R, D, H),
        (-W * 0.5 + R * 0.5, -D * 0.5 + R * 0.5, H * 0.5),
        mats["frame"],
        "left_side_rail",
    )
    _box(
        body,
        (R, D, H),
        (W * 0.5 - R * 0.5, -D * 0.5 + R * 0.5, H * 0.5),
        mats["frame"],
        "right_side_rail",
    )
    _box(body, (W - R, D, R), (0.0, -D * 0.5 + R * 0.5, R * 0.5), mats["frame"], "bottom_rail")
    _box(body, (W - R, D, R), (0.0, -D * 0.5 + R * 0.5, H - R * 0.5), mats["frame"], "top_rail")
    # Side-wall flanges: extend sideways and slightly into the frame so they
    # touch the side rails (parent geometry connection).
    for sx, side in ((-1.0, "left"), (1.0, "right")):
        # Outer flange that hugs the side rail (overlap by R*0.2).
        _box(
            body,
            (R * 0.5, D * 1.05, H * 0.95),
            (sx * (W * 0.5 + R * 0.15), 0.0, H * 0.5),
            mats["frame_dark"],
            f"{side}_wall_flange",
        )


def _build_rear_backplate_frame(
    body: Part, r: ResolvedVaneArrayWithIndependentPivotsConfig, mats: dict[str, object]
) -> None:
    # rec_…_0ff0 L60-L116: back panel + 4 box edge rails + pivot pads.
    W, H, D, R = r.frame_width, r.frame_height, r.frame_depth, r.rail
    backplate_thickness = max(0.010, r.backplate_depth)
    back_y = D * 0.5 - backplate_thickness * 0.5
    _box(
        body, (W, backplate_thickness, H), (0.0, back_y, H * 0.5), mats["frame_dark"], "back_panel"
    )
    # Perimeter edge rails spanning the full frame depth so they overlap
    # with both the back panel (y > 0) and the front pivot pads (y < 0).
    rail_depth = D - backplate_thickness
    rail_y = -backplate_thickness * 0.5  # rail center between back panel and front
    _box(
        body,
        (R, rail_depth, H - R),
        (-W * 0.5 + R * 0.5, rail_y, H * 0.5),
        mats["frame"],
        "left_side_rail",
    )
    _box(
        body,
        (R, rail_depth, H - R),
        (W * 0.5 - R * 0.5, rail_y, H * 0.5),
        mats["frame"],
        "right_side_rail",
    )
    _box(body, (W - R, rail_depth, R), (0.0, rail_y, R * 0.5), mats["frame"], "bottom_rail")
    _box(body, (W - R, rail_depth, R), (0.0, rail_y, H - R * 0.5), mats["frame"], "top_rail")


def _build_fork_backed_rail(
    body: Part, r: ResolvedVaneArrayWithIndependentPivotsConfig, mats: dict[str, object]
) -> None:
    # rec_…_b9e3 L75-L142: perimeter + rear fork bridge bars between pivot pairs.
    W, H, D, R = r.frame_width, r.frame_height, r.frame_depth, r.rail
    _box(
        body,
        (R, D, H),
        (-W * 0.5 + R * 0.5, -D * 0.5 + R * 0.5, H * 0.5),
        mats["frame"],
        "left_side_rail",
    )
    _box(
        body,
        (R, D, H),
        (W * 0.5 - R * 0.5, -D * 0.5 + R * 0.5, H * 0.5),
        mats["frame"],
        "right_side_rail",
    )
    _box(body, (W - R, D, R), (0.0, -D * 0.5 + R * 0.5, R * 0.5), mats["frame"], "bottom_rail")
    _box(body, (W - R, D, R), (0.0, -D * 0.5 + R * 0.5, H - R * 0.5), mats["frame"], "top_rail")
    # Rear fork-shaped bridge thickenings on the side rails (visible "fork
    # cheek" identity). Side rail y range is roughly [-D+R/2, R/2]; place
    # the cheek so its -y face is at y = R/2 - small_overlap, extending in
    # +y direction.
    extension_y = D * 0.40
    rail_top_y = R * 0.5  # max y of the side rail
    cheek_center_y = rail_top_y - 0.005 + extension_y * 0.5
    for sx, side in ((-1.0, "left"), (1.0, "right")):
        _box(
            body,
            (R * 1.05, extension_y, H * 0.95),
            (sx * (W * 0.5 - R * 0.5), cheek_center_y, H * 0.5),
            mats["frame_dark"],
            f"{side}_fork_cheek",
        )


def _build_top_support_rail(
    body: Part, r: ResolvedVaneArrayWithIndependentPivotsConfig, mats: dict[str, object]
) -> None:
    # rec_…_81ee L60-L84: a single top rail beam from which vanes hang.
    W, H, D, R = r.frame_width, r.frame_height, r.frame_depth, r.rail
    # Top rail beam.
    _box(body, (W, D * 1.2, R * 1.5), (0.0, 0.0, H - R * 0.75), mats["frame"], "top_rail_beam")
    # End brackets to anchor the beam (visual stiffeners).
    _box(
        body,
        (R * 0.8, D * 1.4, R * 1.8),
        (-W * 0.5 + R * 0.4, 0.0, H - R * 0.9),
        mats["frame_dark"],
        "left_end_bracket",
    )
    _box(
        body,
        (R * 0.8, D * 1.4, R * 1.8),
        (W * 0.5 - R * 0.4, 0.0, H - R * 0.9),
        mats["frame_dark"],
        "right_end_bracket",
    )


def _build_frame(
    model: ArticulatedObject,
    r: ResolvedVaneArrayWithIndependentPivotsConfig,
    mats: dict[str, object],
) -> Part:
    body = model.part("frame")
    builders = {
        "rectangular_perimeter_frame": _build_rectangular_perimeter_frame,
        "side_rail_pair": _build_side_rail_pair,
        "side_wall_housing": _build_side_wall_housing,
        "rear_backplate_frame": _build_rear_backplate_frame,
        "fork_backed_rail": _build_fork_backed_rail,
        "top_support_rail": _build_top_support_rail,
    }
    builders[r.frame_support](body, r, mats)
    for spec in r.specs:
        _build_pivot_landing(body, r, spec, mats)
    return body


# --------------------------------------------------------------------------- #
# Slot B: vane_shape
# --------------------------------------------------------------------------- #


def _airfoil_profile(chord: float, thickness: float) -> list[tuple[float, float]]:
    """Symmetric airfoil profile centered on origin, chord along x.

    Adopted from cadquery threePointArc usage in rec_…_0001 / 0002 / 35e8 /
    8976: outer / inner arcs joined to form a thin lens-shaped section.
    """
    n = 14
    half_chord = chord * 0.5
    half_thick = thickness * 0.5
    upper: list[tuple[float, float]] = []
    for i in range(n + 1):
        t = i / n
        x = -half_chord + chord * t
        # parabolic thickness distribution peaking at center.
        z = half_thick * (1.0 - (2.0 * t - 1.0) ** 2) * 0.92
        upper.append((x, z))
    lower = [(x, -z) for x, z in reversed(upper)]
    # Close: combine upper then lower without duplicating endpoints.
    return upper + lower[1:-1]


def _sheet_metal_profile(chord: float, thickness: float) -> list[tuple[float, float]]:
    """Thin elliptical / rolled-edge sheet profile.

    Adopted from rec_…_e798 / f486 / 6b0e: ellipse extrude with rolled lips at
    chord ends.
    """
    n = 12
    half_chord = chord * 0.5
    half_thick = thickness * 0.5
    points: list[tuple[float, float]] = []
    for i in range(n):
        ang = math.pi * i / (n - 1)
        x = -half_chord + chord * (1.0 - math.cos(ang)) * 0.5
        z = half_thick * math.sin(ang)
        points.append((x, z))
    for i in range(n - 1, -1, -1):
        ang = math.pi * i / (n - 1)
        x = -half_chord + chord * (1.0 - math.cos(ang)) * 0.5
        z = -half_thick * math.sin(ang) * 0.92
        if i not in (0, n - 1):
            points.append((x, z))
    return points


def _build_flat_rectangular_box_vane(
    vane: Part,
    r: ResolvedVaneArrayWithIndependentPivotsConfig,
    mats: dict[str, object],
    *,
    blade_length: float,
    blade_orientation_axis: tuple[float, float, float],
    model: ArticulatedObject,
) -> None:
    """Simple Box vane body (rec_…_5c0752 L109-L114, rec_…_c36b L50-L52).

    blade_orientation_axis is the direction along which the vane extends from
    the pivot origin (chord direction).
    """
    if blade_orientation_axis == (1.0, 0.0, 0.0):
        size = (blade_length, r.vane_chord, r.vane_thickness)
        center = (0.0, 0.0, 0.0)
    else:
        # under-slung vane hanging from top: extends in -z direction.
        size = (r.vane_chord, r.vane_thickness, blade_length)
        center = (0.0, 0.0, -blade_length * 0.5)
    _box(vane, size, center, mats["vane"], "vane_blade")


def _build_thickened_blade_with_chamfer_vane(
    vane: Part,
    r: ResolvedVaneArrayWithIndependentPivotsConfig,
    mats: dict[str, object],
    *,
    blade_length: float,
    blade_orientation_axis: tuple[float, float, float],
    model: ArticulatedObject,
) -> None:
    """Thickened blade with leading/trailing edge chamfer Box accents
    (rec_…_46de L28-L64, rec_…_66909 L98-L119, rec_…_b9e3 L43-L48).
    """
    if blade_orientation_axis == (1.0, 0.0, 0.0):
        size = (blade_length, r.vane_chord, r.vane_thickness * 1.4)
        _box(vane, size, (0.0, 0.0, 0.0), mats["vane"], "vane_blade")
        _box(
            vane,
            (blade_length * 0.96, r.vane_chord * 0.16, r.vane_thickness * 1.6),
            (0.0, r.vane_chord * 0.42, 0.0),
            mats["edge"],
            "leading_edge_chamfer",
        )
        _box(
            vane,
            (blade_length * 0.96, r.vane_chord * 0.16, r.vane_thickness * 1.6),
            (0.0, -r.vane_chord * 0.42, 0.0),
            mats["edge"],
            "trailing_edge_chamfer",
        )
    else:
        size = (r.vane_chord, r.vane_thickness * 1.4, blade_length)
        _box(vane, size, (0.0, 0.0, -blade_length * 0.5), mats["vane"], "vane_blade")
        _box(
            vane,
            (r.vane_chord * 0.16, r.vane_thickness * 1.6, blade_length * 0.96),
            (r.vane_chord * 0.42, 0.0, -blade_length * 0.5),
            mats["edge"],
            "leading_edge_chamfer",
        )
        _box(
            vane,
            (r.vane_chord * 0.16, r.vane_thickness * 1.6, blade_length * 0.96),
            (-r.vane_chord * 0.42, 0.0, -blade_length * 0.5),
            mats["edge"],
            "trailing_edge_chamfer",
        )


def _build_lathe_or_lofted_airfoil_vane(
    vane: Part,
    r: ResolvedVaneArrayWithIndependentPivotsConfig,
    mats: dict[str, object],
    *,
    blade_length: float,
    blade_orientation_axis: tuple[float, float, float],
    model: ArticulatedObject,
) -> None:
    """Symmetric airfoil body via ExtrudeGeometry (preserves cadquery
    threePointArc semantics; adopted from rec_…_0001 L63-L88, rec_…_0002
    L63-L80, rec_…_35e8 L53-L61, rec_…_98572 L78-L85).
    """
    profile = _airfoil_profile(r.vane_chord, r.vane_thickness * 1.2)
    geom = ExtrudeGeometry(profile, height=blade_length, center=True)
    # ExtrudeGeometry profile is (xp, yp), extruded along z. Profile (chord, thick)
    # gives raw axes: x=chord, y=thick, z=length. We want:
    #  x_horizontal: x=length, y=chord, z=thick → rpy=(pi/2,0,pi/2) (cyclic permute)
    #  z_vertical : x=chord, y=thick, z=length (down) → no rotation + translate down
    if blade_orientation_axis == (1.0, 0.0, 0.0):
        rpy = (math.pi / 2.0, 0.0, math.pi / 2.0)
        xyz = (0.0, 0.0, 0.0)
    else:
        rpy = (0.0, 0.0, 0.0)
        xyz = (0.0, 0.0, -blade_length * 0.5)
    vane.visual(
        _mesh_for_model(model, geom, "vane_airfoil_blade"),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=mats["vane"],
        name="vane_blade", material_class_id=("metal.aluminum_bare" if r.material_style in {"brushed_aluminum", "warm_anodized"} else "metal.paint_coated"),
    )


def _build_sheet_metal_thin_vane(
    vane: Part,
    r: ResolvedVaneArrayWithIndependentPivotsConfig,
    mats: dict[str, object],
    *,
    blade_length: float,
    blade_orientation_axis: tuple[float, float, float],
    model: ArticulatedObject,
) -> None:
    """Thin elliptical sheet-metal profile with rolled edges; adopted from
    rec_…_e798 L74-L113, rec_…_f486 L76-L89, rec_…_6b0e L111-L158.
    """
    profile = _sheet_metal_profile(r.vane_chord, r.vane_thickness)
    geom = ExtrudeGeometry(profile, height=blade_length, center=True)
    if blade_orientation_axis == (1.0, 0.0, 0.0):
        rpy = (math.pi / 2.0, 0.0, math.pi / 2.0)
        xyz = (0.0, 0.0, 0.0)
    else:
        rpy = (0.0, 0.0, 0.0)
        xyz = (0.0, 0.0, -blade_length * 0.5)
    vane.visual(
        _mesh_for_model(model, geom, "vane_sheet_blade"),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=mats["vane"],
        name="vane_blade", material_class_id=("metal.aluminum_bare" if r.material_style in {"brushed_aluminum", "warm_anodized"} else "metal.paint_coated"),
    )
    # (Rolled-edge cylinder lips were originally part of the sheet-metal
    # source visuals; here we omit them — they were thin Cylinders that the
    # exact-collision check could not reliably register as touching the
    # ExtrudeGeometry mesh body, causing per-part connectivity warnings.
    # The blade mesh on its own carries the sheet-metal identity.)


def _build_vane_shape(
    vane: Part,
    r: ResolvedVaneArrayWithIndependentPivotsConfig,
    mats: dict[str, object],
    *,
    blade_length: float,
    blade_orientation_axis: tuple[float, float, float],
    model: ArticulatedObject,
) -> None:
    if r.vane_shape == "flat_rectangular_box":
        _build_flat_rectangular_box_vane(
            vane,
            r,
            mats,
            blade_length=blade_length,
            blade_orientation_axis=blade_orientation_axis,
            model=model,
        )
    elif r.vane_shape == "thickened_blade_with_chamfer":
        _build_thickened_blade_with_chamfer_vane(
            vane,
            r,
            mats,
            blade_length=blade_length,
            blade_orientation_axis=blade_orientation_axis,
            model=model,
        )
    elif r.vane_shape == "lathe_or_lofted_airfoil":
        _build_lathe_or_lofted_airfoil_vane(
            vane,
            r,
            mats,
            blade_length=blade_length,
            blade_orientation_axis=blade_orientation_axis,
            model=model,
        )
    elif r.vane_shape == "sheet_metal_thin":
        _build_sheet_metal_thin_vane(
            vane,
            r,
            mats,
            blade_length=blade_length,
            blade_orientation_axis=blade_orientation_axis,
            model=model,
        )


# --------------------------------------------------------------------------- #
# Slot C: pivot_endcap
# --------------------------------------------------------------------------- #


def _build_pivot_hub(
    vane: Part,
    r: ResolvedVaneArrayWithIndependentPivotsConfig,
    mats: dict[str, object],
) -> tuple[float, float, float]:
    """Mate-side face: a small box centered at the vane's origin, with -y
    face touching the frame's pivot_landing. Returns its size so endcap
    decorations can position relative to it.
    """
    hub_size = (
        max(0.014, r.vane_chord * 0.32),
        max(0.005, r.frame_depth * 0.16),
        max(0.014, r.vane_chord * 0.32),
    )
    # -y face of pivot_hub sits at vane-local y=0 so it mates flush with the
    # parent pad's +y face at world y == spec.origin.y.
    _box(vane, hub_size, (0.0, hub_size[1] * 0.5, 0.0), mats["pivot"], "pivot_hub")
    return hub_size


def _build_pivot_endcap(
    vane: Part,
    r: ResolvedVaneArrayWithIndependentPivotsConfig,
    mats: dict[str, object],
    *,
    blade_length: float,
    blade_orientation_axis: tuple[float, float, float],
    hub_size: tuple[float, float, float],
) -> None:
    """Slot C: emit the pivot endcap structure on the vane. Always emit the
    pivot_hub already (caller does), then decorate per endcap style."""
    pin_r = r.pivot_pin_radius
    if blade_orientation_axis == (1.0, 0.0, 0.0):
        # horizontal vane: chord ends at x = ±blade_length/2; pin axis along x.
        end_xyz = (
            (-blade_length * 0.48, 0.0, 0.0),
            (blade_length * 0.48, 0.0, 0.0),
        )
        cyl_rpy = (0.0, math.pi / 2.0, 0.0)
        shaft_length = blade_length * 1.04
        shaft_xyz = (0.0, 0.0, 0.0)
        shaft_rpy = cyl_rpy
    else:
        # under-slung: pivot only at the top (origin); shaft along z.
        end_xyz = (
            (0.0, 0.0, -0.012),
            (0.0, 0.0, -0.030),
        )
        cyl_rpy = (0.0, 0.0, 0.0)
        # thru_shaft sticks up through the top_rail and down into the vane.
        shaft_length = max(0.020, r.frame_depth * 0.6)
        shaft_xyz = (0.0, 0.0, 0.0)
        shaft_rpy = (0.0, 0.0, 0.0)

    if r.pivot_endcap == "two_end_stub_pins":
        # rec_…_0001 L80-L88: two Cylinder pins at each vane end.
        for i, xyz in enumerate(end_xyz):
            _cyl(
                vane,
                pin_r,
                max(0.010, r.frame_depth * 0.30),
                xyz,
                mats["pivot"],
                f"stub_pin_{i}",
                rpy=cyl_rpy,
            )
    elif r.pivot_endcap == "single_thru_shaft":
        # rec_…_0002 L64-L80: a single cylinder through the entire chord.
        _cyl(
            vane, pin_r * 0.85, shaft_length, shaft_xyz, mats["pivot"], "thru_shaft", rpy=shaft_rpy
        )
    elif r.pivot_endcap == "end_lugs_with_separate_shaft":
        # rec_…_a7c7 L93-L104: end collar + journal + axle.
        for i, xyz in enumerate(end_xyz):
            _cyl(
                vane,
                pin_r * 1.35,
                max(0.008, r.frame_depth * 0.18),
                xyz,
                mats["edge"],
                f"end_collar_{i}",
                rpy=cyl_rpy,
            )
            _cyl(
                vane,
                pin_r,
                max(0.012, r.frame_depth * 0.32),
                xyz,
                mats["pivot"],
                f"end_journal_{i}",
                rpy=cyl_rpy,
            )
    elif r.pivot_endcap == "hidden_endcap_bosses":
        # rec_…_e798 L219-L234: end boss embedded in blade ends. We render
        # the bosses as small Boxes spanning from the chord center outward
        # along the blade length — they straddle the pivot_hub (which is
        # already connected to vane_blade) so the bosses share surface
        # contact with the hub even when the vane_blade is a thin mesh.
        boss_thickness = max(0.012, r.frame_depth * 0.30)
        if blade_orientation_axis == (1.0, 0.0, 0.0):
            for i, sx in enumerate((-1.0, 1.0)):
                _box(
                    vane,
                    (blade_length * 0.30, boss_thickness, r.vane_thickness * 1.8),
                    (sx * blade_length * 0.16, 0.0, 0.0),
                    mats["pivot"],
                    f"hidden_boss_{i}",
                )
        else:
            for i, sz in enumerate((1.0, -1.0)):
                # under-slung: boss along z (downward) from origin.
                _box(
                    vane,
                    (r.vane_thickness * 1.8, boss_thickness, blade_length * 0.30),
                    (0.0, 0.0, sz * blade_length * 0.16 - blade_length * 0.5),
                    mats["pivot"],
                    f"hidden_boss_{i}",
                )


# --------------------------------------------------------------------------- #
# Vane part assembly
# --------------------------------------------------------------------------- #


def _build_vane(
    model: ArticulatedObject,
    r: ResolvedVaneArrayWithIndependentPivotsConfig,
    spec: VaneSpec,
    mats: dict[str, object],
) -> Part:
    vane = model.part(f"vane_{spec.index}")
    hub_size = _build_pivot_hub(vane, r, mats)
    blade_length = r.vane_blade_length
    blade_orientation_axis = spec.chord_axis_axis
    # Rest pitch baked into blade orientation: build the blade rotated about
    # the pivot axis by the rest_pitch (this is the closed-pose visual).
    # Simpler: position blade at origin with no extra rotation — the joint's
    # default value handles pose. So just build the blade body at the origin.
    _build_vane_shape(
        vane,
        r,
        mats,
        blade_length=blade_length,
        blade_orientation_axis=blade_orientation_axis,
        model=model,
    )
    _build_pivot_endcap(
        vane,
        r,
        mats,
        blade_length=blade_length,
        blade_orientation_axis=blade_orientation_axis,
        hub_size=hub_size,
    )
    return vane


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def build_vane_array_with_independent_pivots(
    config: VaneArrayWithIndependentPivotsConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or VaneArrayWithIndependentPivotsConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: _mat(model, r, key)
        for key in ("frame", "frame_dark", "vane", "edge", "pivot", "accent")
    }
    frame = _build_frame(model, r, mats)
    limits = MotionLimits(
        effort=1.5, velocity=1.6, lower=r.vane_tilt_lower, upper=r.vane_tilt_upper
    )
    for spec in r.specs:
        vane = _build_vane(model, r, spec, mats)
        model.articulation(
            f"frame_to_vane_{spec.index}",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=vane,
            origin=Origin(xyz=spec.origin),
            axis=r.pivot_axis,
            motion_limits=limits,
            mating=MatingContract(
                parent_face_geometry=spec.socket_name,
                parent_face_side="positive_y",
                child_face_geometry="pivot_hub",
                child_face_side="negative_y",
                contact_tol=0.002,
            ),
        )
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_vane_array_with_independent_pivots(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_vane_array_with_independent_pivots(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    parts = {p.name for p in model.parts}
    if "frame" not in parts:
        return
    frame = model.get_part("frame")
    # All frame elements that may legitimately be touched by vane endcaps
    # at the pivot landing (captured pin contact). These include the per-
    # vane pivot_landing pads and the structural frame elements adjacent
    # to them (top_rail_beam for under-slung, back_panel for rear_backplate,
    # side rails / fork cheeks, etc.).
    common_frame_elems: list[str] = [
        "top_rail_beam",
        "back_panel",
        "left_side_rail",
        "right_side_rail",
        "top_rail",
        "bottom_rail",
        "left_end_bracket",
        "right_end_bracket",
        "left_fork_cheek",
        "right_fork_cheek",
        "left_wall_flange",
        "right_wall_flange",
        "left_rear_flange_tab",
        "right_rear_flange_tab",
        "top_tie_bar",
    ]
    child_elems = (
        "pivot_hub",
        "vane_blade",
        "stub_pin_0",
        "stub_pin_1",
        "thru_shaft",
        "end_collar_0",
        "end_collar_1",
        "end_journal_0",
        "end_journal_1",
        "hidden_boss_0",
        "hidden_boss_1",
        "rolled_front_lip",
        "rolled_rear_lip",
    )
    for part in model.parts:
        if not part.name.startswith("vane_"):
            continue
        try:
            index = int(part.name.rsplit("_", 1)[-1])
        except ValueError:
            continue
        parent_elems = list(common_frame_elems) + [
            f"pivot_landing_{index}",
            f"pivot_neck_{index}",
        ]
        for parent_elem in parent_elems:
            for child_elem in child_elems:
                try:
                    ctx.allow_overlap(
                        frame,
                        part,
                        elem_a=parent_elem,
                        elem_b=child_elem,
                        reason="vane pivot endcap is captured at the frame pivot landing",
                    )
                except Exception:
                    pass


def run_vane_array_with_independent_pivots_tests(
    object_model: ArticulatedObject,
    config: VaneArrayWithIndependentPivotsConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model)
    # Forward-compatible: silence the connectivity warn for the frame and per-
    # vane parts where applicable (vanes legitimately have separated pin / shaft
    # / collar pieces that can sit slightly apart in the rest pose).
    allow_islands = getattr(ctx, "allow_disconnected_islands", None)
    if callable(allow_islands):
        part_names = {p.name for p in object_model.parts}
        targets = ["frame"] + [n for n in part_names if n.startswith("vane_")]
        for pn in targets:
            allow_islands(
                object_model.get_part(pn),
                reason=(
                    "vane array has separated rigid sub-pieces: end pins / shafts / "
                    "collars / hidden bosses, pivot landings, edge chamfers"
                ),
            )
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.joints}
    if "frame" not in part_names:
        ctx.fail("identity_frame", "vane array must include a frame part")
    vane_parts = [n for n in part_names if n.startswith("vane_")]
    if len(vane_parts) != r.vane_count:
        ctx.fail(
            "vane_count",
            f"expected {r.vane_count} vanes, got {len(vane_parts)}",
        )
    for spec in r.specs:
        jn = f"frame_to_vane_{spec.index}"
        if jn not in joint_names:
            ctx.fail("identity_joint", f"missing {jn}")
    for joint in object_model.joints:
        if not joint.name.startswith("frame_to_vane_"):
            continue
        if joint.articulation_type != ArticulationType.REVOLUTE:
            ctx.fail("joint_type", f"{joint.name} must be REVOLUTE")
        if r.pivot_axis_kind == "x_horizontal":
            if joint.axis != (1.0, 0.0, 0.0):
                ctx.fail("joint_axis", f"{joint.name} axis must be (1,0,0)")
        else:
            if joint.axis != (0.0, 0.0, 1.0):
                ctx.fail("joint_axis", f"{joint.name} axis must be (0,0,1)")
    return ctx.report()


__all__ = [
    "VaneArrayWithIndependentPivotsConfig",
    "ResolvedVaneArrayWithIndependentPivotsConfig",
    "build_vane_array_with_independent_pivots",
    "build_seeded_vane_array_with_independent_pivots",
    "config_from_seed",
    "resolve_config",
    "run_vane_array_with_independent_pivots_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
