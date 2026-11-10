# SPDX-License-Identifier: Apache-2.0

"""Wire-strippers modular template (0611 / pilers_wire_strippers).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/pilers_wire_strippers.md`` and
the ``pictureX/0611/Pilers_wire_strippers`` 5-star pool (1 origin_anchor
``compact_wire_strippers_001`` + 9 single-axis fork variants).

Structure (pattern ``mixed``):

* baseline 4-part / 3-joint chain: ``pivot`` (root) + ``arm_0`` + ``arm_1`` +
  ``spring``. ``pivot_to_arm_0`` REVOLUTE (pivot -> arm_0, axis ``(0,0,-1)``) +
  ``pivot_to_arm_1`` REVOLUTE (pivot -> arm_1, axis ``(0,0,+1)``) open the
  handles + jaws. ``arm_0_to_spring`` REVOLUTE (arm_0 -> spring, axis +Z) rocks
  the compression/torsion coil.
* ``return_lock = handle_lock`` swaps a 5-part chain by appending a
  ``handle_lock`` part + ``arm_0_to_handle_lock`` REVOLUTE.

Slots:

* ``secondary_module`` (4): baseline_cutter_plate / terminal_crimper /
  bolt_shear / cable_cutter. Swap arm-internal cut loops + cutter_plate
  polyline.
* ``stripper_mechanism`` (3): standard_plier / compound_automatic /
  self_adjusting_parallel. Swap ``_metal_arm`` jaw polyline family.
* ``return_lock`` (3): spring_coil (baseline) / torsion_return / handle_lock.
  Only handle_lock changes chain topology (+1 part +1 joint).
* ``gauge_count`` (4): 5 / 6 (baseline) / 7 / 9. Uniform Y layout with
  radius taper. Each arm receives the same layout.

``palette_style`` (6): pure material rgba axis; does not enter slot_choices.

The central rivet is captured-pin geometry (shaft through the two half-lap
hubs) so its joints omit ``MatingContract`` and are guarded by broad
``allow_overlap(pivot, arm_0)`` and ``allow_overlap(pivot, arm_1)``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enum axes
# ---------------------------------------------------------------------------
SecondaryModule = Literal["baseline_cutter_plate", "terminal_crimper", "bolt_shear", "cable_cutter"]
StripperMechanism = Literal["standard_plier", "compound_automatic", "self_adjusting_parallel"]
ReturnLock = Literal["spring_coil", "torsion_return", "handle_lock"]
GaugeCount = Literal[5, 6, 7, 9]
PaletteStyle = Literal[
    "black_yellow_pro",
    "red_black",
    "blue_yellow",
    "all_black",
    "orange_black",
    "chrome_natural",
]

SECONDARY_MODULES: tuple[SecondaryModule, ...] = (
    "baseline_cutter_plate",
    "terminal_crimper",
    "bolt_shear",
    "cable_cutter",
)
STRIPPER_MECHANISMS: tuple[StripperMechanism, ...] = (
    "standard_plier",
    "compound_automatic",
    "self_adjusting_parallel",
)
RETURN_LOCKS: tuple[ReturnLock, ...] = (
    "spring_coil",
    "torsion_return",
    "handle_lock",
)
GAUGE_COUNTS: tuple[GaugeCount, ...] = (5, 6, 7, 9)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "black_yellow_pro",
    "red_black",
    "blue_yellow",
    "all_black",
    "orange_black",
    "chrome_natural",
)

# Baseline plate thickness / pivot bore (source: P0 model.py L22-23).
PLATE_THICKNESS = 0.0030
PIVOT_HOLE_RADIUS = 0.0042

# ---------------------------------------------------------------------------
# Palettes (spec §palette; each provides 5 material rgba keys).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "black_yellow_pro": {
        "metal_frame": (0.035, 0.040, 0.045, 1.0),
        "pivot_metal": (0.82, 0.84, 0.83, 1.0),
        "bright_metal": (0.68, 0.70, 0.69, 1.0),
        "grip_shell": (0.018, 0.020, 0.022, 1.0),
        "grip_insert": (1.0, 0.76, 0.015, 1.0),
    },
    "red_black": {
        "metal_frame": (0.10, 0.10, 0.11, 1.0),
        "pivot_metal": (0.80, 0.82, 0.82, 1.0),
        "bright_metal": (0.65, 0.66, 0.66, 1.0),
        "grip_shell": (0.85, 0.08, 0.06, 1.0),
        "grip_insert": (0.10, 0.10, 0.10, 1.0),
    },
    "blue_yellow": {
        "metal_frame": (0.16, 0.18, 0.20, 1.0),
        "pivot_metal": (0.85, 0.86, 0.86, 1.0),
        "bright_metal": (0.72, 0.74, 0.74, 1.0),
        "grip_shell": (0.10, 0.20, 0.55, 1.0),
        "grip_insert": (1.0, 0.78, 0.10, 1.0),
    },
    "all_black": {
        "metal_frame": (0.05, 0.05, 0.06, 1.0),
        "pivot_metal": (0.55, 0.56, 0.56, 1.0),
        "bright_metal": (0.42, 0.42, 0.42, 1.0),
        "grip_shell": (0.05, 0.05, 0.06, 1.0),
        "grip_insert": (0.20, 0.20, 0.22, 1.0),
    },
    "orange_black": {
        "metal_frame": (0.10, 0.10, 0.11, 1.0),
        "pivot_metal": (0.82, 0.84, 0.83, 1.0),
        "bright_metal": (0.68, 0.70, 0.69, 1.0),
        "grip_shell": (0.95, 0.42, 0.05, 1.0),
        "grip_insert": (0.08, 0.08, 0.08, 1.0),
    },
    "chrome_natural": {
        "metal_frame": (0.80, 0.82, 0.85, 1.0),
        "pivot_metal": (0.90, 0.92, 0.93, 1.0),
        "bright_metal": (0.88, 0.90, 0.92, 1.0),
        "grip_shell": (0.35, 0.36, 0.38, 1.0),
        "grip_insert": (0.60, 0.62, 0.64, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PilersWireStrippersConfig:
    secondary_module: SecondaryModule | None = None
    stripper_mechanism: StripperMechanism | None = None
    return_lock: ReturnLock | None = None
    gauge_count: GaugeCount | None = None
    palette_style: PaletteStyle = "black_yellow_pro"
    overall_len_scale: float = 1.0
    jaw_len_scale: float = 1.0
    grip_girth_scale: float = 1.0
    open_angle_scale: float = 1.0
    name: str = "pilers_wire_strippers"


@dataclass(frozen=True)
class ResolvedConfig:
    secondary_module: SecondaryModule
    stripper_mechanism: StripperMechanism
    return_lock: ReturnLock
    gauge_count: GaugeCount
    palette_style: PaletteStyle
    overall_len_scale: float
    jaw_len_scale: float
    grip_girth_scale: float
    open_upper: float
    open_lower: float
    name: str

    @property
    def has_handle_lock(self) -> bool:
        return self.return_lock == "handle_lock"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> PilersWireStrippersConfig:
    rng = random.Random(seed)
    sec = rng.choices(SECONDARY_MODULES, weights=[5, 3, 3, 3], k=1)[0]
    mech = rng.choices(STRIPPER_MECHANISMS, weights=[5, 3, 3], k=1)[0]
    ret = rng.choices(RETURN_LOCKS, weights=[5, 3, 2], k=1)[0]
    gauge = rng.choices(GAUGE_COUNTS, weights=[3, 5, 3, 2], k=1)[0]
    return PilersWireStrippersConfig(
        secondary_module=sec,
        stripper_mechanism=mech,
        return_lock=ret,
        gauge_count=gauge,
        palette_style=rng.choice(PALETTE_STYLES),
        overall_len_scale=round(rng.uniform(0.92, 1.10), 4),
        jaw_len_scale=round(rng.uniform(0.94, 1.08), 4),
        grip_girth_scale=round(rng.uniform(0.94, 1.08), 4),
        open_angle_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_pilers_wire_strippers_{seed}",
    )


def resolve_config(config: PilersWireStrippersConfig | None = None) -> ResolvedConfig:
    cfg = config or PilersWireStrippersConfig()
    sec = _pick(cfg.secondary_module, SECONDARY_MODULES)
    mech = _pick(cfg.stripper_mechanism, STRIPPER_MECHANISMS)
    ret = _pick(cfg.return_lock, RETURN_LOCKS)
    gauge = _pick(cfg.gauge_count, GAUGE_COUNTS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    overall = _clamp(cfg.overall_len_scale, 0.92, 1.10)
    jaw_len = _clamp(cfg.jaw_len_scale, 0.94, 1.08)
    grip_girth = _clamp(cfg.grip_girth_scale, 0.94, 1.08)
    open_scale = _clamp(cfg.open_angle_scale, 0.85, 1.15)

    upper = _clamp(math.radians(18.0) * open_scale, 0.18, 0.42)
    lower = _clamp(math.radians(-2.0) * open_scale, -0.10, -0.010)

    return ResolvedConfig(
        secondary_module=sec,
        stripper_mechanism=mech,
        return_lock=ret,
        gauge_count=gauge,
        palette_style=palette,
        overall_len_scale=overall,
        jaw_len_scale=jaw_len,
        grip_girth_scale=grip_girth,
        open_upper=upper,
        open_lower=lower,
        name=cfg.name or "pilers_wire_strippers",
    )


def with_overrides(
    config: PilersWireStrippersConfig, **kwargs: object
) -> PilersWireStrippersConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: PilersWireStrippersConfig | ResolvedConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("secondary_module", r.secondary_module),
        ("stripper_mechanism", r.stripper_mechanism),
        ("return_lock", r.return_lock),
        ("gauge_count", str(r.gauge_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers.
# ---------------------------------------------------------------------------
def _poly_solid(points: list[tuple[float, float]], thickness: float, z_center: float):
    return (
        cq.Workplane("XY")
        .polyline(points)
        .close()
        .extrude(thickness)
        .translate((0.0, 0.0, z_center - thickness / 2.0))
    )


def _circle_solid(
    radius: float,
    thickness: float,
    z_center: float,
    x: float = 0.0,
    y: float = 0.0,
):
    return (
        cq.Workplane("XY")
        .center(x, y)
        .circle(radius)
        .extrude(thickness)
        .translate((0.0, 0.0, z_center - thickness / 2.0))
    )


def _gauge_layout(count: int) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Uniform Y layout with radius taper. Source: P0 L24-25 (6-hole)."""
    if count == 5:
        y0, yn = 0.040, 0.084
    elif count == 9:
        y0, yn = 0.034, 0.094
    else:
        y0, yn = 0.037, 0.086
    r_max, r_min = 0.00255, 0.00128
    ys = tuple(y0 + i * (yn - y0) / (count - 1) for i in range(count))
    rs = tuple(r_max - i * (r_max - r_min) / (count - 1) for i in range(count))
    return ys, rs


def _handle_polyline(side: int, r: ResolvedConfig) -> list[tuple[float, float]]:
    ol = r.overall_len_scale
    gw = r.grip_girth_scale

    def p(x: float, y: float) -> tuple[float, float]:
        return (side * x * gw, y * ol)

    return [
        p(0.001, -0.006),
        p(-0.014, -0.004),
        p(-0.026, -0.035),
        p(-0.047, -0.139),
        p(-0.043, -0.151),
        p(-0.034, -0.157),
        p(-0.025, -0.149),
        p(-0.012, -0.051),
        p(0.005, -0.012),
    ]


def _jaw_polyline(side: int, r: ResolvedConfig) -> list[tuple[float, float]]:
    jl = r.jaw_len_scale
    mech = r.stripper_mechanism

    def p(x: float, y: float) -> tuple[float, float]:
        return (side * x, y * jl)

    if mech == "standard_plier":
        return [
            p(-0.0020, 0.004),
            p(0.0145, 0.004),
            p(0.0180, 0.025),
            p(0.0130, 0.084),
            p(0.0105, 0.092),
            p(0.0063, 0.098),
            p(0.0010, 0.095),
            p(0.00065, 0.024),
        ]
    if mech == "compound_automatic":
        # Wider mid-jaw with an offset toggle boss.
        return [
            p(-0.0020, 0.004),
            p(0.0175, 0.004),
            p(0.0215, 0.026),
            p(0.0210, 0.055),  # toggle boss
            p(0.0160, 0.084),
            p(0.0125, 0.092),
            p(0.0075, 0.098),
            p(0.0015, 0.095),
            p(0.00065, 0.024),
        ]
    # self_adjusting_parallel: flat tip + wider jaw.
    return [
        p(-0.0020, 0.004),
        p(0.0185, 0.004),
        p(0.0220, 0.025),
        p(0.0180, 0.070),
        p(0.0175, 0.090),
        p(0.0140, 0.098),
        p(0.0070, 0.098),
        p(0.0015, 0.095),
        p(0.00065, 0.024),
    ]


def _metal_arm_solid(side: int, z_center: float, r: ResolvedConfig):
    pivot = _circle_solid(0.0162, PLATE_THICKNESS, z_center)
    handle = _poly_solid(_handle_polyline(side, r), PLATE_THICKNESS, z_center)
    jaw = _poly_solid(_jaw_polyline(side, r), PLATE_THICKNESS, z_center)
    result = pivot.union(handle).union(jaw)

    # Real pivot bore.
    result = result.cut(_circle_solid(PIVOT_HOLE_RADIUS, 0.007, z_center))

    # Six-position (parameterized) stripping apertures along the jaw seam.
    ys, rs = _gauge_layout(r.gauge_count)
    for y, radius in zip(ys, rs):
        result = result.cut(_circle_solid(radius, 0.007, z_center, x=0.0, y=y * r.jaw_len_scale))

    # Two larger near-pivot crimp nests (baseline).
    for y, radius in ((0.019, 0.0034), (0.028, 0.0028)):
        result = result.cut(_circle_solid(radius, 0.007, z_center, x=0.0, y=y * r.jaw_len_scale))

    # Slot A: terminal_crimper adds 4 die cavities on the outer jaw face.
    if r.secondary_module == "terminal_crimper":
        die_ys = (0.045, 0.058, 0.071, 0.084)
        die_rs = (0.0036, 0.0030, 0.0024, 0.0018)
        for y, radius in zip(die_ys, die_rs):
            # Cut on the outer side of the seam so it does not conflict with
            # gauge holes at x=0. Offset toward the arm's x direction.
            result = result.cut(
                _circle_solid(radius, 0.007, z_center, x=side * 0.0060, y=y * r.jaw_len_scale)
            )
    return result


def _grip_shapes(side: int, z_center: float, r: ResolvedConfig):
    ol = r.overall_len_scale
    gw = r.grip_girth_scale

    def p(x: float, y: float) -> tuple[float, float]:
        return (side * x * gw, y * ol)

    outer_pts = [
        p(-0.015, -0.029),
        p(-0.030, -0.027),
        p(-0.038, -0.050),
        p(-0.058, -0.136),
        p(-0.056, -0.149),
        p(-0.047, -0.160),
        p(-0.038, -0.161),
        p(-0.030, -0.150),
        p(-0.016, -0.063),
    ]
    insert_pts = [
        p(-0.019, -0.035),
        p(-0.027, -0.034),
        p(-0.033, -0.054),
        p(-0.051, -0.135),
        p(-0.049, -0.146),
        p(-0.044, -0.152),
        p(-0.039, -0.151),
        p(-0.034, -0.142),
        p(-0.022, -0.061),
    ]
    outer = _poly_solid(outer_pts, 0.0110, z_center)
    insert = _poly_solid(insert_pts, 0.0114, z_center)
    black_border = outer.cut(insert)
    return black_border, insert


def _cutter_plate(side: int, z_center: float, r: ResolvedConfig):
    def p(x: float, y: float) -> tuple[float, float]:
        return (side * x, y)

    sec = r.secondary_module
    if sec == "cable_cutter":
        # Wider cutter plate with a V-notch cable-cut mouth. Baseline width
        # was ~0.014, cable_cutter targets > 0.020.
        pts = [
            p(-0.002, -0.010),
            p(0.021, -0.008),
            p(0.024, 0.008),
            p(0.021, 0.031),
            p(0.010, 0.035),
            p(0.001, 0.030),
            p(0.001, 0.006),
        ]
        plate = _poly_solid(pts, 0.0010, z_center)
        # V-notch: two circle cuts widening the crimp/cut mouth.
        plate = plate.cut(_circle_solid(0.0032, 0.003, z_center, x=side * 0.012, y=0.020))
    else:
        pts = [
            p(-0.001, -0.010),
            p(0.011, -0.008),
            p(0.014, 0.008),
            p(0.011, 0.031),
            p(0.004, 0.035),
            p(0.001, 0.030),
            p(0.001, 0.006),
        ]
        plate = _poly_solid(pts, 0.0008, z_center)
    for y, radius in ((0.019, 0.0034), (0.028, 0.0028)):
        plate = plate.cut(_circle_solid(radius, 0.002, z_center, x=0.0, y=y))
    return plate


def _bolt_shear_plate(side: int, z_center: float):
    """Small plate with 2 shear notches at Y=0.012/0.016."""

    def p(x: float, y: float) -> tuple[float, float]:
        return (side * x, y)

    pts = [
        p(-0.001, 0.010),
        p(0.006, 0.010),
        p(0.006, 0.020),
        p(-0.001, 0.020),
    ]
    plate = _poly_solid(pts, 0.0010, z_center)
    for y, radius in ((0.012, 0.0016), (0.016, 0.0020)):
        plate = plate.cut(_circle_solid(radius, 0.003, z_center, x=side * 0.003, y=y))
    return plate


def _spring_coil_geometry(coils: int = 9) -> object:
    points: list[tuple[float, float, float]] = [(0.0, 0.0, 0.0), (0.002, 0.0, 0.0)]
    samples = 108
    radius = 0.0033
    for i in range(samples + 1):
        u = i / samples
        theta = coils * 2.0 * math.pi * u
        points.append(
            (
                0.002 + 0.032 * u,
                radius * (math.cos(theta) - 1.0),
                radius * math.sin(theta),
            )
        )
    points.extend([(0.036, 0.0, 0.0), (0.038, 0.0, 0.0)])
    return tube_from_spline_points(
        points,
        radius=0.00085,
        samples_per_segment=2,
        radial_segments=10,
        cap_ends=True,
    )


def _torsion_coil_geometry() -> object:
    """Tight helical torsion coil wrapping the x axis."""
    points: list[tuple[float, float, float]] = []
    coils = 4
    samples = 96
    radius = 0.0028
    length = 0.020
    for i in range(samples + 1):
        u = i / samples
        theta = coils * 2.0 * math.pi * u
        x = 0.002 + length * u
        y = radius * (math.cos(theta) - 1.0)
        z = radius * math.sin(theta)
        points.append((x, y, z))
    # Short tail arms.
    points.append((points[-1][0] + 0.004, points[-1][1], points[-1][2]))
    points.insert(0, (points[0][0] - 0.004, points[0][1], points[0][2]))
    return tube_from_spline_points(
        points,
        radius=0.00090,
        samples_per_segment=2,
        radial_segments=10,
        cap_ends=True,
    )


def _handle_lock_lever():
    pts = [
        (-0.001, -0.006),
        (0.010, -0.006),
        (0.014, -0.010),
        (0.014, -0.024),
        (0.008, -0.028),
        (-0.001, -0.028),
    ]
    lever = _poly_solid(pts, 0.0028, 0.0)
    # Pivot boss + small hook lip.
    boss = _circle_solid(0.0028, 0.0028, 0.0, x=0.0, y=-0.006)
    return lever.union(boss)


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def build_pilers_wire_strippers(
    config: PilersWireStrippersConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"pws_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    # ------------------------------------------------------------------
    # pivot (root): shared rivet body.
    # ------------------------------------------------------------------
    pivot = model.part(
        "pivot",
        meta={"role": "shared_pivot"},
    )
    # Pivot shaft radius must exceed PIVOT_HOLE_RADIUS so it physically
    # touches both arm hubs (bore=0.0042); a snug interference guarantees
    # zero-gap capture and satisfies the isolated-part contact gate.
    pivot.visual(
        Cylinder(radius=0.0046, length=0.0110),
        material=mats["pivot_metal"],
        name="pivot_shaft", material_class_id="metal.stainless_matte",
    )
    pivot.visual(
        Cylinder(radius=0.0083, length=0.0018),
        origin=Origin(xyz=(0.0, 0.0, -0.0046)),
        material=mats["pivot_metal"],
        name="rear_rivet_head", material_class_id="metal.stainless_matte",
    )
    pivot.visual(
        Cylinder(radius=0.0083, length=0.0018),
        origin=Origin(xyz=(0.0, 0.0, 0.0047)),
        material=mats["pivot_metal"],
        name="front_rivet_head", material_class_id="metal.stainless_matte",
    )

    # ------------------------------------------------------------------
    # arm_0 (-x handle, +x jaw), arm_1 (+x handle, -x jaw).
    # ------------------------------------------------------------------
    arm_0 = model.part(
        "arm_0",
        meta={
            "handle_side": "negative_x",
            "jaw_side": "positive_x",
            "gauge_hole_count": r.gauge_count,
            "insulated_grip": True,
        },
    )
    arm_1 = model.part(
        "arm_1",
        meta={
            "handle_side": "positive_x",
            "jaw_side": "negative_x",
            "gauge_hole_count": r.gauge_count,
            "insulated_grip": True,
        },
    )

    ys_layout, _ = _gauge_layout(r.gauge_count)

    arm_specs = (
        (arm_0, 1, -0.0017),
        (arm_1, -1, 0.0017),
    )
    for index, (arm, side, z_center) in enumerate(arm_specs):
        arm.visual(
            mesh_from_cadquery(
                _metal_arm_solid(side, z_center, r),
                f"arm_{index}_metal",
                tolerance=0.0003,
            ),
            material=mats["metal_frame"],
            name="metal_frame", material_class_id=("metal.paint_coated" if config.palette_style in {"black_yellow_pro", "red_black", "blue_yellow", "all_black", "orange_black"} else "metal.chrome_polished"),
        )
        black_grip, yellow_insert = _grip_shapes(side, z_center, r)
        arm.visual(
            mesh_from_cadquery(
                black_grip,
                f"arm_{index}_grip_border",
                tolerance=0.0003,
            ),
            material=mats["grip_shell"],
            name="grip_shell", material_class_id="plastic.opaque_glossy_molded",
        )
        arm.visual(
            mesh_from_cadquery(
                yellow_insert,
                f"arm_{index}_grip_insert",
                tolerance=0.0003,
            ),
            material=mats["grip_insert"],
            name="grip_insert", material_class_id="rubber.smooth_plain",
        )

        # Small gauge markers so the calibrated notches read visually.
        marker_z = z_center + PLATE_THICKNESS / 2.0 + 0.00012
        for marker_index, y in enumerate(ys_layout):
            arm.visual(
                Box((0.0014, 0.0026, 0.00035)),
                origin=Origin(xyz=(side * 0.0103, y * r.jaw_len_scale, marker_z)),
                material=mats["bright_metal"],
                name=f"gauge_mark_{marker_index}", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )

    # Cutter plate + secondary module on arm_1 front face.
    arm_1.visual(
        mesh_from_cadquery(
            _cutter_plate(-1, 0.00335, r),
            "front_cutter_plate",
            tolerance=0.0003,
        ),
        material=mats["bright_metal"],
        name="cutter_plate", material_class_id="metal.stainless_matte",
    )
    if r.secondary_module == "bolt_shear":
        arm_0.visual(
            mesh_from_cadquery(
                _bolt_shear_plate(1, -0.0017 + PLATE_THICKNESS / 2.0 + 0.00040),
                "bolt_shear_plate_0",
                tolerance=0.0003,
            ),
            material=mats["bright_metal"],
            name="bolt_shear_plate", material_class_id="metal.stainless_matte",
        )
        arm_1.visual(
            mesh_from_cadquery(
                _bolt_shear_plate(-1, 0.0017 - PLATE_THICKNESS / 2.0 - 0.00040),
                "bolt_shear_plate_1",
                tolerance=0.0003,
            ),
            material=mats["bright_metal"],
            name="bolt_shear_plate", material_class_id="metal.stainless_matte",
        )

    # Spring seats.
    arm_0.visual(
        Cylinder(radius=0.0022, length=0.0060),
        origin=Origin(xyz=(-0.018, -0.028 * r.overall_len_scale, 0.0065)),
        material=mats["metal_frame"],
        name="spring_seat", material_class_id=("metal.paint_coated" if config.palette_style in {"black_yellow_pro", "red_black", "blue_yellow", "all_black", "orange_black"} else "metal.chrome_polished"),
    )
    arm_1.visual(
        Cylinder(radius=0.0022, length=0.0032),
        origin=Origin(xyz=(0.020, -0.028 * r.overall_len_scale, 0.0084)),
        material=mats["metal_frame"],
        name="spring_seat", material_class_id=("metal.paint_coated" if config.palette_style in {"black_yellow_pro", "red_black", "blue_yellow", "all_black", "orange_black"} else "metal.chrome_polished"),
    )

    # Joints: pivot -> arm_0 / arm_1 (symmetric axes about Z).
    model.articulation(
        "pivot_to_arm_0",
        ArticulationType.REVOLUTE,
        parent=pivot,
        child=arm_0,
        origin=Origin(),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(
            effort=85.0,
            velocity=2.5,
            lower=r.open_lower,
            upper=r.open_upper,
        ),
        meta={"positive_motion": "negative-x handle and positive-x jaw open outward"},
    )
    model.articulation(
        "pivot_to_arm_1",
        ArticulationType.REVOLUTE,
        parent=pivot,
        child=arm_1,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=85.0,
            velocity=2.5,
            lower=r.open_lower,
            upper=r.open_upper,
        ),
        meta={"positive_motion": "positive-x handle and negative-x jaw open outward"},
    )

    # Spring part.
    spring = model.part(
        "spring",
        meta={"role": "handle_return_spring", "return_lock": r.return_lock},
    )
    if r.return_lock == "torsion_return":
        spring.visual(
            mesh_from_geometry(_torsion_coil_geometry(), "return_spring"),
            material=mats["metal_frame"],
            name="coil", material_class_id=("metal.paint_coated" if config.palette_style in {"black_yellow_pro", "red_black", "blue_yellow", "all_black", "orange_black"} else "metal.chrome_polished"),
        )
    else:
        spring.visual(
            mesh_from_geometry(_spring_coil_geometry(), "return_spring"),
            material=mats["metal_frame"],
            name="coil", material_class_id=("metal.paint_coated" if config.palette_style in {"black_yellow_pro", "red_black", "blue_yellow", "all_black", "orange_black"} else "metal.chrome_polished"),
        )
    model.articulation(
        "arm_0_to_spring",
        ArticulationType.REVOLUTE,
        parent=arm_0,
        child=spring,
        origin=Origin(xyz=(-0.018, -0.028 * r.overall_len_scale, 0.0084)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=4.0,
            velocity=3.0,
            lower=math.radians(-7.0),
            upper=math.radians(7.0),
        ),
        meta={"positive_motion": "spring body rocks slightly at its captured end"},
    )

    # Optional handle_lock chain (return_lock=handle_lock).
    if r.has_handle_lock:
        handle_lock = model.part("handle_lock", meta={"role": "handle_lock_latch"})
        handle_lock.visual(
            mesh_from_cadquery(_handle_lock_lever(), "lock_lever", tolerance=0.0003),
            material=mats["bright_metal"],
            name="lock_lever", material_class_id="metal.stainless_matte",
        )
        model.articulation(
            "arm_0_to_handle_lock",
            ArticulationType.REVOLUTE,
            parent=arm_0,
            child=handle_lock,
            # Sit the lock lever directly on the arm_0 stamped face
            # (arm_0 top surface ~ -0.0017 + 0.0015 = -0.0002 in world z).
            origin=Origin(xyz=(-0.020, -0.060 * r.overall_len_scale, 0.0005)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=1.5,
                velocity=3.0,
                lower=-0.35,
                upper=0.60,
            ),
            meta={"positive_motion": "lock lever swings across the handle gap"},
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pilers_wire_strippers(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_pilers_wire_strippers(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_pilers_wire_strippers_tests(
    object_model: ArticulatedObject,
    config: PilersWireStrippersConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    pivot = object_model.get_part("pivot")
    arm_0 = object_model.get_part("arm_0")
    arm_1 = object_model.get_part("arm_1")
    spring = object_model.get_part("spring")
    j0 = object_model.get_articulation("pivot_to_arm_0")
    j1 = object_model.get_articulation("pivot_to_arm_1")
    js = object_model.get_articulation("arm_0_to_spring")

    # Captured-pin allowances.
    ctx.allow_overlap(
        pivot,
        arm_0,
        reason="rivet shaft captured through the two half-lap hubs (arm_0).",
    )
    ctx.allow_overlap(
        pivot,
        arm_1,
        reason="rivet shaft captured through the two half-lap hubs (arm_1).",
    )
    ctx.allow_overlap(
        arm_0,
        arm_1,
        reason="the two stamped halves overlap through the shared pivot lap.",
    )
    ctx.allow_overlap(
        spring,
        arm_0,
        elem_a="coil",
        elem_b="spring_seat",
        reason="the return spring tang is captured in the rear arm's support stud.",
    )
    ctx.allow_overlap(
        spring,
        arm_1,
        elem_a="coil",
        elem_b="spring_seat",
        reason="the compression spring free tang seats against the opposite stud.",
    )

    if r.has_handle_lock:
        handle_lock = object_model.get_part("handle_lock")
        jl = object_model.get_articulation("arm_0_to_handle_lock")
        ctx.allow_overlap(
            arm_0,
            handle_lock,
            reason="the lock lever pin is captured against the arm's handle face.",
        )
        ctx.check(
            "handle_lock topology has extra part and joint",
            len(object_model.parts) == 5 and len(object_model.articulations) == 4,
            details=(f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}"),
        )
        ctx.check(
            "handle_lock part has lock_lever visual",
            any(v.name == "lock_lever" for v in handle_lock.visuals),
            details=f"visuals={[v.name for v in handle_lock.visuals]}",
        )
        ctx.check(
            "arm_0_to_handle_lock is bounded REVOLUTE about +Z",
            jl.articulation_type == ArticulationType.REVOLUTE and jl.motion_limits is not None,
            details=f"limits={jl.motion_limits}",
        )
    else:
        ctx.check(
            "baseline topology is 4-part / 3-joint",
            len(object_model.parts) == 4 and len(object_model.articulations) == 3,
            details=(f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}"),
        )

    # Slot D: gauge_count parameterisation.
    ctx.check(
        "gauge_hole_count metadata matches gauge_count slot",
        arm_0.meta.get("gauge_hole_count") == r.gauge_count
        and arm_1.meta.get("gauge_hole_count") == r.gauge_count,
        details=f"arm_0={arm_0.meta}, arm_1={arm_1.meta}",
    )
    gauge_marks_0 = [v for v in arm_0.visuals if v.name.startswith("gauge_mark_")]
    ctx.check(
        "arm_0 has exactly gauge_count gauge_mark visuals",
        len(gauge_marks_0) == r.gauge_count,
        details=f"count={len(gauge_marks_0)}",
    )

    # Central pivot joint sanity.
    for j in (j0, j1):
        lm = j.motion_limits
        ctx.check(
            f"{j.name} is a bounded REVOLUTE",
            j.articulation_type == ArticulationType.REVOLUTE
            and lm is not None
            and lm.lower < 0.0 < lm.upper,
            details=f"limits={lm}",
        )
    ctx.check(
        "spring joint is bounded REVOLUTE",
        js.articulation_type == ArticulationType.REVOLUTE and js.motion_limits is not None,
        details=f"limits={js.motion_limits}",
    )

    # Pivot vs arms captured-pin.
    for arm in (arm_0, arm_1):
        ctx.expect_overlap(
            pivot,
            arm,
            axes="xy",
            elem_a="pivot_shaft",
            elem_b="metal_frame",
            min_overlap=0.006,
            name=f"{arm.name} surrounds pivot in plan",
        )

    # Slot A: cutter_plate width claim.
    cutter_aabb = ctx.part_element_world_aabb(arm_1, elem="cutter_plate")
    if cutter_aabb is not None:
        cutter_width = cutter_aabb[1][0] - cutter_aabb[0][0]
        if r.secondary_module == "cable_cutter":
            ctx.check(
                "cable_cutter has wide cutter_plate",
                cutter_width > 0.018,
                details=f"cutter_plate x-width={cutter_width:.4f}",
            )

    # Slot A: bolt_shear plate visible on both arms.
    if r.secondary_module == "bolt_shear":
        ctx.check(
            "bolt_shear adds shear plates on both arms",
            any(v.name == "bolt_shear_plate" for v in arm_0.visuals)
            and any(v.name == "bolt_shear_plate" for v in arm_1.visuals),
            details="expected bolt_shear_plate on arm_0 and arm_1",
        )

    # Kinematics: opening pose separates the two grip shells.
    arm_0_rest = ctx.part_element_world_aabb(arm_0, elem="grip_shell")
    arm_1_rest = ctx.part_element_world_aabb(arm_1, elem="grip_shell")
    with ctx.pose({j0: j0.motion_limits.upper, j1: j1.motion_limits.upper}):
        arm_0_open = ctx.part_element_world_aabb(arm_0, elem="grip_shell")
        arm_1_open = ctx.part_element_world_aabb(arm_1, elem="grip_shell")
        ctx.check(
            "both handles open outward",
            arm_0_rest is not None
            and arm_1_rest is not None
            and arm_0_open is not None
            and arm_1_open is not None
            and arm_0_open[0][0] < arm_0_rest[0][0] - 0.005
            and arm_1_open[1][0] > arm_1_rest[1][0] + 0.005,
            details=(
                f"arm_0 rest/open={arm_0_rest}/{arm_0_open}; "
                f"arm_1 rest/open={arm_1_rest}/{arm_1_open}"
            ),
        )

    # Spring rocking.
    spring_rest = ctx.part_element_world_aabb(spring, elem="coil")
    with ctx.pose({js: js.motion_limits.upper}):
        spring_rocked = ctx.part_element_world_aabb(spring, elem="coil")
        ctx.check(
            "spring rocks visibly",
            spring_rest is not None
            and spring_rocked is not None
            and (
                abs(spring_rocked[1][1] - spring_rest[1][1])
                + abs(spring_rocked[1][0] - spring_rest[1][0])
            )
            > 0.0005,
            details=f"rest={spring_rest}, rocked={spring_rocked}",
        )

    ctx.check(
        "slot_choices metadata is emitted",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
        details=f"meta slot_choices={object_model.meta.get('slot_choices')}",
    )

    return ctx.report()


__all__ = [
    "PilersWireStrippersConfig",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "with_overrides",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_pilers_wire_strippers",
    "build_seeded_pilers_wire_strippers",
    "run_pilers_wire_strippers_tests",
    "__modular__",
]
