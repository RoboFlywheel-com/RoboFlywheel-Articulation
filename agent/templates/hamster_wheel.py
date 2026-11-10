# SPDX-License-Identifier: Apache-2.0

"""Hamster wheel — modular procedural template.

A single continuous running wheel that spins freely on a fixed axle carried by
a low stand / cage mount. Two structural layers vary independently and share
one mating interface — the fixed axle at ``axle_height`` along the spin axis,
captured coaxially in the wheel hub bore:

* Slot A ``mount``       — acrylic_block | bent_wire | cage_clamp  (support ①)
* Slot B ``wheel_body``  — solid_drum | open_rung_ring | wire_mesh_band |
                            tilted_saucer  (③ Primary Form Family)

Loop-emitted multiplicity on the wheel: running-surface treads/rungs/mesh_bars
(``n_tread``) and hub spokes (``n_spoke``). Exactly one revolute spin joint
``stand_to_wheel``. seed 0 is NOT special-cased — every seed is sampled by
``random.Random(seed)``.

Sources (5-star): origin A (solid_drum + acrylic_block, ``rec_...__001``),
origin B (bent_wire, ``rec_...__002``) and the verified forks
``rec_hamster_wheel_var_{body_open_ring,body_mesh,skeleton_saucer,mount_clamp}``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    MeshGeometry,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True


Mount = Literal["acrylic_block", "bent_wire", "cage_clamp"]
BodyForm = Literal["solid_drum", "open_rung_ring", "wire_mesh_band", "tilted_saucer"]
PaletteTheme = Literal["blue_clear", "green_translucent", "pink_candy", "amber_honey", "violet_ice"]

MOUNT_MODULES: tuple[Mount, ...] = ("acrylic_block", "bent_wire", "cage_clamp")
BODY_MODULES: tuple[BodyForm, ...] = (
    "solid_drum",
    "open_rung_ring",
    "wire_mesh_band",
    "tilted_saucer",
)
DRUM_FAMILY: frozenset[str] = frozenset({"solid_drum", "open_rung_ring", "wire_mesh_band"})

# Saucer skeleton (source SA): disc normal ~35deg from horizontal, inclined X-Z axle.
SAUCER_TILT = math.radians(35.0)
SAUCER_RADIUS = 0.145
SAUCER_AXLE_HEIGHT = 0.180

AXLE_RADIUS = 0.005

N_TREAD_RANGE = (12, 56)
N_SPOKE_RANGE = (3, 12)


# Every palette carries the same material tokens so any body/mount reads them.
PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "blue_clear": {
        "body": (0.02, 0.62, 1.0, 0.48),
        "shell": (0.92, 0.98, 1.0, 0.34),
        "rim": (0.0, 0.35, 1.0, 0.72),
        "rear": (0.02, 0.62, 1.0, 0.48),
        "hub": (0.0, 0.35, 1.0, 0.72),
        "stand": (0.92, 0.98, 1.0, 0.34),
        "wire": (0.68, 0.70, 0.69, 1.0),
        "axle": (0.95, 0.96, 0.94, 1.0),
    },
    "green_translucent": {
        "body": (0.45, 0.70, 0.38, 0.55),
        "shell": (0.82, 0.95, 0.82, 0.40),
        "rim": (0.82, 0.95, 0.82, 0.55),
        "rear": (0.45, 0.70, 0.38, 0.55),
        "hub": (0.30, 0.55, 0.28, 0.80),
        "stand": (0.93, 0.96, 0.95, 1.0),
        "wire": (0.93, 0.96, 0.95, 1.0),
        "axle": (0.96, 0.96, 0.92, 1.0),
    },
    "pink_candy": {
        "body": (0.98, 0.42, 0.66, 0.50),
        "shell": (1.0, 0.86, 0.92, 0.36),
        "rim": (0.92, 0.20, 0.52, 0.75),
        "rear": (0.98, 0.42, 0.66, 0.50),
        "hub": (0.92, 0.20, 0.52, 0.80),
        "stand": (0.97, 0.90, 0.93, 1.0),
        "wire": (0.72, 0.72, 0.74, 1.0),
        "axle": (0.96, 0.96, 0.94, 1.0),
    },
    "amber_honey": {
        "body": (0.98, 0.68, 0.18, 0.50),
        "shell": (1.0, 0.92, 0.72, 0.36),
        "rim": (0.86, 0.52, 0.06, 0.78),
        "rear": (0.98, 0.68, 0.18, 0.50),
        "hub": (0.86, 0.52, 0.06, 0.82),
        "stand": (0.30, 0.31, 0.33, 1.0),
        "wire": (0.66, 0.67, 0.69, 1.0),
        "axle": (0.90, 0.90, 0.88, 1.0),
    },
    "violet_ice": {
        "body": (0.62, 0.42, 0.98, 0.48),
        "shell": (0.90, 0.86, 1.0, 0.34),
        "rim": (0.42, 0.20, 0.86, 0.74),
        "rear": (0.62, 0.42, 0.98, 0.48),
        "hub": (0.42, 0.20, 0.86, 0.80),
        "stand": (0.93, 0.92, 0.97, 1.0),
        "wire": (0.70, 0.71, 0.74, 1.0),
        "axle": (0.96, 0.96, 0.94, 1.0),
    },
}


@dataclass(frozen=True)
class HamsterWheelConfig:
    mount: Mount | None = None
    body_form: BodyForm | None = None
    n_tread: int = 32
    n_spoke: int = 5
    wheel_radius: float = 0.112
    wheel_depth: float = 0.082
    axle_height: float = 0.160
    spin_range: float = math.pi
    palette_theme: PaletteTheme = "blue_clear"
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["blue_clear"])
    )


@dataclass(frozen=True)
class ResolvedHamsterWheelConfig:
    mount: Mount
    body_form: BodyForm
    n_tread: int
    n_spoke: int
    wheel_radius: float
    wheel_depth: float
    axle_height: float
    spin_range: float
    palette_theme: PaletteTheme
    spin_axis: tuple[float, float, float]
    axle_rpy: tuple[float, float, float]
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _clamp_int(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))


def _weighted_small_int(rng: random.Random, lo: int, hi: int) -> int:
    """Sample an int in [lo, hi] biased toward small values (skew^2)."""
    frac = rng.random() ** 2.0
    return _clamp_int(round(lo + frac * (hi - lo)), lo, hi)


def config_from_seed(seed: int) -> HamsterWheelConfig:
    rng = random.Random(seed)
    body_form: BodyForm = rng.choice(BODY_MODULES)  # type: ignore[assignment]
    if body_form == "tilted_saucer":
        # Compatibility gate: the inclined disc requires converging rear supports;
        # flanking-post / cantilever horizontal stands collide it → bent_wire only.
        mount: Mount = "bent_wire"
    else:
        mount = rng.choice(MOUNT_MODULES)  # type: ignore[assignment]
    palette_theme: PaletteTheme = rng.choice(tuple(PALETTES.keys()))  # type: ignore[assignment]
    return HamsterWheelConfig(
        mount=mount,
        body_form=body_form,
        n_tread=_weighted_small_int(rng, *N_TREAD_RANGE),
        n_spoke=_weighted_small_int(rng, *N_SPOKE_RANGE),
        wheel_radius=round(rng.uniform(0.090, 0.140), 4),
        wheel_depth=round(rng.uniform(0.055, 0.110), 4),
        axle_height=round(rng.uniform(0.140, 0.200), 4),
        spin_range=round(rng.uniform(math.pi, 2.0 * math.pi), 4),
        palette_theme=palette_theme,
    )


def resolve_config(config: HamsterWheelConfig) -> ResolvedHamsterWheelConfig:
    mount = config.mount or "acrylic_block"
    body_form = config.body_form or "solid_drum"
    if mount not in MOUNT_MODULES:
        raise ValueError(f"Unsupported mount: {mount!r}")
    if body_form not in BODY_MODULES:
        raise ValueError(f"Unsupported body_form: {body_form!r}")
    if config.palette_theme not in PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme!r}")
    # Compatibility gate resolved here (never left to the builder).
    if body_form == "tilted_saucer":
        mount = "bent_wire"

    if body_form == "tilted_saucer":
        wheel_radius = SAUCER_RADIUS
        wheel_depth = 0.026
        axle_height = SAUCER_AXLE_HEIGHT
        spin_axis = (math.cos(SAUCER_TILT), 0.0, math.sin(SAUCER_TILT))
        axle_rpy = (0.0, math.pi / 2.0 - SAUCER_TILT, 0.0)
    else:
        wheel_radius = _clamp(config.wheel_radius, 0.090, 0.140)
        wheel_depth = _clamp(config.wheel_depth, 0.055, 0.110)
        axle_height = _clamp(config.axle_height, 0.140, 0.200)
        # inequality: wheel must clear the base plate.
        axle_height = max(axle_height, wheel_radius + 0.030)
        spin_axis = (0.0, 1.0, 0.0)
        axle_rpy = (math.pi / 2.0, 0.0, 0.0)

    return ResolvedHamsterWheelConfig(
        mount=mount,  # type: ignore[arg-type]
        body_form=body_form,  # type: ignore[arg-type]
        n_tread=_clamp_int(config.n_tread, *N_TREAD_RANGE),
        n_spoke=_clamp_int(config.n_spoke, *N_SPOKE_RANGE),
        wheel_radius=wheel_radius,
        wheel_depth=wheel_depth,
        axle_height=axle_height,
        spin_range=_clamp(config.spin_range, math.pi, 2.0 * math.pi),
        palette_theme=config.palette_theme,
        spin_axis=spin_axis,
        axle_rpy=axle_rpy,
        palette=dict(PALETTES[config.palette_theme]),
    )


# ── Geometry helpers ─────────────────────────────────────────────────────


def _annular_cylinder_y(
    outer_radius: float,
    inner_radius: float,
    depth: float,
    *,
    segments: int = 96,
) -> MeshGeometry:
    """Closed annular cylinder with its axis along local Y (source A helper)."""
    geom = MeshGeometry()
    y_front = -depth / 2.0
    y_rear = depth / 2.0
    outer_front: list[int] = []
    outer_rear: list[int] = []
    inner_front: list[int] = []
    inner_rear: list[int] = []
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        xo = outer_radius * math.cos(angle)
        zo = outer_radius * math.sin(angle)
        xi = inner_radius * math.cos(angle)
        zi = inner_radius * math.sin(angle)
        outer_front.append(geom.add_vertex(xo, y_front, zo))
        outer_rear.append(geom.add_vertex(xo, y_rear, zo))
        inner_front.append(geom.add_vertex(xi, y_front, zi))
        inner_rear.append(geom.add_vertex(xi, y_rear, zi))
    for i in range(segments):
        j = (i + 1) % segments
        geom.add_face(outer_front[i], outer_front[j], outer_rear[j])
        geom.add_face(outer_front[i], outer_rear[j], outer_rear[i])
        geom.add_face(inner_front[j], inner_front[i], inner_rear[i])
        geom.add_face(inner_front[j], inner_rear[i], inner_rear[j])
        geom.add_face(inner_front[i], inner_front[j], outer_front[j])
        geom.add_face(inner_front[i], outer_front[j], outer_front[i])
        geom.add_face(outer_rear[i], outer_rear[j], inner_rear[j])
        geom.add_face(outer_rear[i], inner_rear[j], inner_rear[i])
    return geom


def _add_y_cylinder(
    part: Part,
    *,
    radius: float,
    length: float,
    xyz: tuple[float, float, float],
    material: str,
    name: str,
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="plastic.opaque_glossy_molded",
    )


def _add_radial_cylinder(
    part: Part,
    *,
    angle: float,
    radius_mid: float,
    length: float,
    rod_radius: float,
    y: float,
    material: str,
    name: str,
) -> None:
    x = radius_mid * math.cos(angle)
    z = radius_mid * math.sin(angle)
    pitch = math.pi / 2.0 - angle
    part.visual(
        Cylinder(radius=rod_radius, length=length),
        origin=Origin(xyz=(x, y, z), rpy=(0.0, pitch, 0.0)),
        material=material,
        name=name, material_class_id="plastic.opaque_glossy_molded",
    )


def _y_torus_rim(radius: float, tube: float, name: str) -> MeshGeometry:
    torus = TorusGeometry(radius, tube, radial_segments=16, tubular_segments=128)
    torus.rotate_x(math.pi / 2.0)
    return mesh_from_geometry(torus, name)


# ── Shared axle assembly (horizontal Y, drum-family mounts) ────────────────


def _emit_horizontal_axle(stand: Part, r: ResolvedHamsterWheelConfig) -> float:
    """Fixed axle + front cap + rear bearing along +Y, captured by the hub.

    Returns the rear-support anchor y (where posts/yokes/arm converge)."""
    d = r.wheel_depth
    h = r.axle_height
    front_y = -(d / 2.0 + 0.020)
    rear_y = d / 2.0 + 0.023
    y_rear_support = d / 2.0 + 0.017
    axle_center = (front_y + rear_y) / 2.0
    axle_len = (rear_y - front_y)
    _add_y_cylinder(
        stand,
        radius=AXLE_RADIUS,
        length=axle_len,
        xyz=(0.0, axle_center, h),
        material="axle",
        name="axle_shaft",
    )
    _add_y_cylinder(
        stand,
        radius=0.014,
        length=0.012,
        xyz=(0.0, front_y - 0.002, h),
        material="axle",
        name="front_axle_cap",
    )
    _add_y_cylinder(
        stand,
        radius=0.017,
        length=0.020,
        xyz=(0.0, rear_y - 0.004, h),
        material="body",
        name="bearing_block",
    )
    return y_rear_support


# ── Mount modules (build the grounded ``stand`` part) ──────────────────────


def _build_acrylic_block(model: ArticulatedObject, r: ResolvedHamsterWheelConfig) -> None:
    stand = model.part("stand")
    R, h = r.wheel_radius, r.axle_height
    y_rear = _emit_horizontal_axle(stand, r)

    base_w = 2.0 * R + 0.056
    base_d = max(0.150, r.wheel_depth + 2.0 * y_rear + 0.040)
    base_cy = (y_rear + 0.006) * 0.5 - (r.wheel_depth / 2.0 + 0.020) * 0.5
    base_profile = rounded_rect_profile(base_w, base_d, 0.018, corner_segments=10)
    stand.visual(
        mesh_from_geometry(
            ExtrudeGeometry.from_z0(base_profile, 0.010, cap=True, closed=True),
            "rounded_base_plate",
        ),
        origin=Origin(xyz=(0.0, base_cy, 0.0)),
        material="stand",
        name="base_plate", material_class_id=("plastic.clear_rigid" if r.palette_theme == "blue_clear" else "plastic.opaque_glossy_molded"),
    )
    post_x = R * 0.48
    post_h = h - 0.010
    for i, sx in enumerate((-1.0, 1.0)):
        stand.visual(
            Box((0.013, 0.012, post_h)),
            origin=Origin(xyz=(sx * post_x, y_rear, 0.010 + post_h * 0.5)),
            material="stand",
            name=f"support_post_{i}", material_class_id=("plastic.clear_rigid" if r.palette_theme == "blue_clear" else "plastic.opaque_glossy_molded"),
        )
    stand.visual(
        Box((2.0 * post_x + 0.016, 0.014, 0.016)),
        origin=Origin(xyz=(0.0, y_rear, h)),
        material="stand",
        name="bearing_crossbar", material_class_id=("plastic.clear_rigid" if r.palette_theme == "blue_clear" else "plastic.opaque_glossy_molded"),
    )
    stand.visual(
        Box((2.0 * post_x + 0.020, 0.020, 0.011)),
        origin=Origin(xyz=(0.0, y_rear, 0.0155)),
        material="stand",
        name="rear_foot_rail", material_class_id=("plastic.clear_rigid" if r.palette_theme == "blue_clear" else "plastic.opaque_glossy_molded"),
    )
    _set_stand_inertial(stand, base_w, base_d, h)


def _build_bent_wire(model: ArticulatedObject, r: ResolvedHamsterWheelConfig) -> None:
    stand = model.part("stand")
    h = r.axle_height
    y_rear = _emit_horizontal_axle(stand, r)
    front_y = -(r.wheel_depth / 2.0 + 0.030)
    rear_y = y_rear + 0.045
    xw = r.wheel_radius + 0.010

    base_loop = tube_from_spline_points(
        [
            (-xw, front_y, 0.006),
            (xw, front_y, 0.006),
            (xw + 0.010, rear_y, 0.006),
            (-xw - 0.010, rear_y, 0.006),
        ],
        radius=0.0045,
        samples_per_segment=12,
        closed_spline=True,
        radial_segments=16,
    )
    stand.visual(
        mesh_from_geometry(base_loop, "stand_base_loop"),
        material="wire",
        name="base_loop", material_class_id="metal.paint_coated",
    )
    for idx, side in enumerate((-1.0, 1.0)):
        yoke = tube_from_spline_points(
            [
                (side * (xw + 0.008), rear_y, 0.006),
                (side * (xw - 0.010), rear_y - 0.010, 0.050),
                (side * 0.050, y_rear + 0.020, 0.5 * (h + 0.010)),
                (side * 0.020, y_rear + 0.006, h),
                (0.0, y_rear + 0.004, h),
            ],
            radius=0.0042,
            samples_per_segment=10,
            closed_spline=False,
            radial_segments=16,
            cap_ends=True,
        )
        stand.visual(
            mesh_from_geometry(yoke, f"side_support_{idx}"),
            material="wire",
            name=f"side_support_{idx}", material_class_id="metal.paint_coated",
        )
    _set_stand_inertial(stand, 2.0 * xw, rear_y - front_y, h)


def _build_cage_clamp(model: ArticulatedObject, r: ResolvedHamsterWheelConfig) -> None:
    stand = model.part("stand")
    h = r.axle_height
    y_rear = _emit_horizontal_axle(stand, r)
    plate_y = y_rear + 0.070
    jaw_y = plate_y - 0.006  # jaws overlap the clamp plate in y (no island gap)

    stand.visual(
        Box((0.052, 0.006, 0.082)),
        origin=Origin(xyz=(0.0, plate_y, h)),
        material="wire",
        name="clamp_plate", material_class_id="metal.paint_coated",
    )
    # Upper jaw hooks over a cage bar from above; lower jaw grips from below.
    stand.visual(
        Box((0.042, 0.022, 0.007)),
        origin=Origin(xyz=(0.0, jaw_y, h + 0.032)),
        material="wire",
        name="clamp_jaw_upper", material_class_id="metal.paint_coated",
    )
    stand.visual(
        Box((0.042, 0.005, 0.014)),
        origin=Origin(xyz=(0.0, jaw_y - 0.0085, h + 0.024)),
        material="wire",
        name="clamp_jaw_upper_hook", material_class_id="metal.paint_coated",
    )
    stand.visual(
        Box((0.042, 0.022, 0.007)),
        origin=Origin(xyz=(0.0, jaw_y, h - 0.038)),
        material="wire",
        name="clamp_jaw_lower", material_class_id="metal.paint_coated",
    )
    stand.visual(
        Box((0.042, 0.005, 0.010)),
        origin=Origin(xyz=(0.0, jaw_y - 0.0085, h - 0.030)),
        material="wire",
        name="clamp_jaw_lower_grip", material_class_id="metal.paint_coated",
    )
    # Horizontal cantilever arm from the clamp plate inward to the bearing.
    arm_front = y_rear - 0.004
    arm_back = plate_y
    arm_len = arm_back - arm_front
    stand.visual(
        Box((0.020, arm_len, 0.016)),
        origin=Origin(xyz=(0.0, (arm_front + arm_back) * 0.5, h)),
        material="stand",
        name="mount_arm", material_class_id="metal.paint_coated",
    )
    stand.visual(
        Box((0.006, 0.020, 0.028)),
        origin=Origin(xyz=(0.0, arm_back - 0.004, h + 0.020)),
        material="stand",
        name="mount_arm_brace", material_class_id="metal.paint_coated",
    )
    _set_stand_inertial(stand, 0.10, arm_len + 0.05, h)


def _set_stand_inertial(stand: Part, w: float, d: float, h: float) -> None:
    stand.inertial = Inertial.from_geometry(
        Box((max(w, 0.05), max(d, 0.05), h)),
        mass=1.4,
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
    )


def _build_stand(model: ArticulatedObject, r: ResolvedHamsterWheelConfig) -> None:
    if r.body_form == "tilted_saucer":
        _build_saucer_stand(model, r)
    elif r.mount == "acrylic_block":
        _build_acrylic_block(model, r)
    elif r.mount == "bent_wire":
        _build_bent_wire(model, r)
    else:
        _build_cage_clamp(model, r)


# ── Wheel bodies (build the spinning ``wheel`` part) ───────────────────────


def _emit_rims_hub_backbone(wheel: Part, r: ResolvedHamsterWheelConfig, *, full_rear: bool) -> None:
    """Torus rims + connective rear_disk + hub sleeve shared by drum-family."""
    R, D = r.wheel_radius, r.wheel_depth
    wheel.visual(
        _y_torus_rim(R, 0.0045, "rounded_front_rim"),
        origin=Origin(xyz=(0.0, -D / 2.0, 0.0)),
        material="rim",
        name="front_rim", material_class_id="plastic.frosted_translucent",
    )
    wheel.visual(
        _y_torus_rim(R, 0.0045, "rounded_rear_rim"),
        origin=Origin(xyz=(0.0, D / 2.0, 0.0)),
        material="rim",
        name="rear_rim", material_class_id="plastic.frosted_translucent",
    )
    # Rear disk is the connective backbone: reaches the rim so rims/spokes/
    # running-surface all share a support path to the hub (kills islands).
    rear_outer = R - 0.001 if full_rear else R - 0.008
    wheel.visual(
        mesh_from_geometry(
            _annular_cylinder_y(rear_outer, AXLE_RADIUS + 0.006, 0.004, segments=128),
            "rear_disk_with_axle_hole",
        ),
        origin=Origin(xyz=(0.0, -D / 2.0 + 0.006, 0.0)),
        material="rear",
        name="rear_disk", material_class_id="plastic.frosted_translucent",
    )
    wheel.visual(
        mesh_from_geometry(
            _annular_cylinder_y(0.018, AXLE_RADIUS * 0.90, min(0.033, D - 0.008), segments=72),
            "central_hub_sleeve",
        ),
        origin=Origin(xyz=(0.0, -D / 2.0 + 0.012, 0.0)),
        material="hub",
        name="wheel_hub", material_class_id="plastic.opaque_glossy_molded",
    )


def _emit_spokes(wheel: Part, r: ResolvedHamsterWheelConfig, *, reach: float) -> None:
    D = r.wheel_depth
    spoke_inner = 0.018
    spoke_mid = (spoke_inner + reach) / 2.0
    spoke_len = reach - spoke_inner
    n = r.n_spoke
    for i in range(n):
        angle = math.radians(18.0 + i * (360.0 / n))
        _add_radial_cylinder(
            wheel,
            angle=angle,
            radius_mid=spoke_mid,
            length=spoke_len,
            rod_radius=0.0028,
            y=-D / 2.0 + 0.008,
            material="hub",
            name=f"spoke_{i}",
        )


def _build_solid_drum(model: ArticulatedObject, r: ResolvedHamsterWheelConfig) -> None:
    wheel = model.part("wheel")
    R, D = r.wheel_radius, r.wheel_depth
    wheel.visual(
        mesh_from_geometry(
            _annular_cylinder_y(R - 0.004, R - 0.009, D, segments=128),
            "transparent_running_drum",
        ),
        origin=Origin(),
        material="body",
        name="drum_wall", material_class_id="plastic.clear_rigid",
    )
    _emit_rims_hub_backbone(wheel, r, full_rear=False)
    _emit_spokes(wheel, r, reach=R - 0.008)
    tread_r = R - 0.011
    for i in range(r.n_tread):
        angle = 2.0 * math.pi * i / r.n_tread
        _add_y_cylinder(
            wheel,
            radius=0.0019,
            length=D - 0.016,
            xyz=(tread_r * math.cos(angle), 0.0, tread_r * math.sin(angle)),
            material="rim",
            name=f"tread_{i}",
        )
    _set_wheel_inertial(wheel, r)


def _build_open_rung_ring(model: ArticulatedObject, r: ResolvedHamsterWheelConfig) -> None:
    wheel = model.part("wheel")
    R, D = r.wheel_radius, r.wheel_depth
    _emit_rims_hub_backbone(wheel, r, full_rear=True)
    _emit_spokes(wheel, r, reach=R - 0.001)
    for i in range(r.n_tread):
        angle = 2.0 * math.pi * i / r.n_tread
        _add_y_cylinder(
            wheel,
            radius=0.0022,
            length=D - 0.002,
            xyz=(R * math.cos(angle), 0.0, R * math.sin(angle)),
            material="rim",
            name=f"rung_{i}",
        )
    _set_wheel_inertial(wheel, r)


def _build_wire_mesh_band(model: ArticulatedObject, r: ResolvedHamsterWheelConfig) -> None:
    wheel = model.part("wheel")
    R, D = r.wheel_radius, r.wheel_depth
    _emit_rims_hub_backbone(wheel, r, full_rear=True)
    _emit_spokes(wheel, r, reach=R - 0.001)
    wire_radius = 0.0015
    mesh_radius = R - 0.006  # outer edge (mesh_radius + wire) meets the rim inner edge
    n_bar = r.n_tread
    for i in range(n_bar):
        angle = 2.0 * math.pi * i / n_bar
        _add_y_cylinder(
            wheel,
            radius=wire_radius,
            # Span the full depth so the bars reach (and touch) both rims.
            length=D + 0.002,
            xyz=(mesh_radius * math.cos(angle), 0.0, mesh_radius * math.sin(angle)),
            material="wire",
            name=f"mesh_bar_{i}",
        )
    n_hoop = max(3, min(8, r.n_spoke + 1))
    for j in range(n_hoop):
        y_pos = -D / 2.0 + 0.008 + j * (D - 0.016) / max(1, n_hoop - 1)
        hoop = TorusGeometry(mesh_radius, wire_radius, radial_segments=10, tubular_segments=96)
        hoop.rotate_x(math.pi / 2.0)
        wheel.visual(
            mesh_from_geometry(hoop, f"mesh_hoop_ring_{j}"),
            origin=Origin(xyz=(0.0, y_pos, 0.0)),
            material="wire",
            name=f"mesh_hoop_{j}", material_class_id="metal.mesh_chainmail",
        )
    _set_wheel_inertial(wheel, r)


def _make_saucer_disc(radius: float) -> object:
    """Shallow saucer disc: annular disc + hub boss + peripheral lip (source SA)."""
    disc_t = 0.010
    hub_extra = 0.010
    hub_outer_r = 0.034
    bore_r = 0.012
    lip_h = 0.018
    lip_w = 0.012
    disc = (
        cq.Workplane("YZ").circle(radius).circle(bore_r).extrude(disc_t).translate((-disc_t / 2.0, 0.0, 0.0))
    )
    hub_t = disc_t + hub_extra
    hub = (
        cq.Workplane("YZ").circle(hub_outer_r).circle(bore_r).extrude(hub_t).translate((-hub_t / 2.0, 0.0, 0.0))
    )
    lip = (
        cq.Workplane("YZ")
        .circle(radius + 0.003)
        .circle(radius - lip_w)
        .extrude(lip_h)
        .translate((disc_t / 2.0, 0.0, 0.0))
    )
    return disc.union(hub).union(lip)


def _build_tilted_saucer(model: ArticulatedObject, r: ResolvedHamsterWheelConfig) -> None:
    wheel = model.part("wheel")
    wheel.visual(
        mesh_from_cadquery(
            _make_saucer_disc(r.wheel_radius),
            "running_disc",
            tolerance=0.0008,
            angular_tolerance=0.05,
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, -SAUCER_TILT, 0.0)),
        material="body",
        name="running_disc", material_class_id="plastic.frosted_translucent",
    )
    wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=r.wheel_radius, length=0.03),
        mass=0.28,
        origin=Origin(),
    )


def _set_wheel_inertial(wheel: Part, r: ResolvedHamsterWheelConfig) -> None:
    wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=r.wheel_radius, length=r.wheel_depth),
        mass=0.30,
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
    )


def _build_wheel(model: ArticulatedObject, r: ResolvedHamsterWheelConfig) -> None:
    if r.body_form == "solid_drum":
        _build_solid_drum(model, r)
    elif r.body_form == "open_rung_ring":
        _build_open_rung_ring(model, r)
    elif r.body_form == "wire_mesh_band":
        _build_wire_mesh_band(model, r)
    else:
        _build_tilted_saucer(model, r)


# ── Saucer stand (inclined converging-yoke bent wire, source SA) ───────────


def _saucer_axis_to_world(d: float, h: float) -> tuple[float, float, float]:
    return (d * math.cos(SAUCER_TILT), 0.0, h + d * math.sin(SAUCER_TILT))


def _build_saucer_stand(model: ArticulatedObject, r: ResolvedHamsterWheelConfig) -> None:
    stand = model.part("stand")
    h = r.axle_height
    pitch = r.axle_rpy[1]

    base_loop = tube_from_spline_points(
        [
            (-0.082, -0.175, 0.006),
            (0.094, -0.175, 0.006),
            (0.104, 0.175, 0.006),
            (-0.082, 0.175, 0.006),
        ],
        radius=0.0045,
        samples_per_segment=12,
        closed_spline=True,
        radial_segments=16,
    )
    stand.visual(mesh_from_geometry(base_loop, "stand_base_loop"), material="wire", name="base_loop", material_class_id="metal.paint_coated")

    rear_axle_pt = _saucer_axis_to_world(-0.055, h)
    for idx, side in enumerate((-1.0, 1.0)):
        yoke = tube_from_spline_points(
            [
                (-0.082, side * 0.175, 0.006),
                (-0.078, side * 0.130, 0.055),
                (-0.068, side * 0.060, 0.110),
                (-0.052, side * 0.012, rear_axle_pt[2] + 0.005),
                rear_axle_pt,
            ],
            radius=0.0042,
            samples_per_segment=10,
            closed_spline=False,
            radial_segments=16,
            cap_ends=True,
        )
        stand.visual(mesh_from_geometry(yoke, f"side_support_{idx}"), material="wire", name=f"side_support_{idx}", material_class_id="metal.paint_coated")

    # Inclined axle + thrust-bearing caps pressing on the disc hub faces.
    hub_half_t = (0.010 + 0.010) / 2.0
    thrust = 0.0005
    front_cap_d = hub_half_t - thrust + 0.006
    rear_bearing_d = -(hub_half_t - thrust + 0.007)
    axle_front_d = front_cap_d + 0.006 + 0.005
    axle_rear_d = -0.072
    axle_center_d = (axle_front_d + axle_rear_d) / 2.0
    axle_span = axle_front_d - axle_rear_d
    stand.visual(
        Cylinder(radius=0.006, length=axle_span),
        origin=Origin(xyz=_saucer_axis_to_world(axle_center_d, h), rpy=(0.0, pitch, 0.0)),
        material="wire",
        name="axle_shaft", material_class_id="metal.stainless_matte",
    )
    stand.visual(
        Cylinder(radius=0.018, length=0.012),
        origin=Origin(xyz=_saucer_axis_to_world(front_cap_d, h), rpy=(0.0, pitch, 0.0)),
        material="axle",
        name="front_axle_cap", material_class_id="metal.stainless_matte",
    )
    stand.visual(
        Cylinder(radius=0.016, length=0.014),
        origin=Origin(xyz=_saucer_axis_to_world(rear_bearing_d, h), rpy=(0.0, pitch, 0.0)),
        material="axle",
        name="rear_bearing", material_class_id="metal.stainless_matte",
    )
    _set_stand_inertial(stand, 0.20, 0.35, h)


# ── Assembly ───────────────────────────────────────────────────────────────


def build_hamster_wheel(
    config: HamsterWheelConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="hamster_wheel", assets=assets)
    for material, rgba in r.palette.items():
        model.material(material, rgba=rgba)

    _build_stand(model, r)
    _build_wheel(model, r)

    model.articulation(
        "stand_to_wheel",
        ArticulationType.REVOLUTE,
        parent=model.get_part("stand"),
        child=model.get_part("wheel"),
        origin=Origin(xyz=(0.0, 0.0, r.axle_height)),
        axis=r.spin_axis,
        motion_limits=MotionLimits(
            effort=0.25, velocity=16.0, lower=-r.spin_range, upper=r.spin_range
        ),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_hamster_wheel(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_hamster_wheel(config_from_seed(seed), assets=assets)


def _tread_band(r: ResolvedHamsterWheelConfig) -> str:
    if r.body_form == "tilted_saucer":
        return "na"
    n = r.n_tread
    if n < 22:
        return "sparse"
    if n <= 40:
        return "medium"
    return "dense"


def slot_choices_for_config(r: ResolvedHamsterWheelConfig) -> list[tuple[str, str]]:
    spoke = "na" if r.body_form == "tilted_saucer" else str(r.n_spoke)
    return [
        ("mount", r.mount),
        ("body_form", r.body_form),
        ("n_tread", _tread_band(r)),
        ("n_spoke", spoke),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ── Tests ────────────────────────────────────────────────────────────────


def _visual_names(part: Part) -> set[str]:
    return {v.name for v in part.visuals if v.name is not None}


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedHamsterWheelConfig) -> None:
    stand = model.get_part("stand")
    wheel = model.get_part("wheel")
    if r.body_form == "tilted_saucer":
        # Thrust-bearing caps press on the disc hub faces (captured on the axle).
        ctx.allow_overlap(
            stand, wheel, elem_a="front_axle_cap", elem_b="running_disc",
            reason="Front axle cap seats against the saucer hub face as a thrust bearing.",
        )
        ctx.allow_overlap(
            stand, wheel, elem_a="rear_bearing", elem_b="running_disc",
            reason="Rear bearing seats against the saucer hub face as a thrust bearing.",
        )
        ctx.allow_overlap(
            stand, wheel, elem_a="axle_shaft", elem_b="running_disc",
            reason="Fixed axle passes through the saucer hub bore (captured pin).",
        )
    else:
        # Fixed axle is captured inside the rotating hub sleeve (pin-through-sleeve).
        ctx.allow_overlap(
            stand, wheel, elem_a="axle_shaft", elem_b="wheel_hub",
            reason="The rotating hub sleeve is captured on the fixed axle shaft.",
        )


def run_hamster_wheel_tests(object_model: ArticulatedObject, config: HamsterWheelConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlaps(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    parts = {p.name for p in object_model.parts}
    ctx.check("stand_present", "stand" in parts)
    ctx.check("wheel_present", "wheel" in parts)

    spins = [
        j for j in object_model.articulations
        if j.name == "stand_to_wheel" and j.articulation_type == ArticulationType.REVOLUTE
    ]
    ctx.check(
        "exactly_one_revolute_spin",
        len(spins) == 1 and len([j for j in object_model.articulations]) == 1,
        details=f"articulations={[j.name for j in object_model.articulations]}",
    )
    stand = object_model.get_part("stand")
    wheel = object_model.get_part("wheel")
    spin = object_model.get_articulation("stand_to_wheel")

    ctx.check(
        "spin_axis_matches_body",
        all(abs(spin.axis[i] - r.spin_axis[i]) < 1e-6 for i in range(3))
        and abs(spin.origin.xyz[2] - r.axle_height) < 1e-6,
        details=f"axis={tuple(spin.axis)}, origin={spin.origin.xyz}",
    )

    # Wheel stands above the base: the lowest wheel point clears z=0.
    wheel_aabb = ctx.part_world_aabb(wheel)
    if wheel_aabb is not None:
        ctx.check(
            "wheel_clears_the_floor",
            wheel_aabb[0][2] > 0.010,
            details=f"wheel_min_z={wheel_aabb[0][2]:.4f}",
        )

    # Axle is coaxial inside the hub bore (captured-pin interface).
    if r.body_form != "tilted_saucer":
        ctx.expect_within(
            stand, wheel, axes="xz",
            inner_elem="axle_shaft", outer_elem="wheel_hub",
            margin=0.0, name="axle shaft coaxial inside hub sleeve",
        )

    # Running-surface + spoke multiplicity is present with the sampled counts.
    wheel_visuals = _visual_names(wheel)
    if r.body_form in DRUM_FAMILY:
        stem = {"solid_drum": "tread", "open_rung_ring": "rung", "wire_mesh_band": "mesh_bar"}[r.body_form]
        ctx.check(
            f"{stem}_multiplicity_realized",
            all(f"{stem}_{i}" in wheel_visuals for i in range(r.n_tread)),
            details=f"expected {r.n_tread} {stem}_*",
        )
        ctx.check(
            "spoke_multiplicity_realized",
            all(f"spoke_{i}" in wheel_visuals for i in range(r.n_spoke)),
            details=f"expected {r.n_spoke} spoke_*",
        )
    else:
        ctx.check("saucer_disc_present", "running_disc" in wheel_visuals)

    # Motion: wheel is symmetric about the spin axis, so its envelope is
    # constant under rotation — closed-pose clearance implies all-pose clearance.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    def _center(elem: str):
        box = ctx.part_element_world_aabb(wheel, elem=elem)
        if box is None:
            return None
        (mn, mx) = box
        return ((mn[0] + mx[0]) / 2.0, (mn[1] + mx[1]) / 2.0, (mn[2] + mx[2]) / 2.0)

    if r.body_form in DRUM_FAMILY:
        # Targeted spin: an off-centre running element sweeps around the axle.
        probe = {"solid_drum": "tread_0", "open_rung_ring": "rung_0", "wire_mesh_band": "mesh_bar_0"}[
            r.body_form
        ]
        rest = _center(probe)
        with ctx.pose({spin: min(r.spin_range, math.pi / 2.0)}):
            spun = _center(probe)
            wheel_pose = ctx.part_world_position(wheel)
        moved = (
            rest is not None and spun is not None
            and (abs(spun[0] - rest[0]) > 0.008 or abs(spun[1] - rest[1]) > 0.008)
            and abs(spun[2] - rest[2]) > 0.008
        )
        ctx.check("running_surface_spins_around_axle", moved, details=f"rest={rest}, spun={spun}")
    else:
        # The saucer disc is rotationally symmetric (no trackable off-axis
        # feature); assert its defining tilt instead (source SA proof).
        disc_aabb = ctx.part_element_world_aabb(wheel, elem="running_disc")
        with ctx.pose({spin: min(r.spin_range, math.pi / 2.0)}):
            wheel_pose = ctx.part_world_position(wheel)
        ctx.check(
            "saucer_disc_is_tilted",
            disc_aabb is not None and (disc_aabb[1][2] - disc_aabb[0][2]) > 0.080,
            details=f"z_extent={None if disc_aabb is None else disc_aabb[1][2]-disc_aabb[0][2]:.4f}",
        )

    ctx.check(
        "wheel_origin_pinned_to_axle",
        wheel_pose is not None
        and abs(wheel_pose[0]) < 1e-6
        and abs(wheel_pose[1]) < 1e-6
        and abs(wheel_pose[2] - r.axle_height) < 1e-6,
        details=f"wheel_pose={wheel_pose}",
    )

    return ctx.report()


__all__ = [
    "BodyForm",
    "HamsterWheelConfig",
    "Mount",
    "PaletteTheme",
    "ResolvedHamsterWheelConfig",
    "__modular__",
    "build_hamster_wheel",
    "build_seeded_hamster_wheel",
    "config_from_seed",
    "resolve_config",
    "run_hamster_wheel_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
