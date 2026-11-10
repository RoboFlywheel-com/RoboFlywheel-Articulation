# SPDX-License-Identifier: Apache-2.0

"""Procedural modular template for ``tailor_s_dummy`` (Textiles_Fabric).

Implements the reviewed modular spec at
``articraft_template_authoring/specs_modular_v1/tailor_s_dummy.md``.

A headless, legless fabric-covered torso / dress form on an adjustable vertical
stand. The shared spine (telescoping pole + superellipse fabric torso + neck) is
module-local fixed structure; diversity comes from three source-backed slots plus
a sizing-dial multiplicity axis:

* Slot A ``base_support`` (① floor topology): tripod_radial (S1) /
  star_caster_rolling (S2) / round_cast_disc (V2 LatheGeometry disc).
* Slot B ``arms`` (①②): armless (S1) / static_wood_arms (S2 visuals) /
  articulated_posable_arms (V1 shoulder+elbow REVOLUTE).
* Slot C ``adjustment`` (②): sizing_dials (S1/V3/V4 CONTINUOUS thumbwheels,
  N∈[3,10] multiplicity) / fixed_pinnable (S2 no dials).

Always-present rotary hardware: clamp_knob (base collar, CONTINUOUS) and
top_knob (column neck, CONTINUOUS). Height adjustment: base ``base_to_column``
PRISMATIC (z). All joints are telescoping / captured-pin / ball-mount /
surface-seated thumbwheels — geometry that is not two axis-aligned faces in
contact, so they are grandfathered (no MatingContract) with element-scoped
``allow_overlap`` per AUTHORING §B.

Adopted sources (model.py:Lx-Ly):
  S1 rec_textiles_fabric__tailor_s_dummy__001…  (tripod, dials, torso, knobs)
  S2 rec_textiles_fabric__tailor_s_dummy__002…  (star-caster, static wood arms, clamp)
  V1 rec_tailor_s_dummy_var_arms_articulated     (shoulder+elbow REVOLUTE arms)
  V2 rec_tailor_s_dummy_var_base_round           (LatheGeometry cast-iron disc)
  V3/V4 …_dials_n6 / …_dials_n9                  (dial multiplicity seats)
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
    Box,
    Cylinder,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    Part,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True


BaseSupport = Literal["tripod_radial", "star_caster_rolling", "round_cast_disc"]
ArmStyle = Literal["armless", "static_wood_arms", "articulated_posable_arms"]
AdjustmentStyle = Literal["sizing_dials", "fixed_pinnable"]
MaterialStyle = Literal["neoprene_grey", "cream_canvas", "cast_iron_chrome"]

BASE_SUPPORTS: tuple[BaseSupport, ...] = (
    "tripod_radial",
    "star_caster_rolling",
    "round_cast_disc",
)
ARM_STYLES: tuple[ArmStyle, ...] = (
    "armless",
    "static_wood_arms",
    "articulated_posable_arms",
)
ADJUSTMENT_STYLES: tuple[AdjustmentStyle, ...] = ("sizing_dials", "fixed_pinnable")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "neoprene_grey",
    "cream_canvas",
    "cast_iron_chrome",
)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "neoprene_grey": {
        "fabric": (0.30, 0.27, 0.27, 1.0),
        "seam": (0.018, 0.016, 0.017, 1.0),
        "metal": (0.78, 0.76, 0.70, 1.0),
        "dark_metal": (0.08, 0.075, 0.07, 1.0),
        "brass": (0.70, 0.55, 0.32, 1.0),
        "wood": (0.22, 0.14, 0.08, 1.0),
        "rubber": (0.025, 0.024, 0.022, 1.0),
    },
    "cream_canvas": {
        "fabric": (0.78, 0.70, 0.55, 1.0),
        "seam": (0.47, 0.39, 0.27, 1.0),
        "metal": (0.35, 0.36, 0.38, 1.0),
        "dark_metal": (0.01, 0.011, 0.012, 1.0),
        "brass": (0.66, 0.52, 0.30, 1.0),
        "wood": (0.22, 0.14, 0.08, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
    },
    "cast_iron_chrome": {
        "fabric": (0.34, 0.32, 0.33, 1.0),
        "seam": (0.05, 0.05, 0.05, 1.0),
        "metal": (0.80, 0.81, 0.82, 1.0),
        "dark_metal": (0.13, 0.12, 0.11, 1.0),
        "brass": (0.76, 0.77, 0.79, 1.0),
        "wood": (0.25, 0.16, 0.09, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class TailorSDummyConfig:
    base_support: BaseSupport | None = None
    arms: ArmStyle | None = None
    adjustment: AdjustmentStyle | None = None
    material_style: MaterialStyle = "neoprene_grey"
    dial_count: int = 3
    torso_width_scale: float = 1.0
    base_radius_scale: float = 1.0
    height_travel: float = 0.24
    name: str = "reference_tailor_s_dummy"


@dataclass(frozen=True)
class ResolvedTailorSDummyConfig:
    base_support: BaseSupport
    arms: ArmStyle
    adjustment: AdjustmentStyle
    material_style: MaterialStyle
    dial_count: int
    torso_width_scale: float
    base_radius_scale: float
    height_travel: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _choice(value: str | None, choices: tuple[str, ...], fallback: str) -> str:
    return value if value in choices else fallback


def config_from_seed(seed: int) -> TailorSDummyConfig:
    """Deterministic procedural sampling. ``seed=0`` is not special-cased."""
    rng = random.Random(seed)
    base: BaseSupport = rng.choice(BASE_SUPPORTS)
    arms: ArmStyle = rng.choice(ARM_STYLES)
    adjustment: AdjustmentStyle = rng.choice(ADJUSTMENT_STYLES)
    material: MaterialStyle = rng.choice(MATERIAL_STYLES)

    # Dial multiplicity: small-N weighted (3-4 common, 8-10 rare). Resolved to
    # 0 when adjustment=fixed_pinnable in resolve_config.
    dial_count = rng.choices(
        (3, 4, 5, 6, 7, 8, 9, 10),
        weights=(6, 5, 4, 3, 2, 2, 1, 1),
        k=1,
    )[0]

    return TailorSDummyConfig(
        base_support=base,
        arms=arms,
        adjustment=adjustment,
        material_style=material,
        dial_count=dial_count,
        torso_width_scale=round(rng.uniform(0.90, 1.12), 4),
        base_radius_scale=round(rng.uniform(0.90, 1.15), 4),
        height_travel=round(rng.uniform(0.20, 0.26), 4),
        name=f"seeded_tailor_s_dummy_{seed}",
    )


def resolve_config(config: TailorSDummyConfig) -> ResolvedTailorSDummyConfig:
    base = _choice(config.base_support, BASE_SUPPORTS, "tripod_radial")
    arms = _choice(config.arms, ARM_STYLES, "armless")
    adjustment = _choice(config.adjustment, ADJUSTMENT_STYLES, "sizing_dials")
    material = _choice(config.material_style, MATERIAL_STYLES, "neoprene_grey")

    # Compatibility gating: dial count only meaningful with sizing_dials.
    if adjustment == "sizing_dials":
        dial_count = int(_clamp(config.dial_count, 3, 10))
    else:
        dial_count = 0

    return ResolvedTailorSDummyConfig(
        base_support=base,  # type: ignore[arg-type]
        arms=arms,  # type: ignore[arg-type]
        adjustment=adjustment,  # type: ignore[arg-type]
        material_style=material,  # type: ignore[arg-type]
        dial_count=dial_count,
        torso_width_scale=_clamp(config.torso_width_scale, 0.90, 1.12),
        base_radius_scale=_clamp(config.base_radius_scale, 0.90, 1.15),
        height_travel=_clamp(config.height_travel, 0.20, 0.26),
        name=str(config.name or "tailor_s_dummy"),
    )


def _dial_count_band(n: int) -> str:
    if n <= 0:
        return "n0"
    if n <= 4:
        return f"n{n}"
    if n <= 7:
        return "n5_7"
    return "n8_10"


def slot_choices_for_config(config: TailorSDummyConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("base_support", r.base_support),
        ("arms", r.arms),
        ("adjustment", r.adjustment),
        ("dial_count", _dial_count_band(r.dial_count)),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Shared torso geometry (adapted from S1 model.py:L23-L172, scalable width)
# --------------------------------------------------------------------------- #

_TORSO_SECTIONS_BASE = (
    # z, width, front depth (-Y), back depth (+Y), superellipse power
    (0.000, 0.340, 0.100, 0.088, 2.5),
    (0.110, 0.365, 0.112, 0.096, 2.6),
    (0.250, 0.292, 0.086, 0.083, 2.8),
    (0.390, 0.392, 0.138, 0.104, 2.4),
    (0.530, 0.440, 0.118, 0.102, 2.6),
    (0.610, 0.382, 0.096, 0.088, 2.8),
    (0.665, 0.210, 0.074, 0.068, 2.5),
    (0.720, 0.140, 0.058, 0.055, 2.4),
)

_TORSO_TOP_Z = _TORSO_SECTIONS_BASE[-1][0]
_SHOULDER_Z = 0.600


def _torso_sections(width_scale: float) -> tuple[tuple[float, float, float, float, float], ...]:
    return tuple(
        (z, w * width_scale, front * width_scale, back * width_scale, power)
        for (z, w, front, back, power) in _TORSO_SECTIONS_BASE
    )


def _sgn(value: float) -> float:
    return -1.0 if value < 0.0 else 1.0


def _section_at(sections, z: float) -> tuple[float, float, float, float]:
    if z <= sections[0][0]:
        _, w, front, back, p = sections[0]
        return w, front, back, p
    if z >= sections[-1][0]:
        _, w, front, back, p = sections[-1]
        return w, front, back, p
    for lower, upper in zip(sections[:-1], sections[1:]):
        zl, wl, fl, bl, pl = lower
        zu, wu, fu, bu, pu = upper
        if zl <= z <= zu:
            t = (z - zl) / (zu - zl)
            return (
                wl + (wu - wl) * t,
                fl + (fu - fl) * t,
                bl + (bu - bl) * t,
                pl + (pu - pl) * t,
            )
    _, w, front, back, p = sections[-1]
    return w, front, back, p


def _torso_surface(sections, theta: float, z: float) -> tuple[float, float, tuple[float, float, float]]:
    width, front_depth, back_depth, power = _section_at(sections, z)
    c = math.cos(theta)
    s = math.sin(theta)
    exp = 2.0 / power
    x = 0.5 * width * _sgn(c) * (abs(c) ** exp)
    depth = front_depth if s < 0.0 else back_depth
    y = depth * _sgn(s) * (abs(s) ** exp)
    nx = x / max(0.5 * width, 1e-6)
    ny = y / max(depth, 1e-6)
    length = math.hypot(nx, ny)
    if length < 1e-6:
        normal = (math.cos(theta), math.sin(theta), 0.0)
    else:
        normal = (nx / length, ny / length, 0.0)
    return x, y, normal


def _make_torso_mesh(sections) -> MeshGeometry:
    geom = MeshGeometry()
    segments = 72
    loops: list[list[int]] = []
    for z, width, front_depth, back_depth, power in sections:
        loop: list[int] = []
        exp = 2.0 / power
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            c = math.cos(theta)
            s = math.sin(theta)
            x = 0.5 * width * _sgn(c) * (abs(c) ** exp)
            depth = front_depth if s < 0.0 else back_depth
            y = depth * _sgn(s) * (abs(s) ** exp)
            loop.append(geom.add_vertex(x, y, z))
        loops.append(loop)
    for lower, upper in zip(loops[:-1], loops[1:]):
        for i in range(segments):
            j = (i + 1) % segments
            geom.add_face(lower[i], lower[j], upper[j])
            geom.add_face(lower[i], upper[j], upper[i])
    bottom_center = geom.add_vertex(0.0, 0.0, sections[0][0])
    top_center = geom.add_vertex(0.0, 0.0, sections[-1][0])
    for i in range(segments):
        j = (i + 1) % segments
        geom.add_face(bottom_center, loops[0][j], loops[0][i])
        geom.add_face(top_center, loops[-1][i], loops[-1][j])
    return geom


def _make_vertical_seam(sections, theta: float, z0: float, z1: float, *, width: float = 0.008) -> MeshGeometry:
    geom = MeshGeometry()
    samples = 24
    rings: list[list[int]] = []
    tangent = (-math.sin(theta), math.cos(theta), 0.0)
    for k in range(samples + 1):
        z = z0 + (z1 - z0) * k / samples
        x, y, normal = _torso_surface(sections, theta, z)
        outer = (x + normal[0] * 0.004, y + normal[1] * 0.004, z)
        inner = (x - normal[0] * 0.002, y - normal[1] * 0.002, z)
        ring = [
            geom.add_vertex(outer[0] - tangent[0] * width / 2, outer[1] - tangent[1] * width / 2, z),
            geom.add_vertex(outer[0] + tangent[0] * width / 2, outer[1] + tangent[1] * width / 2, z),
            geom.add_vertex(inner[0] + tangent[0] * width / 2, inner[1] + tangent[1] * width / 2, z),
            geom.add_vertex(inner[0] - tangent[0] * width / 2, inner[1] - tangent[1] * width / 2, z),
        ]
        rings.append(ring)
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(4):
            j = (i + 1) % 4
            geom.add_face(a[i], a[j], b[j])
            geom.add_face(a[i], b[j], b[i])
    for ring in (rings[0], rings[-1]):
        geom.add_face(ring[0], ring[1], ring[2])
        geom.add_face(ring[0], ring[2], ring[3])
    return geom


def _make_waist_band(sections, z: float, *, height: float = 0.006) -> MeshGeometry:
    geom = MeshGeometry()
    segments = 72
    rings: list[list[int]] = []
    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        x, y, normal = _torso_surface(sections, theta, z)
        outer = (x + normal[0] * 0.0035, y + normal[1] * 0.0035)
        inner = (x - normal[0] * 0.002, y - normal[1] * 0.002)
        rings.append(
            [
                geom.add_vertex(outer[0], outer[1], z - height / 2),
                geom.add_vertex(outer[0], outer[1], z + height / 2),
                geom.add_vertex(inner[0], inner[1], z + height / 2),
                geom.add_vertex(inner[0], inner[1], z - height / 2),
            ]
        )
    for i in range(segments):
        a = rings[i]
        b = rings[(i + 1) % segments]
        for j in range(4):
            n = (j + 1) % 4
            geom.add_face(a[j], b[j], b[n])
            geom.add_face(a[j], b[n], a[n])
    return geom


def _mesh(model: ArticulatedObject, geometry: object, name: str):
    if getattr(model, "assets", None) is not None:
        return mesh_from_geometry(geometry, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geometry, name)


# --------------------------------------------------------------------------- #
# Stand geometry constants (base pole hardware + torso mount)
# --------------------------------------------------------------------------- #

_SLEEVE_R = 0.018
_SLEEVE_Z0 = 0.020
_SLEEVE_Z1 = 0.580
_SLEEVE_CENTER = 0.5 * (_SLEEVE_Z0 + _SLEEVE_Z1)
_SLEEVE_LEN = _SLEEVE_Z1 - _SLEEVE_Z0
_COLLAR_Z = 0.600
_COLLAR_R = 0.030
_COLLAR_LEN = 0.046
# Torso column mounts above the collar top so the support_plate clears it.
_COLUMN_MOUNT_Z = 0.645
_INNER_POLE_LEN = 0.360


# --------------------------------------------------------------------------- #
# Slot A: base_support (① floor topology)
# --------------------------------------------------------------------------- #


def _emit_stand_sleeve(base: Part, r: ResolvedTailorSDummyConfig, m: dict) -> None:
    """Shared vertical pole hardware — the telescoping outer sleeve + clamp
    collar. Identical across all three floor topologies (S1 L192-L203)."""
    base.visual(
        Cylinder(radius=_SLEEVE_R, length=_SLEEVE_LEN),
        origin=Origin(xyz=(0.0, 0.0, _SLEEVE_CENTER)),
        material=m["metal"],
        name="outer_sleeve", material_class_id=("metal.chrome_polished" if r.material_style == "cast_iron_chrome" else "metal.stainless_matte"),
    )
    base.visual(
        Cylinder(radius=_COLLAR_R, length=_COLLAR_LEN),
        origin=Origin(xyz=(0.0, 0.0, _COLLAR_Z)),
        material=m["dark_metal"],
        name="height_collar", material_class_id=("metal.cast_iron_bare" if r.material_style == "cast_iron_chrome" else "metal.blackened_gunmetal"),
    )


def _build_tripod_base(base: Part, r: ResolvedTailorSDummyConfig, m: dict) -> None:
    """S1 L185-L221: central floor hub + 4 radial legs + rubber foot caps."""
    s = r.base_radius_scale
    base.visual(
        Cylinder(radius=0.045, length=0.036),
        origin=Origin(xyz=(0.0, 0.0, 0.018)),
        material=m["dark_metal"],
        name="floor_hub", material_class_id=("metal.cast_iron_bare" if r.material_style == "cast_iron_chrome" else "metal.blackened_gunmetal"),
    )
    for idx, angle in enumerate((0.0, math.pi / 2, math.pi, 3 * math.pi / 2)):
        c = math.cos(angle)
        s_ = math.sin(angle)
        base.visual(
            Cylinder(radius=0.0075, length=0.460 * s),
            origin=Origin(xyz=(0.230 * s * c, 0.230 * s * s_, 0.012), rpy=(0.0, math.pi / 2, angle)),
            material=m["metal"],
            name=f"tripod_leg_{idx}", material_class_id=("metal.chrome_polished" if r.material_style == "cast_iron_chrome" else "metal.stainless_matte"),
        )
        base.visual(
            Sphere(radius=0.017),
            origin=Origin(xyz=(0.463 * s * c, 0.463 * s * s_, 0.012)),
            material=m["rubber"],
            name=f"foot_cap_{idx}", material_class_id="rubber.smooth_plain",
        )


def _star_base_leg(angle: float, s: float) -> MeshGeometry:
    r0 = 0.035
    r1 = 0.335 * s
    points = [
        (r0 * math.cos(angle), r0 * math.sin(angle), 0.055),
        (0.18 * s * math.cos(angle), 0.18 * s * math.sin(angle), 0.035),
        (r1 * math.cos(angle), r1 * math.sin(angle), 0.025),
    ]
    return tube_from_spline_points(points, radius=0.012, samples_per_segment=10, radial_segments=12)


def _build_star_caster_base(base: Part, r: ResolvedTailorSDummyConfig, m: dict, *, model: ArticulatedObject) -> None:
    """S2 L200-L221: central hub + dome + 5 swept spoke legs w/ casters."""
    s = r.base_radius_scale
    base.visual(
        Cylinder(radius=0.043, length=0.035),
        origin=Origin(xyz=(0.0, 0.0, 0.040)),
        material=m["dark_metal"],
        name="central_hub", material_class_id=("metal.cast_iron_bare" if r.material_style == "cast_iron_chrome" else "metal.blackened_gunmetal"),
    )
    base.visual(
        Sphere(radius=0.046),
        origin=Origin(xyz=(0.0, 0.0, 0.055)),
        material=m["dark_metal"],
        name="hub_dome", material_class_id=("metal.cast_iron_bare" if r.material_style == "cast_iron_chrome" else "metal.blackened_gunmetal"),
    )
    for i in range(5):
        angle = 2.0 * math.pi * i / 5.0 + math.radians(18.0)
        base.visual(
            _mesh(model, _star_base_leg(angle, s), f"spoke_{i}"),
            material=m["dark_metal"],
            name=f"spoke_{i}", material_class_id=("metal.cast_iron_bare" if r.material_style == "cast_iron_chrome" else "metal.blackened_gunmetal"),
        )
        end_x = 0.325 * s * math.cos(angle)
        end_y = 0.325 * s * math.sin(angle)
        tangent = angle + math.pi / 2.0
        base.visual(
            Box((0.022, 0.016, 0.042)),
            origin=Origin(xyz=(end_x, end_y, 0.022), rpy=(0.0, 0.0, angle)),
            material=m["dark_metal"],
            name=f"caster_fork_{i}", material_class_id=("metal.cast_iron_bare" if r.material_style == "cast_iron_chrome" else "metal.blackened_gunmetal"),
        )
        base.visual(
            Cylinder(radius=0.024, length=0.018),
            origin=Origin(xyz=(end_x, end_y, 0.010), rpy=(0.0, math.pi / 2.0, tangent)),
            material=m["rubber"],
            name=f"caster_wheel_{i}", material_class_id="rubber.smooth_plain",
        )


def _make_base_disc(s: float) -> LatheGeometry:
    """V2 L175-L193: solid cast-iron domed disc (flat bottom, gentle dome)."""
    max_radius = 0.150 * s
    edge_height = 0.010
    peak_height = 0.028
    profile: list[tuple[float, float]] = [(0.0, 0.0), (max_radius, 0.0), (max_radius, edge_height)]
    n_dome = 12
    for i in range(1, n_dome + 1):
        t = i / n_dome
        rr = max_radius * (1.0 - t)
        z = edge_height + (peak_height - edge_height) * math.sin(math.pi * t / 2.0)
        profile.append((max(0.0, rr), z))
    return LatheGeometry(profile, segments=64)


def _build_round_disc_base(base: Part, r: ResolvedTailorSDummyConfig, m: dict, *, model: ArticulatedObject) -> None:
    """V2 L207-L219: LatheGeometry cast-iron disc + short pedestal collar."""
    s = r.base_radius_scale
    base.visual(
        _mesh(model, _make_base_disc(s), "base_disc"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=m["dark_metal"],
        name="base_disc", material_class_id="metal.cast_iron_bare",
    )
    base.visual(
        Cylinder(radius=0.025, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, 0.036)),
        material=m["dark_metal"],
        name="pedestal_collar", material_class_id=("metal.cast_iron_bare" if r.material_style == "cast_iron_chrome" else "metal.blackened_gunmetal"),
    )


def _build_base(model: ArticulatedObject, r: ResolvedTailorSDummyConfig, m: dict) -> Part:
    base = model.part("base")
    if r.base_support == "tripod_radial":
        _build_tripod_base(base, r, m)
    elif r.base_support == "star_caster_rolling":
        _build_star_caster_base(base, r, m, model=model)
    else:
        _build_round_disc_base(base, r, m, model=model)
    _emit_stand_sleeve(base, r, m)
    return base


# --------------------------------------------------------------------------- #
# Shared spine: column (inner pole + torso + neck) — S1 L223-L270
# --------------------------------------------------------------------------- #


def _build_column(model: ArticulatedObject, r: ResolvedTailorSDummyConfig, m: dict, sections) -> Part:
    """Telescoping inner pole + fabric torso shell + host-conformal seams + neck.

    Local frame: torso bottom section at z=0, neck at z≈0.72; the inner pole
    extends downward (z<0) to be retained inside the base sleeve.
    """
    column = model.part("column")
    # Inner sliding pole (retained inside the base sleeve at rest and extended).
    column.visual(
        Cylinder(radius=0.012, length=_INNER_POLE_LEN),
        origin=Origin(xyz=(0.0, 0.0, -_INNER_POLE_LEN * 0.5)),
        material=m["metal"],
        name="inner_pole", material_class_id=("metal.chrome_polished" if r.material_style == "cast_iron_chrome" else "metal.stainless_matte"),
    )
    column.visual(
        Cylinder(radius=0.040, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, -0.006)),
        material=m["dark_metal"],
        name="support_plate", material_class_id=("metal.cast_iron_bare" if r.material_style == "cast_iron_chrome" else "metal.blackened_gunmetal"),
    )
    # Fabric torso shell + host-derived decoration (④, derived after ③/⑤).
    column.visual(_mesh(model, _make_torso_mesh(sections), "fabric_torso_shell"), material=m["fabric"], name="torso_shell", material_class_id=("fabric.canvas" if r.material_style == "cream_canvas" else "fabric.upholstery_plain"))
    column.visual(
        _mesh(model, _make_vertical_seam(sections, -math.pi / 2, 0.055, 0.705, width=0.009), "front_seam"),
        material=m["seam"],
        name="front_seam", material_class_id="fabric.thread_yarn",
    )
    column.visual(
        _mesh(model, _make_vertical_seam(sections, -2.55, 0.070, 0.600, width=0.007), "side_seam"),
        material=m["seam"],
        name="side_seam", material_class_id="fabric.thread_yarn",
    )
    column.visual(_mesh(model, _make_waist_band(sections, 0.252), "waist_band"), material=m["seam"], name="waist_seam", material_class_id="fabric.thread_yarn")
    column.visual(
        Cylinder(radius=0.075, length=0.016),
        origin=Origin(xyz=(0.0, 0.0, 0.728)),
        material=m["dark_metal"],
        name="neck_cap", material_class_id=("metal.cast_iron_bare" if r.material_style == "cast_iron_chrome" else "metal.blackened_gunmetal"),
    )
    column.visual(
        Cylinder(radius=0.032, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, 0.707)),
        material=m["dark_metal"],
        name="neck_plug", material_class_id=("metal.cast_iron_bare" if r.material_style == "cast_iron_chrome" else "metal.blackened_gunmetal"),
    )
    return column


# --------------------------------------------------------------------------- #
# Always-present rotary hardware: clamp knob (base collar) + neck knob
# --------------------------------------------------------------------------- #


def _build_clamp_knob(model: ArticulatedObject, m: dict) -> Part:
    """S1 L272-L295: collar clamp screw + lobed knob."""
    knob = model.part("clamp_knob")
    knob.visual(
        Cylinder(radius=0.005, length=0.050),
        origin=Origin(xyz=(0.0, 0.0, 0.025)),
        material=m["dark_metal"],
        name="clamp_screw", material_class_id="metal.blackened_gunmetal",
    )
    knob.visual(
        _mesh(
            model,
            KnobGeometry(
                0.040,
                0.020,
                body_style="lobed",
                base_diameter=0.030,
                top_diameter=0.038,
                crown_radius=0.0015,
                grip=KnobGrip(style="ribbed", count=8, depth=0.0012),
            ),
            "collar_lobed_knob",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.058)),
        material=m["dark_metal"],
        name="clamp_knob_cap", material_class_id="metal.blackened_gunmetal",
    )
    return knob


def _build_top_knob(model: ArticulatedObject, m: dict) -> Part:
    """S1 L297-L318: neck stem + domed indicator knob."""
    knob = model.part("top_knob")
    knob.visual(
        Cylinder(radius=0.008, length=0.025),
        origin=Origin(xyz=(0.0, 0.0, 0.0125)),
        material=m["dark_metal"],
        name="neck_stem", material_class_id="metal.blackened_gunmetal",
    )
    knob.visual(
        _mesh(
            model,
            KnobGeometry(
                0.032,
                0.018,
                body_style="domed",
                crown_radius=0.004,
                indicator=KnobIndicator(style="dot", mode="raised", angle_deg=0.0),
            ),
            "top_domed_knob",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.034)),
        material=m["dark_metal"],
        name="top_knob_cap", material_class_id="metal.blackened_gunmetal",
    )
    return knob


# --------------------------------------------------------------------------- #
# Slot B: arms (armless / static_wood_arms / articulated_posable_arms)
# --------------------------------------------------------------------------- #


def _arm_ref_points(sections, side: float) -> tuple[tuple, tuple, tuple]:
    """Shoulder / elbow / wrist reference points in the column frame.

    The arm mounts at the FRONT shoulder and hangs down-forward just OUTSIDE the
    widest (scaled) bust silhouette, so it clears the torso at any
    torso_width_scale — matching a folded posable artist arm."""
    theta_sh = -math.pi / 2.0 + side * 0.9
    sx, sy, _n = _torso_surface(sections, theta_sh, _SHOULDER_Z)
    bust_hw = 0.5 * _section_at(sections, 0.530)[0]
    shoulder = (sx * 0.99, sy * 0.99, _SHOULDER_Z)
    elbow = (side * (bust_hw + 0.035), sy - 0.050, 0.455)
    wrist = (side * (bust_hw - 0.020), sy - 0.120, 0.315)
    return shoulder, elbow, wrist


def _tube(points, radius: float) -> MeshGeometry:
    return tube_from_spline_points(points, radius=radius, samples_per_segment=10, radial_segments=14)


def _hand_points(wrist: tuple, side: float, origin: tuple) -> list[tuple]:
    """Palm spline starting AT the wrist (so it overlaps the wrist ball /
    forearm end) and curling inward, rebased by ``origin``."""
    pts_abs = [
        wrist,
        (wrist[0] - side * 0.022, wrist[1] - 0.020, wrist[2] - 0.012),
        (wrist[0] - side * 0.038, wrist[1] - 0.028, wrist[2] - 0.016),
    ]
    return [(p[0] - origin[0], p[1] - origin[1], p[2] - origin[2]) for p in pts_abs]


def _build_static_wood_arms(column: Part, r: ResolvedTailorSDummyConfig, m: dict, sections, *, model: ArticulatedObject) -> None:
    """S2 L257-L262: rigid folded wooden arms as visuals on the torso column."""
    for idx, side in enumerate((-1.0, 1.0)):
        shoulder, elbow, wrist = _arm_ref_points(sections, side)
        column.visual(Sphere(radius=0.030), origin=Origin(xyz=shoulder), material=m["wood"], name=f"shoulder_ball_{idx}", material_class_id="wood.walnut_dark")
        upper_mid = (0.5 * (shoulder[0] + elbow[0]), 0.5 * (shoulder[1] + elbow[1]) - 0.02, 0.5 * (shoulder[2] + elbow[2]))
        upper = _tube([shoulder, upper_mid, elbow], 0.020)
        column.visual(_mesh(model, upper, f"wood_upper_{idx}"), material=m["wood"], name=f"wood_upper_{idx}", material_class_id="wood.walnut_dark")
        column.visual(Sphere(radius=0.024), origin=Origin(xyz=elbow), material=m["wood"], name=f"elbow_ball_{idx}", material_class_id="wood.walnut_dark")
        fore_mid = (0.5 * (elbow[0] + wrist[0]), 0.5 * (elbow[1] + wrist[1]) - 0.015, 0.5 * (elbow[2] + wrist[2]))
        fore = _tube([elbow, fore_mid, wrist], 0.020)
        column.visual(_mesh(model, fore, f"wood_forearm_{idx}"), material=m["wood"], name=f"wood_forearm_{idx}", material_class_id="wood.walnut_dark")
        column.visual(Sphere(radius=0.020), origin=Origin(xyz=wrist), material=m["wood"], name=f"wrist_ball_{idx}", material_class_id="wood.walnut_dark")
        column.visual(_mesh(model, _tube(_hand_points(wrist, side, (0.0, 0.0, 0.0)), 0.015), f"wood_hand_{idx}"), material=m["wood"], name=f"wood_hand_{idx}", material_class_id="wood.walnut_dark")


def _build_articulated_arms(model: ArticulatedObject, column: Part, r: ResolvedTailorSDummyConfig, m: dict, sections) -> list[tuple[Part, Part, int, tuple]]:
    """V1 L298-L443: split arms into upper_arm + forearm parts with REVOLUTE
    shoulder + elbow joints at ball mounts. Returns (upper, fore, idx, shoulder)."""
    out: list[tuple[Part, Part, int, tuple]] = []
    for idx, side in enumerate((-1.0, 1.0)):
        shoulder, elbow, wrist = _arm_ref_points(sections, side)
        # Shoulder ball stays a fixed socket visual on the torso column.
        column.visual(Sphere(radius=0.030), origin=Origin(xyz=shoulder), material=m["wood"], name=f"shoulder_ball_{idx}", material_class_id="wood.walnut_dark")

        # upper_arm part: origin at shoulder ball.
        upper = model.part(f"upper_arm_{idx}")
        e_loc = (elbow[0] - shoulder[0], elbow[1] - shoulder[1], elbow[2] - shoulder[2])
        upper.visual(
            _mesh(model, _tube([(0.0, 0.0, 0.0), (e_loc[0] * 0.5, e_loc[1] * 0.5 - 0.02, e_loc[2] * 0.5), e_loc], 0.020), f"upper_arm_seg_{idx}"),
            material=m["wood"],
            name=f"upper_arm_seg_{idx}", material_class_id="wood.walnut_dark",
        )
        upper.visual(Sphere(radius=0.024), origin=Origin(xyz=e_loc), material=m["wood"], name=f"elbow_ball_{idx}", material_class_id="wood.walnut_dark")

        # forearm part: origin at elbow ball.
        fore = model.part(f"forearm_{idx}")
        w_loc = (wrist[0] - elbow[0], wrist[1] - elbow[1], wrist[2] - elbow[2])
        fore.visual(
            _mesh(model, _tube([(0.0, 0.0, 0.0), (w_loc[0] * 0.5, w_loc[1] * 0.5 - 0.015, w_loc[2] * 0.5), w_loc], 0.020), f"forearm_seg_{idx}"),
            material=m["wood"],
            name=f"forearm_seg_{idx}", material_class_id="wood.walnut_dark",
        )
        fore.visual(Sphere(radius=0.020), origin=Origin(xyz=w_loc), material=m["wood"], name=f"wrist_ball_{idx}", material_class_id="wood.walnut_dark")
        fore.visual(_mesh(model, _tube(_hand_points(wrist, side, elbow), 0.015), f"wood_hand_{idx}"), material=m["wood"], name=f"wood_hand_{idx}", material_class_id="wood.walnut_dark")
        out.append((upper, fore, idx, shoulder))
    return out


# --------------------------------------------------------------------------- #
# Slot C: adjustment (sizing_dials multiplicity / fixed_pinnable)
# --------------------------------------------------------------------------- #

_DIAL_BANDS = (0.150, 0.240, 0.330, 0.430, 0.520)  # hip→bust vertical stack


def _dial_seats(n: int) -> list[tuple[float, float]]:
    """(theta, z) seats: a center-front vertical row (faithful to reference 001)
    then small ±0.22 near-front columns. Offsets stay small so the dials never
    reach the side-hanging arms; adjacent seats are ≥0.028 apart."""
    front = -math.pi / 2.0
    theta_offsets = (0.0, 0.22, -0.22)  # center, near-front-right, near-front-left
    seats: list[tuple[float, float]] = []
    ti = 0
    while len(seats) < n:
        col = ti // len(_DIAL_BANDS)
        band = _DIAL_BANDS[ti % len(_DIAL_BANDS)]
        theta = front + theta_offsets[col % len(theta_offsets)]
        seats.append((theta, band))
        ti += 1
    return seats[:n]


def _emit_dial(model: ArticulatedObject, idx: int, m: dict) -> Part:
    dial = model.part(f"front_dial_{idx}")
    dial.visual(Cylinder(radius=0.004, length=0.012), origin=Origin(xyz=(0.0, 0.0, 0.006)), material=m["brass"], name="dial_stem", material_class_id="metal.brass_polished")
    dial.visual(Cylinder(radius=0.014, length=0.008), origin=Origin(xyz=(0.0, 0.0, 0.016)), material=m["brass"], name="dial_face", material_class_id="metal.brass_polished")
    dial.visual(Box((0.020, 0.0024, 0.0020)), origin=Origin(xyz=(0.0, 0.0, 0.0208)), material=m["seam"], name="screw_slot", material_class_id="metal.blackened_gunmetal")
    return dial


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def build_tailor_s_dummy(
    config: TailorSDummyConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or TailorSDummyConfig()
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    m = {name: model.material(f"td_{name}", rgba=rgba) for name, rgba in PALETTES[r.material_style].items()}
    sections = _torso_sections(r.torso_width_scale)

    base = _build_base(model, r, m)
    column = _build_column(model, r, m, sections)
    clamp_knob = _build_clamp_knob(model, m)
    top_knob = _build_top_knob(model, m)

    # ---- height adjustment: base -> column, PRISMATIC z (telescoping) ----
    model.articulation(
        "base_to_column",
        ArticulationType.PRISMATIC,
        parent=base,
        child=column,
        origin=Origin(xyz=(0.0, 0.0, _COLUMN_MOUNT_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=100.0, velocity=0.18, lower=0.0, upper=r.height_travel),
    )
    # ---- clamp knob on the base collar, CONTINUOUS ----
    model.articulation(
        "base_to_clamp_knob",
        ArticulationType.CONTINUOUS,
        parent=base,
        child=clamp_knob,
        origin=Origin(xyz=(_COLLAR_R, 0.0, _COLLAR_Z), rpy=(0.0, math.pi / 2, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=8.0),
    )
    # ---- neck knob on the column neck, CONTINUOUS ----
    model.articulation(
        "column_to_top_knob",
        ArticulationType.CONTINUOUS,
        parent=column,
        child=top_knob,
        origin=Origin(xyz=(0.0, 0.0, 0.736)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=6.0),
    )

    # ---- Slot B: arms ----
    if r.arms == "static_wood_arms":
        _build_static_wood_arms(column, r, m, sections, model=model)
    elif r.arms == "articulated_posable_arms":
        arm_parts = _build_articulated_arms(model, column, r, m, sections)
        for upper, fore, idx, shoulder in arm_parts:
            side = -1.0 if idx == 0 else 1.0
            e_loc = (
                _arm_ref_points(sections, side)[1][0] - shoulder[0],
                _arm_ref_points(sections, side)[1][1] - shoulder[1],
                _arm_ref_points(sections, side)[1][2] - shoulder[2],
            )
            model.articulation(
                f"shoulder_{idx}",
                ArticulationType.REVOLUTE,
                parent=column,
                child=upper,
                origin=Origin(xyz=shoulder),
                axis=(0.0, -side, 0.0),
                motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=-0.30, upper=1.20),
            )
            model.articulation(
                f"elbow_{idx}",
                ArticulationType.REVOLUTE,
                parent=upper,
                child=fore,
                origin=Origin(xyz=e_loc),
                axis=(-1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=3.0, velocity=2.5, lower=-0.20, upper=1.80),
            )

    # ---- Slot C: sizing dials (multiplicity) ----
    if r.adjustment == "sizing_dials":
        for idx, (theta, z) in enumerate(_dial_seats(r.dial_count)):
            _emit_dial(model, idx, m)
            x, y, normal = _torso_surface(sections, theta, z)
            yaw = math.atan2(normal[0], -normal[1])
            model.articulation(
                f"torso_to_front_dial_{idx}",
                ArticulationType.CONTINUOUS,
                parent=column,
                child=f"front_dial_{idx}",
                origin=Origin(xyz=(x, y, z), rpy=(math.pi / 2, 0.0, yaw)),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=0.5, velocity=8.0),
            )

    return model


def build_seeded_tailor_s_dummy(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_tailor_s_dummy(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedTailorSDummyConfig) -> None:
    part_names = {p.name for p in model.parts}
    base = model.get_part("base")
    column = model.get_part("column")
    # Telescoping inner pole retained inside the sleeve + clamp collar.
    ctx.allow_overlap(base, column, elem_a="outer_sleeve", elem_b="inner_pole",
                      reason="The height-adjustment inner pole is intentionally retained inside the outer sleeve.")
    ctx.allow_overlap(base, column, elem_a="height_collar", elem_b="inner_pole",
                      reason="The clamp collar surrounds the sliding pole as the real clamp hardware does.")
    # Sizing dial stems intentionally enter the fabric shell.
    if r.adjustment == "sizing_dials":
        for idx in range(r.dial_count):
            dp = model.get_part(f"front_dial_{idx}")
            for host in ("torso_shell", "front_seam", "side_seam", "waist_seam"):
                ctx.allow_overlap(dp, column, elem_a="dial_stem", elem_b=host,
                                  reason="The tiny adjustment screw stem intentionally enters the dress-form shell/seam.")
    # Articulated arm ball-joint mounts (tube rooted inside the ball).
    if r.arms == "articulated_posable_arms":
        for idx in (0, 1):
            up = f"upper_arm_{idx}"
            fo = f"forearm_{idx}"
            if up in part_names:
                ua = model.get_part(up)
                ctx.allow_overlap(column, ua, elem_a=f"shoulder_ball_{idx}", elem_b=f"upper_arm_seg_{idx}",
                                  reason=f"Upper arm {idx} is rooted inside the shoulder ball as a posable mount.")
                for host in ("torso_shell", "front_seam", "side_seam", "waist_seam"):
                    ctx.allow_overlap(column, ua, elem_a=host, elem_b=f"upper_arm_seg_{idx}",
                                      reason=f"Upper arm {idx} root socket embeds shallowly at the front-shoulder mount surface/seam.")
            if up in part_names and fo in part_names:
                ua = model.get_part(up)
                fa = model.get_part(fo)
                ctx.allow_overlap(ua, fa, elem_a=f"elbow_ball_{idx}", elem_b=f"forearm_seg_{idx}",
                                  reason=f"Forearm {idx} is rooted inside the elbow ball as a posable hinge.")
                ctx.allow_overlap(ua, fa, elem_a=f"upper_arm_seg_{idx}", elem_b=f"forearm_seg_{idx}",
                                  reason=f"Upper arm and forearm {idx} meet at the elbow hinge junction.")


def run_tailor_s_dummy_tests(model: ArticulatedObject, config: TailorSDummyConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    _allow_expected_overlaps(ctx, model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    part_names = {p.name for p in model.parts}
    joint_names = {j.name for j in model.joints}

    # Identity invariants.
    for required in ("base", "column", "clamp_knob", "top_knob"):
        if required not in part_names:
            ctx.fail("identity_parts", f"missing {required}")
    if "column" in part_names:
        col_visuals = {v.name for v in model.get_part("column").visuals}
        for req in ("torso_shell", "inner_pole", "neck_cap"):
            if req not in col_visuals:
                ctx.fail("column_identity", f"column missing {req}")
    if "base_to_column" in joint_names:
        j = model.get_articulation("base_to_column")
        if j.articulation_type != ArticulationType.PRISMATIC or tuple(j.axis) != (0.0, 0.0, 1.0):
            ctx.fail("height_joint", f"base_to_column must be PRISMATIC z, got {j.articulation_type}/{j.axis}")

    # Dial multiplicity present iff sizing_dials.
    dial_joints = [n for n in joint_names if n.startswith("torso_to_front_dial_")]
    if r.adjustment == "sizing_dials":
        if len(dial_joints) != r.dial_count:
            ctx.fail("dial_count", f"expected {r.dial_count} dial joints, got {len(dial_joints)}")
        for n in dial_joints:
            if model.get_articulation(n).articulation_type != ArticulationType.CONTINUOUS:
                ctx.fail("dial_joint_type", f"{n} must be CONTINUOUS")
    else:
        if dial_joints:
            ctx.fail("dial_gating", "fixed_pinnable must have no dial joints")

    # Arm topology.
    if r.arms == "articulated_posable_arms":
        for idx in (0, 1):
            for jn in (f"shoulder_{idx}", f"elbow_{idx}"):
                if jn not in joint_names:
                    ctx.fail("arm_joints", f"missing {jn}")
                elif model.get_articulation(jn).articulation_type != ArticulationType.REVOLUTE:
                    ctx.fail("arm_joint_type", f"{jn} must be REVOLUTE")

    # ---- Rule 5: dynamic collision at sampled joint poses ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    # ---- Targeted mechanism poses ----
    if "base_to_column" in joint_names:
        lift = model.get_articulation("base_to_column")
        rest = ctx.part_world_position(model.get_part("column"))
        with ctx.pose({lift: r.height_travel}):
            raised = ctx.part_world_position(model.get_part("column"))
        ctx.check(
            "prismatic height adjustment raises the torso column",
            rest is not None and raised is not None and raised[2] > rest[2] + (r.height_travel - 0.02),
            details=f"rest={rest}, raised={raised}",
        )

    if r.arms == "articulated_posable_arms" and "shoulder_0" in joint_names:
        for idx in (0, 1):
            sh = model.get_articulation(f"shoulder_{idx}")
            el = model.get_articulation(f"elbow_{idx}")
            fa = model.get_part(f"forearm_{idx}")
            rest_aabb = ctx.part_element_world_aabb(fa, elem=f"wood_hand_{idx}")
            with ctx.pose({sh: 1.10, el: 0.0}):
                raised_aabb = ctx.part_element_world_aabb(fa, elem=f"wood_hand_{idx}")
            r0 = rest_aabb[0][2] if rest_aabb else None
            r1 = raised_aabb[0][2] if raised_aabb else None
            ctx.check(
                f"shoulder_{idx} positive pose raises the arm",
                r0 is not None and r1 is not None and r1 > r0 + 0.03,
                details=f"rest_hand_min_z={r0}, raised_hand_min_z={r1}",
            )

    return ctx.report()


__all__ = [
    "TailorSDummyConfig",
    "ResolvedTailorSDummyConfig",
    "build_tailor_s_dummy",
    "build_seeded_tailor_s_dummy",
    "config_from_seed",
    "resolve_config",
    "run_tailor_s_dummy_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
