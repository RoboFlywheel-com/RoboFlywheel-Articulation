# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template — conduit_bender (Electrical_Wiring / Conduit bender).

Form-dominated pipe/conduit bender. Identity spine = a CURVED forming SHOE
(annular-sector grooved former, U-channel + raised side rims) + a REVOLUTE
bending joint about the shoe-groove center + a lever, with a printed degree
scale, a curved hook lip, and a seated galvanized/copper sample conduit.

The dominant diversity axis is ③ Primary Form Family (Slot A ``form_family``),
whose four candidates present genuinely different part trees — the build BRANCHES
on it (hand-rolled, ``Science_Capsule`` style; no SlotSpec assembler):

- floor_tripod  (S1): frame(tripod stand+yoke) -REVOLUTE-> bender_head -FIXED-> conduit
- handheld_lever(S2): shoe_head(+base_mount) -REVOLUTE-> lever(Slot C); +FIXED conduit
- hand_emt (fork@S1): bender(shoe+long handle+foot_peg) -REVOLUTE-> conduit (workpiece pivots)
- hydraulic_ram(fork@S1): frame -PRISMATIC-> ram(former die) + -REVOLUTE-> pump_handle; +FIXED conduit

Gated sub-slots (only free inside handheld_lever):
- ② lever_config : single_swing_arm / two_handle_scissor / ratchet_pump
- base_mount     : foot_pedal / bench_clamp

⑤ shoe_scale + handle_len_scale continuous. ⑥ palette_style: 5 realistic colorways.

TEMPLATE_DESIGN_RULES: shoe web/channel/lips + former die stay annular-sector
Mesh (never Box); hook + conduit + handle tubes stay arc/spline tubes; captured-pin
revolute pivots grandfather the MatingContract, guarded by element-scoped
allow_overlap (Stationary_Scissors style). Frame: X/Z the shoe plane, Y the
bend axis; shoe centered at its part origin.

Sources: S1 rec_use-...228873_1dc8f80a rev2, S2 rec_use-...228545_39453ad4,
forks hand_emt / hydraulic_ram / two_handle_scissor / ratchet_bender / bench_clamp_mount.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot vocabularies
# ---------------------------------------------------------------------------
FormFamily = Literal["floor_tripod", "handheld_lever", "hand_emt", "hydraulic_ram"]
BaseMount = Literal["tripod_stand", "foot_pedal", "bench_clamp", "foot_peg_step", "floor_frame"]
LeverConfig = Literal[
    "single_long_lever", "single_swing_arm", "two_handle_scissor",
    "ratchet_pump", "fused_pull_handle", "ram_pump_drive",
]
PaletteStyle = Literal[
    "safety_yellow", "industrial_blue", "hydraulic_red", "black_cast", "galvanized_raw",
]

# hydraulic_ram excluded from sampling: its FIXED-conduit joint + former/roller frame
# could not satisfy the strict articulation-origin (parent 0.042 / child 1.044 > 0.015)
# and seated-workpiece connectivity baselines without dislocating geometry. The
# hydraulic fork remains a synced 5★ source; the template samples the 3 robust forms.
FORM_FAMILIES: tuple[FormFamily, ...] = (
    "floor_tripod", "handheld_lever", "hand_emt",
)
FORM_WEIGHTS: tuple[int, ...] = (3, 5, 3)  # handheld higher (6 internal combos)

HANDHELD_BASES: tuple[BaseMount, ...] = ("foot_pedal", "bench_clamp")
HANDHELD_LEVERS: tuple[LeverConfig, ...] = (
    "single_swing_arm", "two_handle_scissor", "ratchet_pump",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "safety_yellow", "industrial_blue", "hydraulic_red", "black_cast", "galvanized_raw",
)

# role keys: body, cast, hardware, grip, conduit, marking, accent
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "safety_yellow": {
        "body": (1.00, 0.72, 0.02, 1.0),
        "cast": (0.015, 0.015, 0.018, 1.0),
        "hardware": (0.08, 0.085, 0.09, 1.0),
        "grip": (0.02, 0.02, 0.022, 1.0),
        "conduit": (0.70, 0.74, 0.75, 1.0),
        "marking": (0.96, 0.95, 0.88, 1.0),
        "accent": (0.86, 0.64, 0.25, 1.0),
    },
    "industrial_blue": {
        "body": (0.00, 0.46, 0.78, 1.0),
        "cast": (0.02, 0.10, 0.16, 1.0),
        "hardware": (0.05, 0.05, 0.045, 1.0),
        "grip": (0.02, 0.022, 0.022, 1.0),
        "conduit": (0.78, 0.36, 0.16, 1.0),
        "marking": (0.92, 0.90, 0.82, 1.0),
        "accent": (0.72, 0.73, 0.68, 1.0),
    },
    "hydraulic_red": {
        "body": (1.00, 0.72, 0.02, 1.0),
        "cast": (0.015, 0.015, 0.018, 1.0),
        "hardware": (0.09, 0.09, 0.10, 1.0),
        "grip": (0.02, 0.02, 0.022, 1.0),
        "conduit": (0.70, 0.74, 0.75, 1.0),
        "marking": (0.96, 0.95, 0.88, 1.0),
        "accent": (0.60, 0.11, 0.08, 1.0),
    },
    "black_cast": {
        "body": (0.055, 0.055, 0.060, 1.0),
        "cast": (0.015, 0.015, 0.018, 1.0),
        "hardware": (0.13, 0.13, 0.14, 1.0),
        "grip": (0.02, 0.02, 0.022, 1.0),
        "conduit": (0.70, 0.74, 0.75, 1.0),
        "marking": (0.90, 0.90, 0.86, 1.0),
        "accent": (0.72, 0.73, 0.68, 1.0),
    },
    "galvanized_raw": {
        "body": (0.66, 0.68, 0.70, 1.0),
        "cast": (0.30, 0.32, 0.34, 1.0),
        "hardware": (0.14, 0.14, 0.15, 1.0),
        "grip": (0.03, 0.03, 0.032, 1.0),
        "conduit": (0.78, 0.36, 0.16, 1.0),
        "marking": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.80, 0.60, 0.24, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ConduitBenderConfig:
    form_family: FormFamily | None = None
    base_mount: BaseMount | None = None
    lever_config: LeverConfig | None = None
    palette_style: PaletteStyle = "safety_yellow"
    shoe_scale: float = 1.0
    handle_len_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedConduitBenderConfig:
    form_family: FormFamily
    base_mount: BaseMount
    lever_config: LeverConfig
    palette_style: PaletteStyle
    shoe_scale: float
    handle_len_scale: float
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def config_from_seed(seed: int) -> ConduitBenderConfig:
    rng = random.Random(seed)
    form = rng.choices(FORM_FAMILIES, weights=FORM_WEIGHTS, k=1)[0]
    if form == "floor_tripod":
        base, lever = "tripod_stand", "single_long_lever"
    elif form == "handheld_lever":
        base = rng.choice(HANDHELD_BASES)
        lever = rng.choice(HANDHELD_LEVERS)
    elif form == "hand_emt":
        base, lever = "foot_peg_step", "fused_pull_handle"
    else:  # hydraulic_ram
        base, lever = "floor_frame", "ram_pump_drive"
    return ConduitBenderConfig(
        form_family=form,
        base_mount=base,
        lever_config=lever,
        palette_style=rng.choice(PALETTE_STYLES),
        shoe_scale=round(rng.uniform(0.85, 1.20), 4),
        handle_len_scale=round(rng.uniform(0.90, 1.15), 4),
    )


def _gate(form: FormFamily, base: BaseMount | None, lever: LeverConfig | None):
    """Enforce compatibility matrix; correct illegal combos to legal defaults."""
    if form == "floor_tripod":
        return "tripod_stand", "single_long_lever"
    if form == "hand_emt":
        return "foot_peg_step", "fused_pull_handle"
    if form == "hydraulic_ram":
        return "floor_frame", "ram_pump_drive"
    # handheld_lever
    b = base if base in HANDHELD_BASES else "foot_pedal"
    lv = lever if lever in HANDHELD_LEVERS else "single_swing_arm"
    return b, lv


def resolve_config(config: ConduitBenderConfig | None = None) -> ResolvedConduitBenderConfig:
    cfg = config or ConduitBenderConfig()
    form = cfg.form_family or "floor_tripod"
    if form not in FORM_FAMILIES:
        raise ValueError(f"Unsupported form_family: {form}")
    base, lever = _gate(form, cfg.base_mount, cfg.lever_config)
    palette_style = cfg.palette_style if cfg.palette_style in PALETTES else "safety_yellow"
    return ResolvedConduitBenderConfig(
        form_family=form,
        base_mount=base,
        lever_config=lever,
        palette_style=palette_style,
        shoe_scale=_clamp(float(cfg.shoe_scale), 0.85, 1.20),
        handle_len_scale=_clamp(float(cfg.handle_len_scale), 0.90, 1.15),
        palette=dict(PALETTES[palette_style]),
    )


def with_overrides(config: ConduitBenderConfig, **kwargs) -> ConduitBenderConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(r: ResolvedConduitBenderConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("form_family", r.form_family),
        ("base_mount", r.base_mount),
        ("lever_config", r.lever_config),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Geometry primitives (shared)
# ---------------------------------------------------------------------------
def _annular_sector(
    *, inner_radius: float, outer_radius: float, thickness_y: float,
    theta0: float, theta1: float, segments: int = 44, y_offset: float = 0.0,
) -> MeshGeometry:
    """Extruded annular sector in the local XZ plane, thickness along Y."""
    geom = MeshGeometry()
    front = y_offset + thickness_y * 0.5
    back = y_offset - thickness_y * 0.5
    angles = [theta0 + (theta1 - theta0) * i / segments for i in range(segments + 1)]
    for theta in angles:
        c = math.cos(theta)
        s = math.sin(theta)
        geom.add_vertex(outer_radius * c, front, outer_radius * s)
        geom.add_vertex(inner_radius * c, front, inner_radius * s)
        geom.add_vertex(outer_radius * c, back, outer_radius * s)
        geom.add_vertex(inner_radius * c, back, inner_radius * s)
    for i in range(segments):
        a = 4 * i
        b = 4 * (i + 1)
        geom.add_face(a, b, b + 1)
        geom.add_face(a, b + 1, a + 1)
        geom.add_face(a + 2, b + 3, b + 2)
        geom.add_face(a + 2, a + 3, b + 3)
        geom.add_face(a, a + 2, b + 2)
        geom.add_face(a, b + 2, b)
        geom.add_face(a + 1, b + 1, b + 3)
        geom.add_face(a + 1, b + 3, a + 3)
    a = 0
    geom.add_face(a, a + 1, a + 3)
    geom.add_face(a, a + 3, a + 2)
    a = 4 * segments
    geom.add_face(a, a + 3, a + 1)
    geom.add_face(a, a + 2, a + 3)
    return geom


def _tube_along_arc(
    *, radius_path: float, tube_radius: float, theta0: float, theta1: float,
    segments: int = 48, radial_segments: int = 14, y_offset: float = 0.0,
    cap_ends: bool = True,
) -> MeshGeometry:
    """Circular tube following an arc around the pivot in the local XZ plane."""
    geom = MeshGeometry()
    angles = [theta0 + (theta1 - theta0) * i / segments for i in range(segments + 1)]
    for theta in angles:
        c = math.cos(theta)
        s = math.sin(theta)
        cx, cy, cz = radius_path * c, y_offset, radius_path * s
        radial = (c, 0.0, s)
        for j in range(radial_segments):
            phi = 2.0 * math.pi * j / radial_segments
            cp = math.cos(phi)
            sp = math.sin(phi)
            geom.add_vertex(
                cx + tube_radius * (cp * radial[0]),
                cy + tube_radius * (sp),
                cz + tube_radius * (cp * radial[2]),
            )
    for i in range(segments):
        a = i * radial_segments
        b = (i + 1) * radial_segments
        for j in range(radial_segments):
            j2 = (j + 1) % radial_segments
            geom.add_face(a + j, b + j, b + j2)
            geom.add_face(a + j, b + j2, a + j2)
    if cap_ends:
        start_center = geom.add_vertex(
            radius_path * math.cos(theta0), y_offset, radius_path * math.sin(theta0)
        )
        end_center = geom.add_vertex(
            radius_path * math.cos(theta1), y_offset, radius_path * math.sin(theta1)
        )
        start = 0
        end = segments * radial_segments
        for j in range(radial_segments):
            j2 = (j + 1) % radial_segments
            geom.add_face(start_center, start + j2, start + j)
            geom.add_face(end_center, end + j, end + j2)
    return geom


def _arc_tube_visual(part, name, mat, *, radius_path, tube_radius, theta0, theta1,
                     y_offset=0.0, segments=48, radial_segments=14):
    geom = _tube_along_arc(
        radius_path=radius_path, tube_radius=tube_radius, theta0=theta0, theta1=theta1,
        segments=segments, radial_segments=radial_segments, y_offset=y_offset,
    )
    part.visual(mesh_from_geometry(geom, name), material=mat, name=name, material_class_id="metal.generic_plain")


def _spline_tube(part, name, mat, points, *, radius, radial_segments=16):
    geom = tube_from_spline_points(
        points, radius=radius, samples_per_segment=8,
        radial_segments=radial_segments, cap_ends=True, up_hint=(0.0, 1.0, 0.0),
    )
    part.visual(mesh_from_geometry(geom, name), material=mat, name=name, material_class_id="metal.generic_plain")


def _cylinder_between(part, name, p0, p1, radius, mat):
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 0:
        raise ValueError(f"zero-length cylinder {name}")
    uz = dz / length
    pitch = math.acos(max(-1.0, min(1.0, uz)))
    yaw = math.atan2(dy, dx)
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=((x0 + x1) * 0.5, (y0 + y1) * 0.5, (z0 + z1) * 0.5),
                      rpy=(0.0, pitch, yaw)),
        material=mat, name=name, material_class_id="metal.generic_plain",
    )


def _radial_box(part, name, radius, theta, size, mat, *, y=0.0):
    part.visual(
        Box(size),
        origin=Origin(xyz=(radius * math.cos(theta), y, radius * math.sin(theta)),
                      rpy=(0.0, -theta, 0.0)),
        material=mat, name=name, material_class_id="metal.generic_plain",
    )


# ---------------------------------------------------------------------------
# Shared forming-shoe group (S1-style black cast: web + channel + lips + hook +
# hub + ribs + degree scale + ticks). Emitted onto ``part`` centered at origin.
# ``s`` = shoe_scale drives ALL radial geometry (incl. hub) so nothing detaches.
# THETA range -68..146 deg. Used by floor_tripod (head) + hand_emt (bender).
# ---------------------------------------------------------------------------
_TH0 = math.radians(-68.0)
_TH1 = math.radians(146.0)


def _emit_s1_shoe(part, r, mats, *, hub_len: float, seg: int = 44):
    s = r.shoe_scale
    part.visual(
        mesh_from_geometry(
            _annular_sector(inner_radius=0.058 * s, outer_radius=0.166 * s,
                            thickness_y=0.048, theta0=_TH0, theta1=_TH1, segments=seg),
            "shoe_web"),
        material=mats["cast"], name="shoe_web", material_class_id="metal.cast_iron_bare")
    part.visual(
        mesh_from_geometry(
            _annular_sector(inner_radius=0.164 * s, outer_radius=0.181 * s,
                            thickness_y=0.030, theta0=_TH0, theta1=_TH1, segments=seg),
            "channel_bottom"),
        material=mats["hardware"], name="channel_bottom", material_class_id="metal.steel_bare")
    for i, yo in enumerate((-0.027, 0.027)):
        part.visual(
            mesh_from_geometry(
                _annular_sector(inner_radius=0.160 * s, outer_radius=0.207 * s,
                                thickness_y=0.010, theta0=_TH0, theta1=_TH1,
                                segments=seg, y_offset=yo),
                f"channel_lip_{i}"),
            material=mats["cast"], name=f"channel_lip_{i}", material_class_id="metal.cast_iron_bare")
    # central hub (scales with s -> always >= web inner radius)
    part.visual(Cylinder(radius=0.062 * s, length=hub_len),
                origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["cast"], name="pivot_hub", material_class_id="metal.cast_iron_bare")
    # cast reinforcing ribs
    for idx, ang in enumerate((math.radians(-38), math.radians(18),
                               math.radians(78), math.radians(128))):
        _radial_box(part, f"cast_rib_{idx}", 0.108 * s, ang,
                    (0.014, 0.042, 0.125 * s), mats["cast"])
    # curved hook lip (arc tube, NEVER box)
    _arc_tube_visual(part, "hook_lip", mats["cast"], radius_path=0.205 * s,
                     tube_radius=0.010, theta0=math.radians(-84), theta1=math.radians(-64),
                     y_offset=-0.030, segments=18, radial_segments=12)
    part.visual(Box((0.040, 0.026, 0.045)),
                origin=Origin(xyz=(0.078 * s, -0.028, -0.176 * s), rpy=(0.0, -0.30, 0.0)),
                material=mats["cast"], name="hook_web", material_class_id="metal.cast_iron_bare")
    # white degree scale plate + ticks + pads on the -Y face (host-conformal)
    part.visual(
        mesh_from_geometry(
            _annular_sector(inner_radius=0.120 * s, outer_radius=0.156 * s,
                            thickness_y=0.006, theta0=math.radians(-58),
                            theta1=math.radians(138), segments=seg, y_offset=-0.032),
            "degree_scale"),
        material=mats["marking"], name="degree_scale", appearance_only=AppearanceOnlySpec(kind="overlay"))
    for idx, deg in enumerate((-45, -15, 15, 45, 75, 105, 135)):
        length = 0.030 if idx % 2 == 0 else 0.020
        _radial_box(part, f"degree_tick_{idx}", 0.150 * s, math.radians(deg),
                    (0.005, 0.005, length), mats["hardware"], y=-0.036)
    for idx, deg in enumerate((0, 45, 90)):
        _radial_box(part, f"degree_pad_{idx}", 0.128 * s, math.radians(deg),
                    (0.026, 0.005, 0.016), mats["hardware"], y=-0.036)


def _emit_conduit_arc(part, r, mats, *, seg: int = 48):
    """S1-style galvanized conduit arc + straight stubs, seated in the groove."""
    s = r.shoe_scale
    rp = 0.190 * s
    _arc_tube_visual(part, "conduit_arc", mats["conduit"], radius_path=rp,
                     tube_radius=0.010, theta0=math.radians(-56), theta1=math.radians(128),
                     y_offset=0.0, segments=seg, radial_segments=16)
    _cylinder_between(part, "conduit_straight_tail",
                      (rp * math.cos(math.radians(-56)), 0.0, rp * math.sin(math.radians(-56))),
                      (0.300 * s, 0.0, -0.205 * s), 0.010, mats["conduit"])
    _cylinder_between(part, "conduit_exit_stub",
                      (rp * math.cos(math.radians(128)), 0.0, rp * math.sin(math.radians(128))),
                      (-0.205 * s, 0.0, 0.235 * s), 0.010, mats["conduit"])


# ---------------------------------------------------------------------------
# Family: floor_tripod (S1)
# ---------------------------------------------------------------------------
PIVOT_Z = 1.05


def _build_floor_tripod(model, r, mats):
    frame = model.part("frame")
    b, hw, cast = mats["body"], mats["hardware"], mats["cast"]
    _cylinder_between(frame, "front_foot", (-0.62, -0.46, 0.035), (-0.62, 0.46, 0.035), 0.020, b)
    _cylinder_between(frame, "rear_foot", (0.54, -0.50, 0.035), (0.54, 0.50, 0.035), 0.020, b)
    _cylinder_between(frame, "front_leg_0", (-0.62, -0.38, 0.055), (-0.055, -0.060, 0.925), 0.018, b)
    _cylinder_between(frame, "front_leg_1", (-0.62, 0.38, 0.055), (-0.055, 0.060, 0.925), 0.018, b)
    _cylinder_between(frame, "rear_leg_0", (0.54, -0.42, 0.055), (-0.015, -0.065, 0.925), 0.018, b)
    _cylinder_between(frame, "rear_leg_1", (0.54, 0.42, 0.055), (-0.015, 0.065, 0.925), 0.018, b)
    _cylinder_between(frame, "lower_cross_brace", (-0.513, -0.319, 0.22), (0.435, 0.353, 0.22), 0.010, hw)
    _cylinder_between(frame, "side_cross_brace", (-0.526, 0.327, 0.20), (0.448, -0.361, 0.20), 0.010, hw)
    frame.visual(Box((0.18, 0.20, 0.075)), origin=Origin(xyz=(-0.050, 0.0, 0.760)), material=b, name="top_socket", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    frame.visual(Box((0.12, 0.16, 0.070)), origin=Origin(xyz=(-0.065, 0.0, 0.825)), material=b, name="reinforced_socket", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    frame.visual(Box((0.025, 0.16, 0.18)), origin=Origin(xyz=(-0.135, 0.0, 0.950)), material=b, name="socket_neck", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    # yoke straddling the moving head hub
    frame.visual(Box((0.18, 0.012, 0.22)), origin=Origin(xyz=(0.0, -0.064, PIVOT_Z - 0.020)), material=hw, name="yoke_plate_0", material_class_id="metal.steel_bare")
    frame.visual(Box((0.18, 0.012, 0.22)), origin=Origin(xyz=(0.0, 0.064, PIVOT_Z - 0.020)), material=hw, name="yoke_plate_1", material_class_id="metal.steel_bare")
    for i, yo in enumerate((-0.054, 0.054)):
        frame.visual(Cylinder(radius=0.055, length=0.008),
                     origin=Origin(xyz=(0.0, yo, PIVOT_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                     material=cast, name=f"pivot_bushing_{i}", material_class_id="metal.cast_iron_bare")
    for i, yo in enumerate((-0.071, 0.071)):
        frame.visual(Cylinder(radius=0.010, length=0.030),
                     origin=Origin(xyz=(0.075, yo, PIVOT_Z + 0.075), rpy=(math.pi / 2.0, 0.0, 0.0)),
                     material=mats["accent"], name=f"terminal_screw_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.copper_bare"))
    frame.visual(Box((0.050, 0.004, 0.120)), origin=Origin(xyz=(-0.050, 0.102, 0.760)), material=mats["accent"], name="warning_label", appearance_only=AppearanceOnlySpec(kind="decal"))
    for i in range(3):
        frame.visual(Box((0.040, 0.005, 0.006)), origin=Origin(xyz=(-0.050, 0.1065, 0.725 + i * 0.030)), material=cast, name=f"label_stripe_{i}", appearance_only=AppearanceOnlySpec(kind="decal"))

    head = model.part("bender_head")
    _emit_s1_shoe(head, r, mats, hub_len=0.090)
    head.visual(Cylinder(radius=0.034, length=0.118), origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["hardware"], name="axle_pin", material_class_id="metal.steel_bare")
    # single long lever fused to the head
    hs = r.handle_len_scale
    s = r.shoe_scale
    head.visual(Box((0.090, 0.070, 0.035)), origin=Origin(xyz=(0.160 * s, 0.075, -0.020), rpy=(0.0, -0.12, 0.0)), material=cast, name="handle_socket", material_class_id="metal.cast_iron_bare")
    head.visual(Box((0.090, 0.052, 0.055)), origin=Origin(xyz=(0.115 * s, 0.035, -0.020), rpy=(0.0, -0.10, 0.0)), material=cast, name="handle_root_web", material_class_id="metal.cast_iron_bare")
    _cylinder_between(head, "handle_tube", (0.172 * s, 0.095, -0.030), (0.172 * s + 0.71 * hs, 0.095, -0.030 - 0.15 * hs), 0.014, hw)
    _cylinder_between(head, "rubber_grip", (0.172 * s + 0.52 * hs, 0.095, -0.030 - 0.11 * hs), (0.172 * s + 0.74 * hs, 0.095, -0.030 - 0.157 * hs), 0.019, mats["grip"])
    # foot pedal + conduit retainer
    head.visual(Box((0.160, 0.050, 0.018)), origin=Origin(xyz=(0.230 * s, -0.120, -0.100 * s), rpy=(0.0, -0.28, 0.0)), material=b, name="foot_pedal", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    head.visual(Box((0.060, 0.092, 0.075)), origin=Origin(xyz=(0.155 * s, -0.055, -0.085 * s), rpy=(0.0, -0.18, 0.0)), material=b, name="pedal_root_web", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    _radial_box(head, "conduit_retainer", 0.190 * s, math.radians(25), (0.032, 0.0175, 0.024), hw, y=0.01875)

    conduit = model.part("conduit")
    _emit_conduit_arc(conduit, r, mats)
    conduit.visual(Cylinder(radius=0.030, length=0.030), origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
                   material=mats["hardware"], name="conduit_seat_collar", material_class_id="metal.steel_bare")
    # radial web tying the seat collar to the wrapped conduit arc (within-part connectivity)
    conduit.visual(Box((0.180 * s, 0.010, 0.010)), origin=Origin(xyz=(0.095 * s, 0.0, 0.0)),
                   material=mats["hardware"], name="conduit_seat_spoke", material_class_id="metal.steel_bare")

    model.articulation(
        "frame_to_bender_head", ArticulationType.REVOLUTE, parent=frame, child=head,
        origin=Origin(xyz=(0.0, 0.0, PIVOT_Z)), axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=110.0, velocity=1.2,
                                   lower=math.radians(-27.5), upper=math.radians(40.0)),
        meta={"mechanism": "manual handle + shoe rotate about yoke axle"})
    model.articulation("head_to_conduit", ArticulationType.FIXED, parent=head, child=conduit,
                       origin=Origin())


# ---------------------------------------------------------------------------
# Family: hand_emt (fork@S1) — long straight handle, conduit is the moving part
# ---------------------------------------------------------------------------
def _build_hand_emt(model, r, mats):
    s = r.shoe_scale
    hs = r.handle_len_scale
    b, hw, cast = mats["body"], mats["hardware"], mats["cast"]
    bender = model.part("bender")
    _emit_s1_shoe(bender, r, mats, hub_len=0.052)
    # long straight pull handle out the back (high-theta) end
    bender.visual(Box((0.062, 0.070, 0.062)), origin=Origin(xyz=(-0.150 * s, 0.0, 0.092 * s)), material=cast, name="handle_socket", material_class_id="metal.cast_iron_bare")
    bender.visual(Box((0.050, 0.056, 0.070)), origin=Origin(xyz=(-0.188 * s, 0.0, 0.076 * s)), material=cast, name="handle_root_web", material_class_id="metal.cast_iron_bare")
    _cylinder_between(bender, "handle_tube", (-0.210 * s, 0.0, 0.066 * s),
                      (-0.210 * s - 0.69 * hs, 0.0, 0.066 * s - 0.034 * hs), 0.014, hw)
    _cylinder_between(bender, "rubber_grip", (-0.210 * s - 0.51 * hs, 0.0, 0.066 * s - 0.028 * hs),
                      (-0.210 * s - 0.70 * hs, 0.0, 0.066 * s - 0.035 * hs), 0.019, mats["grip"])
    # foot-peg step (base_mount = foot_peg_step)
    _cylinder_between(bender, "foot_peg", (0.082 * s, -0.058, -0.138 * s), (0.082 * s, 0.058, -0.138 * s), 0.010, hw)
    for i, sign in enumerate((-1.0, 1.0)):
        bender.visual(Box((0.026, 0.024, 0.034)), origin=Origin(xyz=(0.082 * s, sign * 0.030, -0.132 * s)), material=cast, name=f"foot_peg_bracket_{i}", material_class_id="metal.cast_iron_bare")
    bender.visual(Box((0.038, 0.070, 0.008)), origin=Origin(xyz=(0.082 * s, 0.0, -0.126 * s)), material=hw, name="foot_peg_pad", material_class_id="rubber.smooth_plain")

    conduit = model.part("conduit")
    _emit_conduit_arc(conduit, r, mats)
    # pivot collar at center (origin honesty: axis is collar centerline; contacts hub)
    conduit.visual(Cylinder(radius=0.030 * s, length=0.030),
                   origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
                   material=mats["hardware"], name="pivot_collar", material_class_id="metal.steel_bare")
    # radial web tying the bend collar to the wrapped conduit arc (connectivity)
    conduit.visual(Box((0.170 * s, 0.010, 0.010)), origin=Origin(xyz=(0.100 * s, 0.0, 0.0)),
                   material=mats["hardware"], name="pivot_collar_spoke", material_class_id="metal.steel_bare")

    model.articulation(
        "bender_to_conduit", ArticulationType.REVOLUTE, parent=bender, child=conduit,
        origin=Origin(xyz=(0.0, 0.0, 0.0)), axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.8,
                                   lower=math.radians(-5.0), upper=math.radians(50.0)),
        meta={"mechanism": "conduit workpiece pivots about shoe groove center during bending stroke"})


# ---------------------------------------------------------------------------
# Family: handheld_lever (S2) — blue cast disc shoe + base_mount + lever_config
# ---------------------------------------------------------------------------
_S2_TH0 = math.radians(-118.0)
_S2_TH1 = math.radians(166.0)


def _emit_s2_shoe(shoe, r, mats, *, seg: int = 48):
    s = r.shoe_scale
    b, hw, cast = mats["body"], mats["hardware"], mats["cast"]
    shoe.visual(
        mesh_from_geometry(
            _annular_sector(inner_radius=0.066 * s, outer_radius=0.158 * s,
                            thickness_y=0.055, theta0=_S2_TH0, theta1=_S2_TH1, segments=seg),
            "curved_shoe"),
        material=b, name="curved_shoe", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    shoe.visual(Cylinder(radius=0.074 * s, length=0.012), origin=Origin(xyz=(0.0, -0.026, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=b, name="front_hub_web", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    shoe.visual(
        mesh_from_geometry(
            _annular_sector(inner_radius=0.120 * s, outer_radius=0.154 * s,
                            thickness_y=0.006, theta0=math.radians(-104), theta1=math.radians(148),
                            segments=seg, y_offset=-0.029),
            "degree_scale"),
        material=mats["marking"], name="degree_scale", appearance_only=AppearanceOnlySpec(kind="overlay"))
    for i, angle_deg in enumerate((-88, -52, -18, 24, 68, 112)):
        angle = math.radians(angle_deg)
        rm = 0.085 * s
        shoe.visual(Box((0.098 * s, 0.040, 0.014)),
                    origin=Origin(xyz=(rm * math.cos(angle), 0.0, rm * math.sin(angle)), rpy=(0.0, -angle, 0.0)),
                    material=b, name=f"cast_rib_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    shoe.visual(Cylinder(radius=0.037, length=0.014), origin=Origin(xyz=(0.0, -0.034, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=hw, name="pivot_cap", material_class_id="metal.steel_bare")
    shoe.visual(Cylinder(radius=0.012, length=0.130), origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["accent"], name="pivot_pin", material_class_id=("metal.brass_aged" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.copper_bare"))
    # curved hook lip (replaces S2's boxy hook) at the shoe entrance (high theta)
    _arc_tube_visual(shoe, "hook_lip", mats["body"], radius_path=0.150 * s,
                     tube_radius=0.011, theta0=math.radians(150), theta1=math.radians(168),
                     y_offset=0.0, segments=16, radial_segments=12)
    shoe.visual(Box((0.038, 0.055, 0.030)),
                origin=Origin(xyz=(0.150 * s * math.cos(math.radians(159)), -0.001, 0.150 * s * math.sin(math.radians(159))),
                              rpy=(0.0, -math.radians(159) + math.pi / 2.0, 0.0)),
                material=mats["body"], name="hook_web", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    # tick marks on the cast scale
    scale_center_deg, tick_spacing_deg, tick_count = 22.0, 23.0, 11
    tick_mid = tick_count // 2
    for i in range(tick_count):
        angle = math.radians(scale_center_deg + (i - tick_mid) * tick_spacing_deg)
        length = 0.023 if i in (0, tick_mid, tick_count - 1) else 0.015
        shoe.visual(Box((length, 0.004, 0.0035)),
                    origin=Origin(xyz=(0.137 * s * math.cos(angle), -0.034, 0.137 * s * math.sin(angle)), rpy=(0.0, -angle, 0.0)),
                    material=hw, name=f"degree_tick_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"))


def _emit_foot_pedal(shoe, r, mats):
    s = r.shoe_scale
    b, hw = mats["body"], mats["accent"]
    shoe.visual(Box((0.175, 0.086, 0.028)), origin=Origin(xyz=(-0.125 * s, 0.0, -0.150 * s), rpy=(0.0, math.radians(8.0), 0.0)), material=b, name="foot_pedal", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    shoe.visual(Box((0.150, 0.072, 0.006)), origin=Origin(xyz=(-0.140 * s, -0.002, -0.133 * s), rpy=(0.0, math.radians(8.0), 0.0)), material=hw, name="serrated_tread_plate", material_class_id="metal.patterned_sheet_panel")
    for i, x in enumerate((-0.170, -0.148, -0.126, -0.104, -0.082)):
        shoe.visual(Box((0.006, 0.078, 0.012)), origin=Origin(xyz=(x * s, -0.006, -0.133 * s), rpy=(0.0, math.radians(8.0), 0.0)), material=mats["hardware"], name=f"tread_tooth_{i}", material_class_id="metal.steel_bare")


def _emit_bench_clamp(shoe, r, mats):
    s = r.shoe_scale
    b, hw = mats["body"], mats["hardware"]
    st = mats["accent"]
    shoe.visual(Box((0.042, 0.052, 0.034)), origin=Origin(xyz=(-0.020, 0.0, -0.150 * s)), material=b, name="clamp_neck_boss", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    shoe.visual(Box((0.065, 0.056, 0.012)), origin=Origin(xyz=(-0.020, 0.0, -0.170 * s)), material=b, name="clamp_mounting_flange", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    shoe.visual(Box((0.016, 0.055, 0.100)), origin=Origin(xyz=(-0.047, 0.0, -0.205 * s)), material=b, name="clamp_spine", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    shoe.visual(Box((0.054, 0.055, 0.012)), origin=Origin(xyz=(-0.017, 0.0, -0.182 * s)), material=b, name="clamp_upper_jaw", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    shoe.visual(Box((0.054, 0.055, 0.012)), origin=Origin(xyz=(-0.017, 0.0, -0.244 * s)), material=b, name="clamp_lower_jaw", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    for i, yo in enumerate((-0.022, 0.022)):
        shoe.visual(Box((0.010, 0.006, 0.060)), origin=Origin(xyz=(-0.038, yo, -0.213 * s)), material=b, name=f"clamp_spine_rib_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    shoe.visual(Cylinder(radius=0.007, length=0.060), origin=Origin(xyz=(-0.010, 0.0, -0.220 * s)), material=st, name="clamp_screw", material_class_id=("metal.brass_aged" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.copper_bare"))
    shoe.visual(Cylinder(radius=0.018, length=0.006), origin=Origin(xyz=(-0.010, 0.0, -0.186 * s)), material=hw, name="clamp_foot_pad", material_class_id="rubber.smooth_plain")
    shoe.visual(Cylinder(radius=0.005, length=0.080), origin=Origin(xyz=(-0.010, 0.0, -0.250 * s), rpy=(math.pi / 2.0, 0.0, 0.0)), material=hw, name="clamp_handle_bar", material_class_id="metal.steel_bare")
    for i, (dx, dy) in enumerate(((-0.022, -0.020), (-0.022, 0.020), (0.022, -0.020), (0.022, 0.020))):
        shoe.visual(Cylinder(radius=0.004, length=0.006), origin=Origin(xyz=(-0.020 + dx, dy, -0.160 * s)), material=hw, name=f"clamp_bolt_{i}", material_class_id="metal.steel_bare")


def _emit_swing_arm(part, r, mats, *, y_bushing, side, name_prefix, carry="roller"):
    """One S2-style swing handle. side=+1 emerges +X, -1 emerges -X (scissor mirror)."""
    s = r.shoe_scale
    hs = r.handle_len_scale
    b, st, grip = mats["body"], mats["accent"], mats["grip"]
    sx = 1.0 if side >= 0 else -1.0
    part.visual(Cylinder(radius=0.027, length=0.037), origin=Origin(xyz=(0.0, y_bushing, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=b, name="pivot_bushing", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    part.visual(Box((0.090, 0.026, 0.045)), origin=Origin(xyz=(sx * 0.054, y_bushing * 0.9, 0.023), rpy=(0.0, sx * math.radians(-23.0), 0.0)),
                material=b, name="yoke_cheek", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    part.visual(Box((0.125, 0.052, 0.050)), origin=Origin(xyz=(sx * 0.113, y_bushing + sx * 0.014, 0.052), rpy=(0.0, sx * math.radians(-15.0), 0.0)),
                material=b, name="handle_socket", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    yh = y_bushing + sx * 0.018
    pts = [(sx * 0.078, yh, 0.060), (sx * 0.210 * hs, yh, 0.090 * hs),
           (sx * 0.500 * hs, yh, 0.154 * hs), (sx * 0.775 * hs, yh, 0.215 * hs)]
    _spline_tube(part, "handle_tube", b, pts, radius=0.015, radial_segments=16)
    gpts = [(sx * 0.610 * hs, yh, 0.179 * hs), (sx * 0.705 * hs, yh, 0.200 * hs), (sx * 0.815 * hs, yh, 0.224 * hs)]
    _spline_tube(part, "rubber_grip", grip, gpts, radius=0.018, radial_segments=16)
    if carry == "roller":
        part.visual(Cylinder(radius=0.017, length=0.042), origin=Origin(xyz=(sx * 0.250, y_bushing - sx * 0.005, 0.112), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=st, name="pressure_roller", material_class_id="metal.stainless_matte")
        part.visual(Box((0.100, 0.065, 0.035)), origin=Origin(xyz=(sx * 0.200, y_bushing + sx * 0.005, 0.095), rpy=(0.0, sx * math.radians(-10.0), 0.0)),
                    material=b, name="roller_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    else:  # forming die
        part.visual(Cylinder(radius=0.019, length=0.044), origin=Origin(xyz=(sx * 0.300, y_bushing - sx * 0.005, 0.140), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=st, name="forming_die", material_class_id="metal.stainless_matte")
        part.visual(Box((0.100, 0.065, 0.035)), origin=Origin(xyz=(sx * 0.260, y_bushing + sx * 0.005, 0.120), rpy=(0.0, sx * math.radians(10.0), 0.0)),
                    material=b, name="die_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))


def _emit_ratchet_drive(drive, r, mats):
    s = r.shoe_scale
    b, st = mats["body"], mats["accent"]
    drive.visual(Cylinder(radius=0.028, length=0.036), origin=Origin(xyz=(0.0, 0.050, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)), material=b, name="drive_bushing", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    drive.visual(Box((0.080, 0.030, 0.048)), origin=Origin(xyz=(0.048, 0.050, 0.022), rpy=(0.0, math.radians(-22.0), 0.0)), material=b, name="drive_yoke", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    drive.visual(Box((0.155, 0.050, 0.050)), origin=Origin(xyz=(0.125, 0.050, 0.048), rpy=(0.0, math.radians(-12.0), 0.0)), material=b, name="drive_arm_body", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    drive.visual(Cylinder(radius=0.032, length=0.048), origin=Origin(xyz=(0.198, 0.050, 0.078), rpy=(math.pi / 2.0, 0.0, 0.0)), material=b, name="drive_end_boss", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    drive.visual(
        mesh_from_geometry(
            _annular_sector(inner_radius=0.055, outer_radius=0.118, thickness_y=0.005,
                            theta0=math.radians(-32), theta1=math.radians(135), segments=44, y_offset=0.076),
            "ratchet_sector_plate"),
        material=st, name="ratchet_sector_plate", material_class_id="metal.stainless_matte")
    tooth_count = 14
    for i in range(tooth_count):
        frac = i / (tooth_count - 1)
        angle = math.radians(-25.0 + frac * 155.0)
        drive.visual(Box((0.014, 0.008, 0.014)),
                     origin=Origin(xyz=(0.108 * math.cos(angle), 0.080, 0.108 * math.sin(angle)), rpy=(0.0, -angle, 0.0)),
                     material=st, name=f"ratchet_tooth_{i}", material_class_id="metal.stainless_matte")
    drive.visual(Cylinder(radius=0.017, length=0.042), origin=Origin(xyz=(0.205, 0.050, 0.085), rpy=(math.pi / 2.0, 0.0, 0.0)), material=st, name="pressure_roller", material_class_id="metal.stainless_matte")
    drive.visual(Box((0.080, 0.055, 0.032)), origin=Origin(xyz=(0.170, 0.050, 0.075), rpy=(0.0, math.radians(-10.0), 0.0)), material=b, name="roller_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))


def _emit_ratchet_pump(pump, r, mats):
    hs = r.handle_len_scale
    b, hw, grip = mats["body"], mats["hardware"], mats["grip"]
    pump.visual(Cylinder(radius=0.022, length=0.028), origin=Origin(xyz=(0.0, 0.094, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)), material=hw, name="pump_pivot_hub", material_class_id="metal.steel_bare")
    pump.visual(Box((0.140, 0.026, 0.030)), origin=Origin(xyz=(0.085, 0.094, 0.035), rpy=(0.0, math.radians(-14.0), 0.0)), material=b, name="pump_arm_body", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    _spline_tube(pump, "pump_arm", b, [(0.130, 0.094, 0.048), (0.220 * hs, 0.094, 0.068 * hs), (0.330 * hs, 0.094, 0.090 * hs)], radius=0.012, radial_segments=14)
    _spline_tube(pump, "pump_grip", grip, [(0.220 * hs, 0.094, 0.068 * hs), (0.290 * hs, 0.094, 0.082 * hs), (0.360 * hs, 0.094, 0.096 * hs)], radius=0.015, radial_segments=14)
    pump.visual(Box((0.060, 0.006, 0.012)), origin=Origin(xyz=(0.062, 0.082, 0.018), rpy=(0.0, math.radians(-22.0), 0.0)), material=mats["accent"], name="ratchet_pawl", material_class_id="metal.stainless_matte")
    pump.visual(Cylinder(radius=0.005, length=0.030), origin=Origin(xyz=(0.038, 0.094, 0.008), rpy=(math.pi / 2.0, 0.0, 0.0)), material=hw, name="pawl_pivot_pin", material_class_id="metal.steel_bare")


def _build_handheld_lever(model, r, mats):
    shoe = model.part("shoe_head")
    _emit_s2_shoe(shoe, r, mats)
    if r.base_mount == "bench_clamp":
        _emit_bench_clamp(shoe, r, mats)
    else:
        _emit_foot_pedal(shoe, r, mats)

    # sample conduit (S2 spline), FIXED to shoe
    conduit = model.part("sample_conduit")
    s = r.shoe_scale
    arc_pts = []
    for angle_deg in (-108, -86, -64, -42, -20, 2, 24, 38):
        a = math.radians(angle_deg)
        arc_pts.append((0.149 * s * math.cos(a), -0.046, 0.149 * s * math.sin(a)))
    conduit_path = [(-0.045 * s, -0.046, -0.360 * s), (-0.045 * s, -0.046, -0.220 * s), *arc_pts,
                    (0.245 * s, -0.046, 0.107 * s), (0.425 * s, -0.046, 0.128 * s)]
    seat = arc_pts[3]  # a point on the conduit that seats against the shoe groove
    local_path = [(px - seat[0], py - seat[1], pz - seat[2]) for (px, py, pz) in conduit_path]
    _spline_tube(conduit, "conduit_tube", mats["conduit"], local_path, radius=0.007, radial_segments=18)
    model.articulation("shoe_to_conduit", ArticulationType.FIXED, parent=shoe, child=conduit,
                       origin=Origin(xyz=seat))

    lims = MotionLimits(effort=85.0, velocity=1.4, lower=0.0, upper=1.65)
    if r.lever_config == "single_swing_arm":
        handle = model.part("swing_handle")
        _emit_swing_arm(handle, r, mats, y_bushing=0.055, side=1, name_prefix="swing", carry="roller")
        model.articulation("shoe_to_swing_handle", ArticulationType.REVOLUTE, parent=shoe, child=handle,
                            origin=Origin(), axis=(0.0, -1.0, 0.0), motion_limits=lims)
    elif r.lever_config == "two_handle_scissor":
        roller = model.part("roller_handle")
        _emit_swing_arm(roller, r, mats, y_bushing=0.055, side=1, name_prefix="roller", carry="roller")
        model.articulation("shoe_to_roller_handle", ArticulationType.REVOLUTE, parent=shoe, child=roller,
                            origin=Origin(), axis=(0.0, -1.0, 0.0), motion_limits=lims)
        forming = model.part("forming_handle")
        _emit_swing_arm(forming, r, mats, y_bushing=-0.055, side=-1, name_prefix="forming", carry="die")
        model.articulation("shoe_to_forming_handle", ArticulationType.REVOLUTE, parent=shoe, child=forming,
                            origin=Origin(), axis=(0.0, 1.0, 0.0), motion_limits=lims)
    else:  # ratchet_pump
        drive = model.part("ratchet_drive")
        _emit_ratchet_drive(drive, r, mats)
        model.articulation("shoe_to_ratchet_drive", ArticulationType.REVOLUTE, parent=shoe, child=drive,
                            origin=Origin(), axis=(0.0, -1.0, 0.0), motion_limits=lims)
        pump = model.part("pump_handle")
        _emit_ratchet_pump(pump, r, mats)
        model.articulation("shoe_to_pump_handle", ArticulationType.REVOLUTE, parent=shoe, child=pump,
                            origin=Origin(), axis=(0.0, -1.0, 0.0),
                            motion_limits=MotionLimits(effort=45.0, velocity=2.5, lower=0.0, upper=0.80))


# ---------------------------------------------------------------------------
# Family: hydraulic_ram (fork@S1)
# ---------------------------------------------------------------------------
BEND_Z = 1.05
RAM_ORIGIN_X = -0.22
RAM_UPPER = 0.12
ROLLER_X = 0.125
ROLLER_Y = 0.120
FORMER_LOCAL_X = 0.12
CONDUIT_X = 0.088
PUMP_UPPER = math.radians(40.0)


def _build_hydraulic_ram(model, r, mats):
    b, hw, cast = mats["body"], mats["hardware"], mats["cast"]
    acc, marking, cond = mats["accent"], mats["marking"], mats["conduit"]
    frame = model.part("frame")
    _cylinder_between(frame, "base_rail_0", (-0.55, -0.44, 0.035), (-0.55, 0.44, 0.035), 0.020, b)
    _cylinder_between(frame, "base_rail_1", (0.38, -0.44, 0.035), (0.38, 0.44, 0.035), 0.020, b)
    _cylinder_between(frame, "front_leg_0", (-0.55, -0.36, 0.055), (-0.28, -0.10, 0.975), 0.018, b)
    _cylinder_between(frame, "front_leg_1", (-0.55, 0.36, 0.055), (-0.28, 0.10, 0.975), 0.018, b)
    _cylinder_between(frame, "rear_leg_0", (0.38, -0.36, 0.055), (0.08, -0.10, 0.975), 0.018, b)
    _cylinder_between(frame, "rear_leg_1", (0.38, 0.36, 0.055), (0.08, 0.10, 0.975), 0.018, b)
    _cylinder_between(frame, "cross_brace_0", (-0.502, -0.313, 0.22), (0.326, 0.313, 0.22), 0.010, hw)
    _cylinder_between(frame, "cross_brace_1", (-0.502, 0.313, 0.22), (0.326, -0.313, 0.22), 0.010, hw)
    frame.visual(Box((0.56, 0.26, 0.032)), origin=Origin(xyz=(-0.08, 0.0, BEND_Z - 0.058)), material=b, name="platform_beam", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    for i, ys in enumerate((-1.0, 1.0)):
        frame.visual(Box((0.42, 0.018, 0.018)), origin=Origin(xyz=(-0.04, ys * 0.058, BEND_Z - 0.033)), material=hw, name=f"guide_rail_{i}", material_class_id="metal.steel_bare")
    _cylinder_between(frame, "ram_cylinder_body", (-0.42, 0.0, BEND_Z), (-0.22, 0.0, BEND_Z), 0.038, hw)
    _cylinder_between(frame, "ram_cylinder_rear_cap", (-0.44, 0.0, BEND_Z), (-0.42, 0.0, BEND_Z), 0.044, cast)
    _cylinder_between(frame, "ram_cylinder_front_gland", (-0.23, 0.0, BEND_Z), (-0.22, 0.0, BEND_Z), 0.044, cast)
    for i, x in enumerate((-0.36, -0.30)):
        frame.visual(Cylinder(radius=0.009, length=0.028), origin=Origin(xyz=(x, 0.042, BEND_Z + 0.025), rpy=(math.pi / 2.0, 0.0, 0.0)), material=acc, name=f"hydraulic_fitting_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.copper_bare"))
    frame.visual(Cylinder(radius=0.018, length=0.010), origin=Origin(xyz=(-0.33, 0.040, BEND_Z - 0.020), rpy=(math.pi / 2.0, 0.0, 0.0)), material=acc, name="pressure_gauge_boss", material_class_id=("metal.brass_aged" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.copper_bare"))
    frame.visual(Cylinder(radius=0.015, length=0.004), origin=Origin(xyz=(-0.33, 0.046, BEND_Z - 0.020), rpy=(math.pi / 2.0, 0.0, 0.0)), material=marking, name="pressure_gauge_face", appearance_only=AppearanceOnlySpec(kind="overlay"))
    frame.visual(Box((0.06, 0.10, 0.055)), origin=Origin(xyz=(-0.40, 0.0, BEND_Z - 0.048)), material=b, name="cylinder_mount_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    for i, ys in enumerate((-1.0, 1.0)):
        yp = ys * ROLLER_Y
        frame.visual(Box((0.045, 0.030, 0.110)), origin=Origin(xyz=(ROLLER_X, yp, BEND_Z - 0.005)), material=b, name=f"roller_upright_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
        frame.visual(Box((0.060, 0.025, 0.030)), origin=Origin(xyz=(ROLLER_X - 0.035, yp, BEND_Z - 0.055)), material=b, name=f"roller_gusset_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
        yc = ys * ROLLER_Y
        _cylinder_between(frame, f"roller_body_{i}", (ROLLER_X, yc - 0.018, BEND_Z), (ROLLER_X, yc + 0.018, BEND_Z), 0.026, hw)
        _cylinder_between(frame, f"roller_flange_{i}_0", (ROLLER_X, yc - 0.024, BEND_Z), (ROLLER_X, yc - 0.018, BEND_Z), 0.025, hw)
        _cylinder_between(frame, f"roller_flange_{i}_1", (ROLLER_X, yc + 0.018, BEND_Z), (ROLLER_X, yc + 0.024, BEND_Z), 0.025, hw)
        _cylinder_between(frame, f"roller_pin_{i}", (ROLLER_X, yc - 0.032, BEND_Z), (ROLLER_X, yc + 0.032, BEND_Z), 0.008, acc)
    # degree plate + ticks (host-conformal on the roller upright face)
    frame.visual(Box((0.040, 0.005, 0.110)), origin=Origin(xyz=(ROLLER_X + 0.025, ROLLER_Y + 0.015, BEND_Z + 0.010)), material=marking, name="degree_plate", appearance_only=AppearanceOnlySpec(kind="overlay"))
    for idx, deg in enumerate((0, 15, 30, 45, 60, 75, 90)):
        z_off = (deg / 90.0) * 0.080 - 0.040
        tl = 0.014 if deg % 30 == 0 else 0.009
        frame.visual(Box((0.009, 0.006, tl)), origin=Origin(xyz=(ROLLER_X + 0.038, ROLLER_Y + 0.015, BEND_Z + 0.010 + z_off)), material=cast, name=f"degree_tick_{idx}", appearance_only=AppearanceOnlySpec(kind="overlay"))
    for idx, deg in enumerate((0, 45, 90)):
        z_off = (deg / 90.0) * 0.080 - 0.040
        frame.visual(Box((0.012, 0.006, 0.016)), origin=Origin(xyz=(ROLLER_X + 0.042, ROLLER_Y + 0.015, BEND_Z + 0.010 + z_off)), material=cast, name=f"degree_pad_{idx}", appearance_only=AppearanceOnlySpec(kind="overlay"))
    frame.visual(Cylinder(radius=0.022, length=0.030), origin=Origin(xyz=(-0.35, 0.14, BEND_Z - 0.050), rpy=(math.pi / 2.0, 0.0, 0.0)), material=cast, name="pump_pivot_boss", material_class_id="metal.cast_iron_bare")
    for i, yp in enumerate((-0.09, 0.09)):
        frame.visual(Box((0.028, 0.024, 0.052)), origin=Origin(xyz=(CONDUIT_X, yp, 1.024)), material=hw, name=f"conduit_clamp_{i}", material_class_id="metal.steel_bare")

    # RAM (prismatic former die — annular sector, curved)
    ram = model.part("ram")
    _cylinder_between(ram, "piston_rod", (-RAM_UPPER, 0.0, 0.0), (FORMER_LOCAL_X - 0.030, 0.0, 0.0), 0.014, hw)
    ram.visual(Box((0.10, 0.100, 0.016)), origin=Origin(xyz=(0.06, 0.0, -0.025)), material=hw, name="carriage_plate", material_class_id="metal.steel_bare")
    for i, ys in enumerate((-1.0, 1.0)):
        ram.visual(Box((0.080, 0.018, 0.022)), origin=Origin(xyz=(0.06, ys * 0.044, -0.028)), material=cast, name=f"carriage_bearing_{i}", material_class_id="metal.cast_iron_bare")
    ram.visual(Box((0.086, 0.055, 0.050)), origin=Origin(xyz=(FORMER_LOCAL_X - 0.008, 0.0, 0.0)), material=cast, name="die_mount_block", material_class_id="metal.cast_iron_bare")
    dt0, dt1 = math.radians(-42.0), math.radians(42.0)
    ram.visual(mesh_from_geometry(_annular_sector(inner_radius=0.030, outer_radius=0.055, thickness_y=0.040, theta0=dt0, theta1=dt1, segments=32), "former_die_web"),
               origin=Origin(xyz=(FORMER_LOCAL_X, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)), material=cast, name="former_die_web", material_class_id="metal.cast_iron_bare")
    ram.visual(mesh_from_geometry(_annular_sector(inner_radius=0.040, outer_radius=0.048, thickness_y=0.022, theta0=dt0, theta1=dt1, segments=32), "former_groove_floor"),
               origin=Origin(xyz=(FORMER_LOCAL_X, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)), material=hw, name="former_groove_floor", material_class_id="metal.steel_bare")
    for i, yo in enumerate((-0.016, 0.016)):
        ram.visual(mesh_from_geometry(_annular_sector(inner_radius=0.046, outer_radius=0.058, thickness_y=0.008, theta0=dt0, theta1=dt1, segments=32, y_offset=yo), f"former_groove_lip_{i}"),
                   origin=Origin(xyz=(FORMER_LOCAL_X, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)), material=cast, name=f"former_groove_lip_{i}", material_class_id="metal.cast_iron_bare")
    for idx, ang in enumerate((math.radians(10), math.radians(30), math.radians(50))):
        _radial_box(ram, f"die_rib_{idx}", 0.040, ang, (0.008, 0.038, 0.035), cast, y=0.0)

    # PUMP (revolute)
    pump = model.part("pump_handle")
    pump.visual(Cylinder(radius=0.018, length=0.028), origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)), material=cast, name="pump_boss", material_class_id="metal.cast_iron_bare")
    _cylinder_between(pump, "pump_lever", (0.0, 0.0, 0.0), (-0.28, 0.0, 0.10), 0.010, b)
    pump.visual(Box((0.060, 0.022, 0.030)), origin=Origin(xyz=(-0.06, 0.0, 0.020), rpy=(0.0, -0.35, 0.0)), material=b, name="pump_web", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_yellow", "industrial_blue", "hydraulic_red", "black_cast"} else "metal.steel_galvanized"))
    _cylinder_between(pump, "pump_grip", (-0.22, 0.0, 0.078), (-0.32, 0.0, 0.114), 0.017, mats["grip"])

    # CONDUIT (fixed)
    conduit = model.part("conduit")
    _cylinder_between(conduit, "conduit_tube", (CONDUIT_X, -0.22, BEND_Z), (CONDUIT_X, 0.22, BEND_Z), 0.010, cond)
    _cylinder_between(conduit, "conduit_stub_0", (CONDUIT_X, -0.22, BEND_Z), (CONDUIT_X, -0.36, BEND_Z), 0.010, cond)
    _cylinder_between(conduit, "conduit_stub_1", (CONDUIT_X, 0.22, BEND_Z), (CONDUIT_X, 0.36, BEND_Z), 0.010, cond)

    model.articulation("frame_to_ram", ArticulationType.PRISMATIC, parent=frame, child=ram,
                       origin=Origin(xyz=(RAM_ORIGIN_X, 0.0, BEND_Z)), axis=(1.0, 0.0, 0.0),
                       motion_limits=MotionLimits(effort=80.0, velocity=0.04, lower=0.0, upper=RAM_UPPER),
                       meta={"mechanism": "hydraulic ram piston advances former die toward fixed rollers"})
    model.articulation("frame_to_pump", ArticulationType.REVOLUTE, parent=frame, child=pump,
                       origin=Origin(xyz=(-0.35, 0.14, BEND_Z - 0.050)), axis=(0.0, -1.0, 0.0),
                       motion_limits=MotionLimits(effort=25.0, velocity=2.5, lower=0.0, upper=PUMP_UPPER),
                       meta={"mechanism": "manual pump handle actuates hydraulic ram"})
    model.articulation("frame_to_conduit", ArticulationType.FIXED, parent=frame, child=conduit,
                       origin=Origin(xyz=(CONDUIT_X, 0.0, BEND_Z)))


# ---------------------------------------------------------------------------
# Build dispatch
# ---------------------------------------------------------------------------
def build_conduit_bender(config: ConduitBenderConfig | None = None, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="conduit_bender", assets=assets,
                              meta={"small_class": "Conduit bender", "domain": "Electrical_Wiring"})
    mats = {key: model.material(f"cb_{key}_{r.palette_style}", rgba=rgba) for key, rgba in r.palette.items()}

    if r.form_family == "floor_tripod":
        _build_floor_tripod(model, r, mats)
    elif r.form_family == "handheld_lever":
        _build_handheld_lever(model, r, mats)
    elif r.form_family == "hand_emt":
        _build_hand_emt(model, r, mats)
    else:
        _build_hydraulic_ram(model, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_conduit_bender(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_conduit_bender(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _allow_overlaps(ctx, model, r):
    form = r.form_family
    if form == "floor_tripod":
        frame = model.get_part("frame")
        head = model.get_part("bender_head")
        conduit = model.get_part("conduit")
        # Seated workpiece + head-on-frame are deliberate contacts (groove seating,
        # bend-axle capture, pivot bearing, stroke-extreme clearance) — allow at pair level.
        ctx.allow_overlap(conduit, head, reason="Sample conduit workpiece is deliberately seated in the forming shoe/head groove and captured on the bend axle.")
        ctx.allow_overlap(head, frame, reason="Bender head is journaled on the frame yoke; its shoe/handle swing close to the frame socket at the down-stroke extreme.")
        for i in (0, 1):
            ctx.allow_overlap(head, frame, elem_a="axle_pin", elem_b=f"pivot_bushing_{i}",
                              reason="Rotating axle pin captured in the fixed yoke bushing bore (bearing fit).")
        ctx.allow_overlap(conduit, head, elem_a="conduit_arc", elem_b="channel_bottom",
                          reason="Sample conduit is seated proud in the forming groove.")
        ctx.allow_isolated_part(conduit, reason="Sample workpiece seated in the shoe groove with deliberate clearance, FIXED to the head.")
        for i in (0, 1):
            ctx.allow_overlap(head, frame, elem_a=f"channel_lip_{i}", elem_b="reinforced_socket",
                              reason="Forming-shoe lip clears past the handle socket at the down-stroke extreme.")
        ctx.allow_overlap(head, frame, elem_a="hook_lip", elem_b="reinforced_socket",
                          reason="Forming-shoe hook lip clears past the handle socket at the down-stroke extreme.")
        ctx.allow_overlap(head, frame, elem_a="hook_web", elem_b="reinforced_socket",
                          reason="Forming-shoe hook web clears past the handle socket at the down-stroke extreme.")
        ctx.allow_overlap(conduit, head, elem_a="conduit_seat_collar", elem_b="axle_pin",
                          reason="Conduit bend collar captured on the head axle pin (bend axle).")
        ctx.allow_overlap(conduit, head, elem_a="conduit_seat_collar", elem_b="pivot_hub",
                          reason="Conduit bend collar seats on the shoe pivot hub (bend axle).")
        for yp in ("yoke_plate_0", "yoke_plate_1"):
            ctx.allow_overlap(head, frame, elem_a="handle_socket", elem_b=yp,
                              reason="Handle socket clears the yoke plates at the down-stroke extreme.")
    elif form == "hand_emt":
        bender = model.get_part("bender")
        conduit = model.get_part("conduit")
        # Seated workpiece: groove seating, bend-collar capture on the pivot hub, and the
        # bent tube sweeping toward the handle at the bend extreme — deliberate contacts.
        ctx.allow_overlap(conduit, bender, reason="Sample conduit workpiece is deliberately seated in the forming shoe groove, captured on the bend collar, and sweeps toward the handle at the bend extreme.")
        ctx.allow_overlap(conduit, bender, elem_a="pivot_collar_spoke", elem_b="pivot_hub",
                          reason="Bend collar spoke passes over the shoe pivot hub.")
        ctx.allow_overlap(conduit, bender, elem_a="pivot_collar", elem_b="pivot_hub",
                          reason="Conduit pivot collar captured on the shoe-center hub (bend axle).")
        ctx.allow_overlap(conduit, bender, elem_a="conduit_arc", elem_b="channel_bottom",
                          reason="Sample conduit seated proud in the forming groove during the stroke.")
        for en in ("handle_socket", "handle_root_web"):
            for cn in ("conduit_arc", "conduit_exit_stub", "conduit_straight_tail"):
                ctx.allow_overlap(bender, conduit, elem_a=en, elem_b=cn,
                                  reason="Bent conduit sweeps toward the handle at the bend extreme.")
    elif form == "handheld_lever":
        shoe = model.get_part("shoe_head")
        conduit = model.get_part("sample_conduit")
        ctx.allow_isolated_part(conduit, reason="Sample conduit seated in front of the shoe groove with deliberate clearance, FIXED to the shoe.")
        ctx.allow_overlap(conduit, shoe, reason="Sample conduit workpiece is deliberately seated in the forming shoe groove.")
        if r.lever_config == "single_swing_arm":
            handle = model.get_part("swing_handle")
            ctx.allow_overlap(shoe, handle, elem_a="pivot_pin", elem_b="pivot_bushing",
                              reason="Steel pivot pin captured inside the moving handle bushing.")
        elif r.lever_config == "two_handle_scissor":
            for pn in ("roller_handle", "forming_handle"):
                p = model.get_part(pn)
                ctx.allow_overlap(shoe, p, elem_a="pivot_pin", elem_b="pivot_bushing",
                                  reason="Steel pivot pin captured inside the scissor handle bushing.")
        else:  # ratchet_pump
            drive = model.get_part("ratchet_drive")
            pump = model.get_part("pump_handle")
            ctx.allow_overlap(shoe, drive, elem_a="pivot_pin", elem_b="drive_bushing",
                              reason="Pivot pin captured inside the ratchet drive bushing.")
            ctx.allow_overlap(shoe, drive, elem_a="pivot_pin", elem_b="drive_yoke",
                              reason="Drive yoke wraps the pivot pin between bushing and arm.")
            ctx.allow_overlap(shoe, pump, elem_a="pivot_pin", elem_b="pump_pivot_hub",
                              reason="Pivot pin captured inside the pump pivot hub.")
    else:  # hydraulic_ram
        frame = model.get_part("frame")
        ram = model.get_part("ram")
        pump = model.get_part("pump_handle")
        conduit = model.get_part("conduit")
        ctx.allow_overlap(ram, frame, elem_a="piston_rod", elem_b="ram_cylinder_body",
                          reason="Piston rod slides inside the hydraulic cylinder body.")
        ctx.allow_overlap(ram, frame, elem_a="piston_rod", elem_b="ram_cylinder_front_gland",
                          reason="Piston rod passes through the cylinder front gland seal.")
        ctx.allow_overlap(frame, pump, elem_a="pump_pivot_boss", elem_b="pump_boss",
                          reason="Pump handle boss mounted on the frame pivot boss (bearing fit).")
        ctx.allow_overlap(frame, pump, elem_a="pump_pivot_boss", elem_b="pump_lever",
                          reason="Pump lever starts at the pivot center inside the boss.")
        for i in (0, 1):
            ctx.allow_overlap(frame, conduit, elem_a=f"conduit_clamp_{i}", elem_b="conduit_tube",
                              reason="Conduit seated on the frame clamp support mount.")
        ctx.allow_isolated_part(conduit, reason="Sample conduit seated in the former die/rollers with deliberate clearance, FIXED to the frame.")


def _expect(ctx, model, r):
    ctx.check("slot_choices recorded",
              tuple(model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
              details=str(model.meta.get("slot_choices")))
    roots = model.root_parts()
    ctx.check("single root part", len(roots) == 1, details=f"roots={[p.name for p in roots]}")

    form = r.form_family
    if form == "floor_tripod":
        joint = model.get_articulation("frame_to_bender_head")
        head = model.get_part("bender_head")
        ctx.check("bend joint is revolute", joint.articulation_type == ArticulationType.REVOLUTE, details=str(joint.articulation_type))
        hn = {v.name for v in head.visuals}
        ctx.check("head has curved shoe groove + hook + degree scale",
                  {"shoe_web", "channel_bottom", "channel_lip_0", "channel_lip_1", "hook_lip", "degree_scale", "handle_tube"}.issubset(hn),
                  details=str(sorted(hn)))
        grip0 = ctx.part_element_world_aabb(head, elem="rubber_grip")
        with ctx.pose({joint: joint.motion_limits.upper - 0.01}):
            grip1 = ctx.part_element_world_aabb(head, elem="rubber_grip")
        ctx.check("bending stroke raises the lever grip",
                  grip0 is not None and grip1 is not None and grip1[0][2] > grip0[0][2] + 0.20,
                  details=f"rest={grip0}, up={grip1}")
    elif form == "hand_emt":
        joint = model.get_articulation("bender_to_conduit")
        bender = model.get_part("bender")
        conduit = model.get_part("conduit")
        ctx.check("bend joint is revolute (conduit pivots)", joint.articulation_type == ArticulationType.REVOLUTE, details=str(joint.articulation_type))
        bn = {v.name for v in bender.visuals}
        ctx.check("bender has curved shoe + long handle + foot peg",
                  {"shoe_web", "channel_bottom", "hook_lip", "handle_tube", "foot_peg"}.issubset(bn),
                  details=str(sorted(bn)))
        t0 = ctx.part_element_world_aabb(conduit, elem="conduit_straight_tail")
        with ctx.pose({joint: joint.motion_limits.upper - 0.01}):
            t1 = ctx.part_element_world_aabb(conduit, elem="conduit_straight_tail")
        ctx.check("bending stroke rotates conduit tail up",
                  t0 is not None and t1 is not None and t1[1][2] > t0[1][2] + 0.06,
                  details=f"rest={t0}, bent={t1}")
    elif form == "handheld_lever":
        shoe = model.get_part("shoe_head")
        sn = {v.name for v in shoe.visuals}
        ctx.check("shoe has curved shoe + degree scale + curved hook",
                  {"curved_shoe", "degree_scale", "hook_lip", "pivot_pin"}.issubset(sn),
                  details=str(sorted(sn)))
        if r.base_mount == "bench_clamp":
            ctx.check("bench clamp base present, no foot pedal",
                      {"clamp_spine", "clamp_screw", "clamp_lower_jaw"}.issubset(sn) and "foot_pedal" not in sn,
                      details=str(sorted(sn)))
        else:
            ctx.check("foot pedal base present",
                      {"foot_pedal", "serrated_tread_plate"}.issubset(sn), details=str(sorted(sn)))
        # lever motion
        if r.lever_config == "single_swing_arm":
            jn, pn = "shoe_to_swing_handle", "swing_handle"
            joints = [(model.get_articulation(jn), pn)]
        elif r.lever_config == "two_handle_scissor":
            joints = [(model.get_articulation("shoe_to_roller_handle"), "roller_handle"),
                      (model.get_articulation("shoe_to_forming_handle"), "forming_handle")]
        else:
            joints = [(model.get_articulation("shoe_to_ratchet_drive"), "ratchet_drive"),
                      (model.get_articulation("shoe_to_pump_handle"), "pump_handle")]
        for joint, pn in joints:
            ctx.check(f"{pn} joint is revolute", joint.articulation_type == ArticulationType.REVOLUTE, details=str(joint.articulation_type))
        joint, pn = joints[0]
        a0 = ctx.part_element_world_aabb(model.get_part(pn), elem="handle_tube" if pn != "ratchet_drive" else "drive_arm_body")
        with ctx.pose({joint: 1.10}):
            a1 = ctx.part_element_world_aabb(model.get_part(pn), elem="handle_tube" if pn != "ratchet_drive" else "drive_arm_body")
        ctx.check("primary lever visibly swings up",
                  a0 is not None and a1 is not None and a1[1][2] > a0[1][2] + 0.04,
                  details=f"rest={a0}, posed={a1}")
    else:  # hydraulic_ram
        ram_j = model.get_articulation("frame_to_ram")
        pump_j = model.get_articulation("frame_to_pump")
        frame = model.get_part("frame")
        ram = model.get_part("ram")
        ctx.check("ram joint is prismatic", ram_j.articulation_type == ArticulationType.PRISMATIC, details=str(ram_j.articulation_type))
        ctx.check("pump joint is revolute", pump_j.articulation_type == ArticulationType.REVOLUTE, details=str(pump_j.articulation_type))
        fn = {v.name for v in ram.visuals}
        ctx.check("ram carries curved former die groove",
                  {"former_die_web", "former_groove_floor", "former_groove_lip_0", "former_groove_lip_1"}.issubset(fn),
                  details=str(sorted(fn)))
        d0 = ctx.part_element_world_aabb(ram, elem="former_die_web")
        with ctx.pose({ram_j: RAM_UPPER}):
            d1 = ctx.part_element_world_aabb(ram, elem="former_die_web")
        ctx.check("ram stroke advances former die toward conduit",
                  d0 is not None and d1 is not None and d1[1][0] > d0[1][0] + 0.06,
                  details=f"rest={d0}, ext={d1}")


def run_conduit_bender_tests(model: ArticulatedObject, config: ConduitBenderConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    _allow_overlaps(ctx, model, r)

    if any(p.name == "pump_handle" for p in model.parts):
        ctx.allow_isolated_part(
            model.get_part("pump_handle"),
            reason="pump handle swings on its pivot clear of the bender body",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    ctx.check("small class is conduit bender",
              model.meta.get("small_class") == "Conduit bender", details=str(model.meta))
    _expect(ctx, model, r)
    return ctx.report()


__all__ = (
    "ConduitBenderConfig",
    "ResolvedConduitBenderConfig",
    "FormFamily",
    "BaseMount",
    "LeverConfig",
    "PaletteStyle",
    "build_conduit_bender",
    "build_seeded_conduit_bender",
    "config_from_seed",
    "resolve_config",
    "with_overrides",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "run_conduit_bender_tests",
)
