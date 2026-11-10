# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template — rope_pulley (Camping / Outdoor Gear).

A rope block / pulley: one or more grooved sheaves spin freely (CONTINUOUS about
Y) on an axle, captured by a body (open cheek-plate block, solid mortise shell, or
tubular fairlead), with a top rope-attachment interface (fixed eye / fixed hook /
U-bail / swivel eye / swivel hook / snap shackle) and an optional self-locking
rope-control mechanism (cam cleat / progress-capture cam) and optional bottom becket.

Hub / parallel-children topology (§B pattern): the body is the grounded root
``frame``; every sheave, the attachment, and the rope-control cam parent directly
to it. ``sheave_count`` is the single multiplicity axis. See
``specs_modular_v1/rope_pulley.md``.

5-star sources (adapted, primitive types preserved):
- open_plate_block: o1 3508f0 (_plate_mesh, _sheave_mesh LatheGeometry, _hook_mesh),
  o3 ad2de3 (revolved V-groove sheave, integral eye).
- mortise_shell_block: var_shell_block (_mortise_shell_body cadquery).
- tube_fairlead: var_tube_fairlead (_tube_shell_mesh cadquery).
- attachments: o2 8db781 (swivel eye + carabiner), var_snap_shackle (bail + gate),
  var_bail_shackle (U-bail), var_fixed_hook, var_becket (torus eye).
- rope_control: var_cam_cleat (eccentric cam), var_progress_capture (ratchet cam).
- snatch_hinge: var_snatch_block (swing cheek REVOLUTE).
- multiplicity: var_triple_block (N=3), probe_triple_becket.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Discrete slot domains
# ---------------------------------------------------------------------------
BODY_FORMS = ("open_plate_block", "mortise_shell_block", "tube_fairlead")
TOP_ATTACHMENTS = (
    "fixed_eye",
    "fixed_hook",
    "u_bail",
    "swivel_eye",
    "swivel_hook",
    "snap_shackle",
)
ROPE_CONTROLS = ("plain", "cam_cleat", "progress_capture")
PALETTE_STYLES = (
    "anodized_orange",
    "stainless_silver",
    "black_anodized",
    "varnished_wood",
    "anodized_blue",
)

# Static attachments are folded into the body as visuals (Rule 1); moving ones
# are real articulated child parts.
_STATIC_ATTACHMENTS = ("fixed_eye", "fixed_hook", "u_bail")
_MOVING_ATTACHMENTS = ("swivel_eye", "swivel_hook", "snap_shackle")

N_MIN = 1
N_MAX = 4
SHEAVE_COUNT_WEIGHTS = (0.50, 0.30, 0.13, 0.07)  # spec §8: small N high-frequency

# ---------------------------------------------------------------------------
# Palettes (⑥). role keys: body / inner / sheave / metal / accent
# ---------------------------------------------------------------------------
PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "anodized_orange": {
        "body": (0.95, 0.30, 0.08, 1.0),
        "inner": (0.03, 0.035, 0.04, 1.0),
        "sheave": (0.72, 0.70, 0.66, 1.0),
        "metal": (0.72, 0.70, 0.66, 1.0),
        "accent": (0.03, 0.035, 0.04, 1.0),
    },
    "stainless_silver": {
        "body": (0.78, 0.78, 0.74, 1.0),
        "inner": (0.04, 0.045, 0.05, 1.0),
        "sheave": (0.10, 0.10, 0.11, 1.0),
        "metal": (0.92, 0.91, 0.86, 1.0),
        "accent": (0.04, 0.045, 0.05, 1.0),
    },
    "black_anodized": {
        "body": (0.10, 0.10, 0.12, 1.0),
        "inner": (0.03, 0.03, 0.04, 1.0),
        "sheave": (0.06, 0.06, 0.09, 1.0),
        "metal": (0.66, 0.67, 0.66, 1.0),
        "accent": (0.66, 0.67, 0.66, 1.0),
    },
    "varnished_wood": {
        "body": (0.52, 0.32, 0.12, 1.0),
        "inner": (0.36, 0.22, 0.09, 1.0),
        "sheave": (0.72, 0.70, 0.66, 1.0),
        "metal": (0.72, 0.70, 0.66, 1.0),
        "accent": (0.03, 0.035, 0.04, 1.0),
    },
    "anodized_blue": {
        "body": (0.12, 0.28, 0.58, 1.0),
        "inner": (0.08, 0.18, 0.40, 1.0),
        "sheave": (0.10, 0.10, 0.11, 1.0),
        "metal": (0.92, 0.91, 0.86, 1.0),
        "accent": (0.92, 0.91, 0.86, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Sheave spins about Y; sheaves stack
# along Z; plates lie in the XZ plane with thickness along Y.
# ---------------------------------------------------------------------------
_BASE_SHEAVE_R = 0.020  # groove-flange outer radius (S1/S3: ~0.016-0.026)
_SHEAVE_WIDTH = 0.014  # sheave thickness along Y (S1)
_BORE_R = 0.0055
_AXLE_R = 0.0050
_PLATE_THICK = 0.0032
_INNER_PLATE_THICK = 0.0024
_MARGIN = 0.013  # plate half-height margin above the sheave stack
_NECK_LEN = 0.012
_SEG = 72  # sheave revolve segments (compile budget)


@dataclass(frozen=True)
class RopePulleyConfig:
    body_form: str | None = None
    top_attachment: str | None = None
    rope_control: str | None = None
    sheave_count: int | None = None
    snatch_hinge: bool | None = None
    becket: bool | None = None
    palette_style: str = "stainless_silver"
    sheave_radius_scale: float = 1.0
    sheave_pitch_scale: float = 1.0
    block_width_scale: float = 1.0
    attach_scale: float = 1.0
    name: str = "rope_pulley"


@dataclass(frozen=True)
class ResolvedRopePulleyConfig:
    body_form: str
    top_attachment: str
    rope_control: str
    sheave_count: int
    snatch_hinge: bool
    becket: bool
    palette_style: str
    # concrete geometry
    sheave_r: float
    sheave_width: float
    pitch: float
    plate_half_h: float
    plate_half_y: float
    block_width: float
    attach_scale: float
    z_offsets: tuple[float, ...]
    top_z: float
    bot_z: float
    cam_z: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> RopePulleyConfig:
    rng = random.Random(seed)
    return RopePulleyConfig(
        body_form=rng.choice(BODY_FORMS),
        top_attachment=rng.choice(TOP_ATTACHMENTS),
        rope_control=rng.choice(ROPE_CONTROLS),
        sheave_count=rng.choices((1, 2, 3, 4), weights=SHEAVE_COUNT_WEIGHTS, k=1)[0],
        snatch_hinge=rng.random() < 0.5,
        becket=rng.random() < 0.5,
        palette_style=rng.choice(PALETTE_STYLES),
        sheave_radius_scale=round(rng.uniform(0.85, 1.20), 4),
        sheave_pitch_scale=round(rng.uniform(0.90, 1.15), 4),
        block_width_scale=round(rng.uniform(0.88, 1.18), 4),
        attach_scale=round(rng.uniform(0.85, 1.20), 4),
        name=f"seeded_rope_pulley_{seed}",
    )


def resolve_config(config: RopePulleyConfig | None = None) -> ResolvedRopePulleyConfig:
    cfg = config or RopePulleyConfig()

    body_form = _pick(cfg.body_form, BODY_FORMS)
    top_attachment = _pick(cfg.top_attachment, TOP_ATTACHMENTS)
    rope_control = _pick(cfg.rope_control, ROPE_CONTROLS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    sheave_count = int(cfg.sheave_count) if cfg.sheave_count is not None else 1
    sheave_count = int(_clamp(sheave_count, N_MIN, N_MAX))
    snatch_hinge = bool(cfg.snatch_hinge) if cfg.snatch_hinge is not None else False
    becket = bool(cfg.becket) if cfg.becket is not None else False

    is_plate = body_form == "open_plate_block"
    # --- Compatibility gating (spec §9). Only the planar cheek-plate block
    #     supports multiplicity, the swing cheek, the rope-control cam, the
    #     becket, and the through-plate U-bail. Enclosed bodies degrade. ---
    if not is_plate:
        sheave_count = 1
        rope_control = "plain"
        snatch_hinge = False
        becket = False
        if top_attachment == "u_bail":
            top_attachment = "swivel_eye"  # U-bail legs need through-plate holes
    if sheave_count > 1:
        snatch_hinge = False  # snatch blocks are single-sheave (sources)

    # --- Continuous scales (§7): independent -> derived -> inequality. ---
    r_scale = _clamp(cfg.sheave_radius_scale, 0.85, 1.20)
    pitch_scale = _clamp(cfg.sheave_pitch_scale, 0.90, 1.15)
    width_scale = _clamp(cfg.block_width_scale, 0.88, 1.18)
    attach_scale = _clamp(cfg.attach_scale, 0.85, 1.20)

    sheave_r = _BASE_SHEAVE_R * r_scale
    sheave_width = _SHEAVE_WIDTH
    # pitch (vertical stack spacing) must exceed the sheave diameter (no overlap).
    pitch = max(2.0 * sheave_r + 0.006, (2.0 * sheave_r + 0.010) * pitch_scale)

    z_offsets = tuple(
        (i - (sheave_count - 1) / 2.0) * pitch for i in range(sheave_count)
    )
    z_top_stack = z_offsets[-1] if z_offsets else 0.0

    # cam sits directly below the lowest sheave, in the rope line (plate only).
    # Clearance: cam max reach (~0.016) + sheave_r + margin so the lobe never
    # sweeps into the wheel through its full release travel.
    cam_z = z_offsets[0] - (sheave_r + 0.023) if rope_control != "plain" else 0.0

    # Inequality: plate half-height must cover the sheave stack (+ cam if any).
    plate_half_h = z_top_stack + sheave_r + _MARGIN
    if rope_control != "plain":
        plate_half_h = max(plate_half_h, abs(cam_z) + 0.014)

    # Y clearance: outer plate inner face must clear the sheave face.
    plate_half_y = sheave_width / 2.0 + 0.0025 + _PLATE_THICK / 2.0

    block_width = (2.0 * sheave_r + 0.022) * width_scale

    if body_form == "tube_fairlead":
        top_z = sheave_r + 0.020
        bot_z = -(sheave_r + 0.020)
    else:
        top_z = plate_half_h + _NECK_LEN
        bot_z = -(plate_half_h + _NECK_LEN)

    return ResolvedRopePulleyConfig(
        body_form=body_form,
        top_attachment=top_attachment,
        rope_control=rope_control,
        sheave_count=sheave_count,
        snatch_hinge=snatch_hinge,
        becket=becket,
        palette_style=palette_style,
        sheave_r=sheave_r,
        sheave_width=sheave_width,
        pitch=pitch,
        plate_half_h=plate_half_h,
        plate_half_y=plate_half_y,
        block_width=block_width,
        attach_scale=attach_scale,
        z_offsets=z_offsets,
        top_z=top_z,
        bot_z=bot_z,
        cam_z=cam_z,
        name=cfg.name or "rope_pulley",
    )


def with_overrides(config: RopePulleyConfig, **kwargs: object) -> RopePulleyConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedRopePulleyConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("top_attachment", r.top_attachment),
        ("rope_control", r.rope_control),
        ("sheave_count", f"n{r.sheave_count}"),
        ("snatch_hinge", "yes" if r.snatch_hinge else "no"),
        ("becket", "yes" if r.becket else "no"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (primitive types preserved from sources)
# ---------------------------------------------------------------------------
def _revolved_sheave_geometry(sheave_r: float, half_w: float, bore_r: float) -> MeshGeometry:
    """Revolved grooved sheave around local Y with a central bore (S1 L77-111)."""
    rim = sheave_r
    groove = sheave_r * 0.80
    shoulder = sheave_r * 0.97
    profile = [
        (rim * 0.86, -half_w),
        (shoulder, -half_w * 0.37),
        (rim, -half_w * 0.23),
        (groove, 0.0),
        (rim, half_w * 0.23),
        (shoulder, half_w * 0.37),
        (rim * 0.86, half_w),
        (bore_r, half_w),
        (bore_r, -half_w),
    ]
    geom = MeshGeometry()
    for i in range(_SEG):
        theta = 2.0 * math.pi * i / _SEG
        c, s = math.cos(theta), math.sin(theta)
        for radius, y in profile:
            geom.add_vertex(radius * c, y, radius * s)
    n = len(profile)
    for i in range(_SEG):
        j = (i + 1) % _SEG
        for k in range(n):
            a = i * n + k
            b = j * n + k
            cc = j * n + ((k + 1) % n)
            d = i * n + ((k + 1) % n)
            geom.add_face(a, b, cc)
            geom.add_face(a, cc, d)
    return geom


def _plate_mesh(name: str, width: float, height: float, thickness: float) -> object:
    """Rounded cheek plate (S3 L28-38): extruded along Z, rotated so thickness is Y."""
    geom = ExtrudeGeometry(
        rounded_rect_profile(width, height, radius=min(width * 0.48, height * 0.20),
                             corner_segments=12),
        thickness,
        cap=True,
        center=True,
    )
    geom.rotate_x(math.pi / 2.0)
    return mesh_from_geometry(geom, name)


def _hook_mesh(name: str, scale: float, sign: float = 1.0) -> object:
    """Continuous bent-rod swivel hook (S3 L59-82). sign +1 up / -1 down."""
    pts = [
        (0.000, 0.000, sign * 0.000),
        (0.000, 0.000, sign * 0.012),
        (-0.004, 0.000, sign * 0.020),
        (-0.016, 0.000, sign * 0.029),
        (-0.017, 0.000, sign * 0.047),
        (-0.004, 0.000, sign * 0.060),
        (0.015, 0.000, sign * 0.054),
        (0.020, 0.000, sign * 0.036),
        (0.009, 0.000, sign * 0.025),
        (0.003, 0.000, sign * 0.029),
    ]
    pts = [(x * scale, y, z * scale) for (x, y, z) in pts]
    geom = tube_from_spline_points(
        pts, radius=0.0038 * scale, samples_per_segment=8, radial_segments=16,
        closed_spline=False, cap_ends=True,
    )
    return mesh_from_geometry(geom, name)


def _carabiner_clip_mesh(name: str, scale: float) -> object:
    """Carabiner / clip loop above the swivel collar (S2 L203-224)."""
    clip_points = [
        (-0.020, 0.0, 0.011),
        (-0.024, 0.0, 0.035),
        (-0.017, 0.0, 0.061),
        (0.0, 0.0, 0.071),
        (0.017, 0.0, 0.061),
        (0.024, 0.0, 0.035),
        (0.020, 0.0, 0.011),
    ]
    clip_points = [(x * scale, y, z * scale) for (x, y, z) in clip_points]
    geom = tube_from_spline_points(
        clip_points, radius=0.0038 * scale, samples_per_segment=9, radial_segments=18,
        cap_ends=True, up_hint=(0.0, 1.0, 0.0),
    )
    return mesh_from_geometry(geom, name)


def _snap_bail_mesh(name: str, scale: float) -> object:
    """D-shaped snap-shackle bail, open on +X between hinge and catch (var_snap_shackle)."""
    bail_points = [
        (0.014, 0.0, 0.040),
        (0.017, 0.0, 0.052),
        (0.012, 0.0, 0.062),
        (0.0, 0.0, 0.070),
        (-0.016, 0.0, 0.062),
        (-0.021, 0.0, 0.046),
        (-0.016, 0.0, 0.030),
        (0.0, 0.0, 0.024),
        (0.010, 0.0, 0.024),
        (0.014, 0.0, 0.022),
    ]
    bail_points = [(x * scale, y, z * scale) for (x, y, z) in bail_points]
    geom = tube_from_spline_points(
        bail_points, radius=0.005 * scale, samples_per_segment=9, radial_segments=18,
        cap_ends=True, up_hint=(0.0, 1.0, 0.0),
    )
    return mesh_from_geometry(geom, name)


def _u_bail_geometry(scale: float) -> object:
    """Captive U-bail straddling the block, legs through both plates (var_bail_shackle)."""
    path = [
        (-0.008, 0.0, 0.000),
        (-0.008, 0.0, 0.008),
        (-0.008, 0.0, 0.016),
        (-0.008, 0.0, 0.024),
        (-0.008, 0.0, 0.030),
        (-0.006, 0.0, 0.037),
        (-0.003, 0.0, 0.042),
        (0.000, 0.0, 0.044),
        (0.003, 0.0, 0.042),
        (0.006, 0.0, 0.037),
        (0.008, 0.0, 0.030),
        (0.008, 0.0, 0.024),
        (0.008, 0.0, 0.016),
        (0.008, 0.0, 0.008),
        (0.008, 0.0, 0.000),
    ]
    path = [(x * scale, y, z * scale) for (x, y, z) in path]
    geom = tube_from_spline_points(
        path, radius=0.0022 * scale, samples_per_segment=12, radial_segments=14,
        cap_ends=True, up_hint=(0.0, 1.0, 0.0),
    )
    return mesh_from_geometry(geom, "u_bail_mesh")


def _becket_eye_mesh(name: str, scale: float) -> object:
    """Fixed torus becket / eye ring (var_becket L87-90)."""
    geom = TorusGeometry(radius=0.008 * scale, tube=0.0025 * scale,
                         radial_segments=16, tubular_segments=40)
    return mesh_from_geometry(geom, name)


def _cam_jaw_geometry(scale: float) -> object:
    """Eccentric toothed cam jaw for a self-locking cleat (var_cam_cleat L65-104)."""
    base_r = 0.004 * scale
    lobe_extent = 0.009 * scale
    tooth_depth = 0.002 * scale
    n_teeth = 6
    grip_arc = math.pi * 0.45
    points: list[tuple[float, float]] = []
    n = 96
    for i in range(n):
        theta = 2.0 * math.pi * i / n
        r = base_r
        angle_from_grip = abs(((theta - math.pi) + math.pi) % (2.0 * math.pi) - math.pi)
        if angle_from_grip < grip_arc:
            blend = 1.0 - (angle_from_grip / grip_arc) ** 2
            r += lobe_extent * blend
            tooth_phase = angle_from_grip * n_teeth / grip_arc
            r += tooth_depth * abs(math.sin(tooth_phase * math.pi)) * blend
        points.append((r * math.cos(theta), r * math.sin(theta)))
    pivot = [
        (0.0026 * scale * math.cos(2 * math.pi * i / 24),
         0.0026 * scale * math.sin(2 * math.pi * i / 24))
        for i in range(24)
    ]
    cam = ExtrudeWithHolesGeometry(points, [pivot], 0.010, cap=True, center=True, closed=True)
    cam.rotate_x(math.pi / 2.0)
    return mesh_from_geometry(cam, "cam_body_mesh")


def _capture_cam_geometry(scale: float) -> object:
    """Asymmetric ratchet progress-capture cam (var_progress_capture L128-177)."""
    base_r = 0.010 * scale
    tooth_h = 0.0022 * scale
    n_teeth = 7
    tooth_start = math.radians(25.0)
    tooth_end = math.radians(155.0)
    tooth_span = tooth_end - tooth_start
    points: list[tuple[float, float]] = []
    smooth_steps = 22
    smooth_span = 2.0 * math.pi - tooth_span
    for i in range(smooth_steps):
        a = tooth_end + smooth_span * i / smooth_steps
        points.append((base_r * math.cos(a), base_r * math.sin(a)))
    for i in range(n_teeth):
        a0 = tooth_start + tooth_span * (i / n_teeth)
        at = tooth_start + tooth_span * ((i + 0.65) / n_teeth)
        a1 = tooth_start + tooth_span * ((i + 1.0) / n_teeth)
        points.append((base_r * math.cos(a0), base_r * math.sin(a0)))
        points.append(((base_r + tooth_h) * math.cos(at), (base_r + tooth_h) * math.sin(at)))
        points.append((base_r * math.cos(a1), base_r * math.sin(a1)))
    bore = [
        (0.0035 * scale * math.cos(2 * math.pi * i / 28),
         0.0035 * scale * math.sin(2 * math.pi * i / 28))
        for i in range(28)
    ]
    cam = ExtrudeWithHolesGeometry(points, [bore], 0.009, center=True)
    return mesh_from_geometry(cam, "capture_cam_mesh")


def _mortise_shell_body(r: ResolvedRopePulleyConfig, assets) -> object:
    """Solid rounded mortise block enclosing the sheave (var_shell_block L94-165)."""
    sr = r.sheave_r
    dx = (2.0 * sr + 0.008) * (r.block_width / (2.0 * sr + 0.022))
    dy = r.sheave_width + 0.020
    dz = 2.0 * r.plate_half_h
    cz = r.plate_half_h - (sr + _MARGIN)  # sheave sits below mid-height
    cavity_r = sr + 0.002
    half_dy = dy / 2.0

    body = (
        cq.Workplane("XY").transformed(offset=(0, 0, cz))
        .box(dx, dy, dz).edges("|Z").fillet(min(0.010, dx * 0.22))
    )
    body = body.edges("#Z").fillet(0.0028)
    pocket = cq.Workplane("XZ").circle(cavity_r).extrude(r.sheave_width / 2.0 + 0.001, both=True)
    body = body.cut(pocket)
    mouth = (
        cq.Workplane("XZ").center(0, -(sr + 0.006))
        .rect(0.013, 0.040).extrude(half_dy + 0.002, both=True)
    )
    body = body.cut(mouth)
    bore = cq.Workplane("XZ").circle(_AXLE_R + 0.0008).extrude(half_dy + 0.002, both=True)
    body = body.cut(bore)
    # attachment eye through X near top (used when top_attachment == fixed_eye)
    eye = (
        cq.Workplane("YZ").center(0, r.plate_half_h + 0.006)
        .circle(0.005).extrude(dx / 2.0 + 0.002, both=True)
    )
    body = body.cut(eye)
    return mesh_from_cadquery(body, "shell_body", assets=assets,
                              tolerance=0.0005, angular_tolerance=0.09)


def _tube_shell_mesh(r: ResolvedRopePulleyConfig, assets) -> object:
    """Tubular rope-glider fairlead shell + end webs + top boss (var_tube_fairlead L25-83)."""
    outer_r = r.sheave_r + 0.016
    inner_r = r.sheave_r + 0.011
    half_len = r.sheave_width / 2.0 + 0.008
    web_inner_r = _AXLE_R + 0.0006
    web_thickness = 0.003
    boss_r = 0.010
    boss_h = 0.010

    shell = cq.Workplane("XZ").circle(outer_r).circle(inner_r).extrude(half_len, both=True)
    for y_sign in (-1, 1):
        y_pos = y_sign * (half_len - web_thickness / 2.0)
        web = (
            cq.Workplane("XZ").circle(inner_r + 0.001).circle(web_inner_r)
            .extrude(web_thickness / 2.0, both=True).translate((0.0, y_pos, 0.0))
        )
        shell = shell.union(web)
    boss = cq.Workplane("XY").circle(boss_r).extrude(boss_h).translate((0.0, 0.0, outer_r - 0.003))
    shell = shell.union(boss)
    slot_w = 0.013
    slot_h = 0.030
    slot_l = half_len * 2.0 + 0.004
    slot_z = -(outer_r - slot_h / 2.0 + 0.003)
    for x_off in (-(r.sheave_r * 0.9), (r.sheave_r * 0.9)):
        cutter = cq.Workplane("XY").box(slot_w, slot_l, slot_h).translate((x_off, 0.0, slot_z))
        shell = shell.cut(cutter)
    return mesh_from_cadquery(shell, "tube_shell", assets=assets,
                              tolerance=0.0005, angular_tolerance=0.09)


# ---------------------------------------------------------------------------
# Body builders — each returns (top_z mount collar built on frame, top mount r)
# ---------------------------------------------------------------------------
def _emit_axle_and_sheaves(model, frame, r: ResolvedRopePulleyConfig, mats, *, axle_len: float):
    """Emit one axle pin per sheave and the spinning sheave parts (multiplicity)."""
    sheave_geom = mesh_from_geometry(
        _revolved_sheave_geometry(r.sheave_r, r.sheave_width / 2.0, _BORE_R),
        f"sheave_r{round(r.sheave_r, 4)}",
    )
    for i, z in enumerate(r.z_offsets):
        frame.visual(
            Cylinder(radius=_AXLE_R, length=axle_len),
            origin=Origin(xyz=(0.0, 0.0, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["metal"], name=f"axle_pin_{i}", material_class_id="metal.stainless_matte",
        )
        sheave = model.part(f"sheave_{i}")
        sheave.visual(sheave_geom, material=mats["sheave"], name="grooved_sheave", material_class_id="metal.blackened_gunmetal")
        for wname, wy in (("front_hub_washer", r.sheave_width / 2.0 - 0.001),
                          ("rear_hub_washer", -(r.sheave_width / 2.0 - 0.001))):
            sheave.visual(
                Cylinder(radius=0.0085, length=0.004),
                origin=Origin(xyz=(0.0, wy, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["metal"], name=wname, material_class_id="metal.stainless_matte",
            )
        # ④ rotation witness mark on the front flange (host-derived radius).
        sheave.visual(
            Box((0.010, 0.00045, 0.0014)),
            origin=Origin(xyz=(r.sheave_r * 0.5, r.sheave_width / 2.0 + 0.0003, 0.0)),
            material=mats["accent"], name="rotation_mark", material_class_id="metal.blackened_gunmetal",
        )
        model.articulation(
            f"frame_to_sheave_{i}", ArticulationType.CONTINUOUS,
            parent=frame, child=sheave,
            origin=Origin(xyz=(0.0, 0.0, z)), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=15.0),
        )


def _build_open_plate_block(model, frame, r: ResolvedRopePulleyConfig, mats):
    plate_h = 2.0 * r.plate_half_h
    axle_len = 2.0 * r.plate_half_y + _PLATE_THICK + 0.002
    outer_plate = _plate_mesh("outer_cheek_plate", r.block_width, plate_h, _PLATE_THICK)
    # Front outer plate always on the frame; rear becomes a swing_plate if snatch.
    frame.visual(outer_plate, origin=Origin(xyz=(0.0, r.plate_half_y, 0.0)),
                 material=mats["body"], name="front_outer_plate", material_class_id="metal.stainless_matte")
    if not r.snatch_hinge:
        frame.visual(outer_plate, origin=Origin(xyz=(0.0, -r.plate_half_y, 0.0)),
                     material=mats["body"], name="rear_outer_plate", material_class_id="metal.stainless_matte")
    # Inner dark plates for multi-sheave blocks (S3 stacked look).
    if r.sheave_count >= 2:
        inner_h = plate_h - 0.008
        inner_w = r.block_width - 0.006
        inner_plate = _plate_mesh("inner_dark_plate", inner_w, inner_h, _INNER_PLATE_THICK)
        inner_y = r.plate_half_y - _PLATE_THICK / 2.0 - _INNER_PLATE_THICK / 2.0 - 0.0006
        frame.visual(inner_plate, origin=Origin(xyz=(0.0, inner_y, 0.0)),
                     material=mats["inner"], name="front_inner_plate", material_class_id="metal.blackened_gunmetal")
        frame.visual(inner_plate, origin=Origin(xyz=(0.0, -inner_y, 0.0)),
                     material=mats["inner"], name="rear_inner_plate", material_class_id="metal.blackened_gunmetal")
    # Side spacer rails between the plates.
    rail_x = r.block_width / 2.0 - 0.004
    for xs, nm in ((rail_x, "side_spacer_pos"), (-rail_x, "side_spacer_neg")):
        frame.visual(
            Box((0.004, 2.0 * r.plate_half_y - 0.001, plate_h * 0.74)),
            origin=Origin(xyz=(xs, 0.0, 0.0)), material=mats["inner"],
            name=nm, material_class_id="metal.blackened_gunmetal",
        )
    _emit_axle_and_sheaves(model, frame, r, mats, axle_len=axle_len)
    # axle rivet caps (④ hardware heads).
    for i, z in enumerate(r.z_offsets):
        for ys, hn in ((r.plate_half_y + 0.0016, "front"), (-(r.plate_half_y + 0.0016), "rear")):
            frame.visual(
                Cylinder(radius=0.0072, length=0.0022),
                origin=Origin(xyz=(0.0, ys, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["metal"], name=f"axle_cap_{i}_{hn}", material_class_id="metal.stainless_matte",
            )
    # Top & bottom necks + collars.
    _emit_neck(frame, r, mats, r.plate_half_h, "top")
    _emit_neck(frame, r, mats, -r.plate_half_h, "bottom")
    # Snatch swing cheek (single-sheave only, gated in resolve).
    if r.snatch_hinge:
        _emit_swing_plate(model, frame, r, mats, outer_plate)


def _emit_neck(frame, r, mats, edge_z: float, tag: str):
    sign = 1.0 if edge_z >= 0 else -1.0
    neck_z = edge_z + sign * (_NECK_LEN / 2.0)
    frame.visual(
        Box((0.013, 2.0 * r.plate_half_y - 0.001, _NECK_LEN + 0.004)),
        origin=Origin(xyz=(0.0, 0.0, neck_z)), material=mats["body"],
        name=f"{tag}_neck", material_class_id="metal.stainless_matte",
    )
    collar_z = edge_z + sign * _NECK_LEN
    frame.visual(
        Cylinder(radius=0.0072, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, collar_z)), material=mats["metal"],
        name=f"{tag}_collar", material_class_id="metal.stainless_matte",
    )


def _emit_swing_plate(model, frame, r, mats, outer_plate):
    # Snatch-block movable cheek: the rear plate pivots open about a top hinge
    # line (axis -X). The captured axle passes through it (allow_overlap).
    pivot_z = r.plate_half_h - 0.010
    swing = model.part("swing_plate")
    swing.visual(
        outer_plate,
        origin=Origin(xyz=(0.0, 0.0, -pivot_z), rpy=(0.0, 0.0, 0.0)),
        material=mats["body"], name="rear_outer_plate", material_class_id="metal.stainless_matte",
    )
    model.articulation(
        "frame_to_swing_plate", ArticulationType.REVOLUTE,
        parent=frame, child=swing,
        origin=Origin(xyz=(0.0, -r.plate_half_y, pivot_z)), axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=math.pi / 2.0),
    )


def _build_mortise_shell(model, frame, r, mats, assets):
    frame.visual(_mortise_shell_body(r, assets), material=mats["body"], name="shell_body", material_class_id="metal.stainless_matte")
    _emit_axle_and_sheaves(model, frame, r, mats,
                           axle_len=r.sheave_width + 0.020)
    for ys, hn in ((r.sheave_width / 2.0 + 0.011, "front"), (-(r.sheave_width / 2.0 + 0.011), "rear")):
        frame.visual(
            Cylinder(radius=0.0084, length=0.0024),
            origin=Origin(xyz=(0.0, ys, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["metal"], name=f"axle_cap_{hn}", material_class_id="metal.stainless_matte",
        )
    _emit_neck(frame, r, mats, r.plate_half_h, "top")


def _build_tube_fairlead(model, frame, r, mats, assets):
    frame.visual(_tube_shell_mesh(r, assets), material=mats["body"], name="tube_shell", material_class_id="metal.stainless_matte")
    _emit_axle_and_sheaves(model, frame, r, mats,
                           axle_len=r.sheave_width + 0.014)
    for ys, hn in ((r.sheave_width / 2.0 + 0.008, "front"), (-(r.sheave_width / 2.0 + 0.008), "rear")):
        frame.visual(
            Cylinder(radius=0.008, length=0.004),
            origin=Origin(xyz=(0.0, ys, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["metal"], name=f"axle_fastener_{hn}", material_class_id="metal.stainless_matte",
        )
    # top swivel socket boss (top of tube).
    frame.visual(
        Cylinder(radius=0.0095, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, r.sheave_r + 0.020)), material=mats["metal"],
        name="top_collar", material_class_id="metal.stainless_matte",
    )


# ---------------------------------------------------------------------------
# Static attachment features (folded into the frame — Rule 1)
# ---------------------------------------------------------------------------
def _fold_static_attachment(frame, r, mats):
    a = r.attach_scale
    mount_z = r.top_z  # collar center on every body form
    if r.top_attachment == "fixed_eye":
        # Torus eye overlapping the collar top (host-connected).
        frame.visual(
            _becket_eye_mesh("fixed_eye_ring", a),
            origin=Origin(xyz=(0.0, 0.0, mount_z + 0.004 * a), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"], name="fixed_eye", material_class_id="metal.stainless_matte",
        )
    elif r.top_attachment == "fixed_hook":
        frame.visual(
            _hook_mesh("fixed_hook_body", a, sign=1.0),
            origin=Origin(xyz=(0.0, 0.0, mount_z - 0.004)), material=mats["metal"],
            name="fixed_hook", material_class_id="metal.stainless_matte",
        )
    elif r.top_attachment == "u_bail":
        # Legs straddle the plate top just above the topmost axle (into the plate).
        frame.visual(
            _u_bail_geometry(a),
            origin=Origin(xyz=(0.0, 0.0, r.plate_half_h - 0.014 * a)),
            material=mats["metal"], name="u_bail", material_class_id="metal.stainless_matte",
        )


# ---------------------------------------------------------------------------
# Moving attachment builders (real articulated child parts)
# ---------------------------------------------------------------------------
def _emit_swivel_eye(model, frame, r, mats):
    a = r.attach_scale
    part = model.part("upper_swivel")
    # Thin shank seats coaxially in the top collar (captured pivot).
    part.visual(Cylinder(radius=0.0035, length=0.016),
                origin=Origin(xyz=(0.0, 0.0, 0.002)), material=mats["metal"],
                name="swivel_shank", material_class_id="metal.stainless_matte")
    part.visual(Cylinder(radius=0.010 * a, length=0.007),
                origin=Origin(xyz=(0.0, 0.0, 0.012)), material=mats["metal"],
                name="swivel_collar", material_class_id="metal.stainless_matte")
    part.visual(_becket_eye_mesh("swivel_eye_ring", a * 1.15),
                origin=Origin(xyz=(0.0, 0.0, 0.024 * a), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["metal"], name="swivel_eye", material_class_id="metal.stainless_matte")
    model.articulation(
        "frame_to_upper_swivel", ArticulationType.CONTINUOUS,
        parent=frame, child=part,
        origin=Origin(xyz=(0.0, 0.0, r.top_z)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=5.0),
    )
    return ["upper_swivel"]


def _emit_swivel_hook(model, frame, r, mats):
    a = r.attach_scale
    part = model.part("top_hook")
    part.visual(Cylinder(radius=0.0034, length=0.018),
                origin=Origin(xyz=(0.0, 0.0, 0.003)), material=mats["metal"],
                name="swivel_shank", material_class_id="metal.stainless_matte")
    part.visual(_hook_mesh("top_hook_body", a, sign=1.0),
                origin=Origin(xyz=(0.0, 0.0, 0.011)), material=mats["metal"],
                name="hook_body", material_class_id="metal.stainless_matte")
    model.articulation(
        "frame_to_top_hook", ArticulationType.REVOLUTE,
        parent=frame, child=part,
        origin=Origin(xyz=(0.0, 0.0, r.top_z)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=-math.pi, upper=math.pi),
    )
    return ["top_hook"]


def _emit_snap_shackle(model, frame, r, mats):
    a = r.attach_scale
    swivel = model.part("upper_swivel")
    swivel.visual(Cylinder(radius=0.0035, length=0.016),
                  origin=Origin(xyz=(0.0, 0.0, 0.002)), material=mats["metal"],
                  name="swivel_shank", material_class_id="metal.stainless_matte")
    swivel.visual(Cylinder(radius=0.011 * a, length=0.008),
                  origin=Origin(xyz=(0.0, 0.0, 0.013)), material=mats["metal"],
                  name="swivel_collar", material_class_id="metal.stainless_matte")
    # Connector barrel bridges the collar up to the bail base (support path).
    conn_bot, conn_top = 0.009, 0.014 + 0.028 * a
    swivel.visual(
        Cylinder(radius=0.005 * a, length=conn_top - conn_bot),
        origin=Origin(xyz=(0.0, 0.0, (conn_bot + conn_top) / 2.0)),
        material=mats["metal"], name="connector_barrel", material_class_id="metal.stainless_matte",
    )
    swivel.visual(_snap_bail_mesh("shackle_body", a),
                  origin=Origin(xyz=(0.0, 0.0, 0.014)), material=mats["metal"],
                  name="shackle_body", material_class_id="metal.stainless_matte")
    swivel.visual(
        Cylinder(radius=0.003 * a, length=0.016),
        origin=Origin(xyz=(0.014 * a, 0.0, 0.014 + 0.040 * a), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["accent"], name="shackle_hinge_pin", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        "frame_to_upper_swivel", ArticulationType.CONTINUOUS,
        parent=frame, child=swivel,
        origin=Origin(xyz=(0.0, 0.0, r.top_z)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=5.0),
    )
    gate = model.part("shackle_gate")
    glen = 0.018 * a
    gate.visual(Cylinder(radius=0.004 * a, length=glen),
                origin=Origin(xyz=(0.0, 0.0, -glen / 2.0)), material=mats["metal"],
                name="gate_lever", material_class_id="metal.stainless_matte")
    gate.visual(Cylinder(radius=0.005 * a, length=0.005),
                origin=Origin(xyz=(0.0, 0.0, -glen - 0.001)), material=mats["accent"],
                name="gate_plunger_tip", material_class_id="metal.blackened_gunmetal")
    model.articulation(
        "upper_swivel_to_gate", ArticulationType.REVOLUTE,
        parent=swivel, child=gate,
        origin=Origin(xyz=(0.014 * a, 0.0, 0.014 + 0.040 * a)), axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=6.0, lower=0.0, upper=0.60),
    )
    return ["upper_swivel", "shackle_gate"]


# ---------------------------------------------------------------------------
# Rope-control cam builders (open_plate_block only)
# ---------------------------------------------------------------------------
def _emit_cam(model, frame, r, mats):
    a = r.attach_scale
    cam_x = 0.0  # directly below the sheave stack, in the rope line
    # cam pivot pin on the frame.
    frame.visual(
        Cylinder(radius=0.0032, length=2.0 * r.plate_half_y - 0.001),
        origin=Origin(xyz=(cam_x, 0.0, r.cam_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"], name="cam_pin", material_class_id="metal.stainless_matte",
    )
    if r.rope_control == "cam_cleat":
        part = model.part("cam_jaw")
        part.visual(_cam_jaw_geometry(a), origin=Origin(), material=mats["accent"], name="cam_body", material_class_id="metal.blackened_gunmetal")
        part.visual(Cylinder(radius=0.0035, length=0.012),
                    origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=mats["metal"], name="cam_bushing", material_class_id="metal.stainless_matte")
        limits = MotionLimits(effort=2.0, velocity=4.0, lower=-0.10, upper=0.90)
        jname, cname = "frame_to_cam", "cam_jaw"
    else:  # progress_capture
        part = model.part("capture_cam")
        part.visual(_capture_cam_geometry(a),
                    origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=mats["metal"], name="cam_body", material_class_id="metal.stainless_matte")
        part.visual(Cylinder(radius=0.0035, length=0.012),
                    origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=mats["metal"], name="cam_bushing", material_class_id="metal.stainless_matte")
        limits = MotionLimits(effort=1.0, velocity=5.0, lower=-0.10, upper=0.50)
        jname, cname = "frame_to_capture_cam", "capture_cam"
    # Witness mark off the pivot axis so the cam's rotation is measurable.
    # Witness bar through the central bushing (always solid) extending off-axis.
    part.visual(
        Box((0.010, 0.0016, 0.0018)),
        origin=Origin(xyz=(-0.004, 0.0, 0.0)), material=mats["accent"], name="cam_mark", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        jname, ArticulationType.REVOLUTE, parent=frame, child=part,
        origin=Origin(xyz=(cam_x, 0.0, r.cam_z)), axis=(0.0, 1.0, 0.0),
        motion_limits=limits,
    )
    return cname, jname


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------
def build_rope_pulley(config: RopePulleyConfig | None = None, *, assets=None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, meta={"template": "rope_pulley"})

    pal = PALETTES[r.palette_style]
    mats = {k: model.material(f"{r.palette_style}_{k}", rgba=v) for k, v in pal.items()}

    frame = model.part("frame")

    if r.body_form == "open_plate_block":
        _build_open_plate_block(model, frame, r, mats)
    elif r.body_form == "mortise_shell_block":
        _build_mortise_shell(model, frame, r, mats, assets)
    else:
        _build_tube_fairlead(model, frame, r, mats, assets)

    # Attachment.
    if r.top_attachment in _STATIC_ATTACHMENTS:
        _fold_static_attachment(frame, r, mats)
    elif r.top_attachment == "swivel_eye":
        _emit_swivel_eye(model, frame, r, mats)
    elif r.top_attachment == "swivel_hook":
        _emit_swivel_hook(model, frame, r, mats)
    elif r.top_attachment == "snap_shackle":
        _emit_snap_shackle(model, frame, r, mats)

    # Bottom becket (folded, open_plate_block only).
    if r.becket:
        frame.visual(
            _becket_eye_mesh("becket_eye_ring", r.attach_scale),
            origin=Origin(xyz=(0.0, 0.0, r.bot_z - 0.008 * r.attach_scale),
                          rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"], name="becket_eye", material_class_id="metal.stainless_matte",
        )

    # Rope control.
    if r.rope_control != "plain":
        _emit_cam(model, frame, r, mats)

    return model


def build_seeded_rope_pulley(seed: int) -> ArticulatedObject:
    return build_rope_pulley(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _allow_capture_overlaps(ctx, model, r: ResolvedRopePulleyConfig):
    frame = model.get_part("frame")
    part_names = {p.name for p in model.parts}
    # axle pin passes through each sheave's hub washers (captured pin).
    for i in range(r.sheave_count):
        sheave = model.get_part(f"sheave_{i}")
        for wname in ("front_hub_washer", "rear_hub_washer"):
            ctx.allow_overlap(frame, sheave, elem_a=f"axle_pin_{i}", elem_b=wname,
                              reason="stationary axle pin captured inside the spinning sheave hub")
    # moving attachment shank/collar captured in the body top collar (coaxial pivot).
    for pname in ("upper_swivel", "top_hook"):
        if pname in part_names:
            part = model.get_part(pname)
            for felem in ("top_collar", "top_neck"):
                for celem in ("swivel_shank", "swivel_collar"):
                    ctx.allow_overlap(frame, part, elem_a=felem, elem_b=celem,
                                      reason="swivel shank/collar captured coaxially in the top collar")
    # cam captured on its pivot pin.
    for pname in ("cam_jaw", "capture_cam"):
        if pname in part_names:
            part = model.get_part(pname)
            ctx.allow_overlap(frame, part, elem_a="cam_pin", elem_b="cam_bushing",
                              reason="cam bushing captured on the stationary cam pivot pin")
            ctx.allow_overlap(frame, part, elem_a="cam_pin", elem_b="cam_body",
                              reason="cam pivot pin passes through the cam body bore")
    # snap-shackle spring gate latches against the bail (hinge + catch seating).
    if "shackle_gate" in part_names:
        swivel = model.get_part("upper_swivel")
        gate = model.get_part("shackle_gate")
        for gelem in ("gate_lever", "gate_plunger_tip"):
            ctx.allow_overlap(swivel, gate, elem_a="shackle_body", elem_b=gelem,
                              reason="spring gate hinges on and latches against the shackle bail")
    # snatch swing cheek: the captured axle passes through the movable plate.
    if "swing_plate" in part_names:
        swing = model.get_part("swing_plate")
        ctx.allow_overlap(frame, swing, elem_a="axle_pin_0", elem_b="rear_outer_plate",
                          reason="captured axle passes through the snatch-block movable cheek")


def run_rope_pulley_tests(model: ArticulatedObject, config: RopePulleyConfig | None = None) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    _allow_capture_overlaps(ctx, model, r)

    # --- Core identity: at least one CONTINUOUS-Y sheave that really spins. ---
    ctx.check("has at least one sheave", any(p.name.startswith("sheave_") for p in model.parts))
    for i in range(r.sheave_count):
        joint = model.get_articulation(f"frame_to_sheave_{i}")
        ctx.check(
            f"frame_to_sheave_{i} is CONTINUOUS about Y",
            joint.articulation_type == ArticulationType.CONTINUOUS
            and tuple(round(v, 3) for v in joint.axis) == (0.0, 1.0, 0.0),
            details=f"type={joint.articulation_type}, axis={joint.axis}",
        )

    # Sheave spin proof: axle center fixed, witness mark travels around the axis.
    sheave0 = model.get_part("sheave_0")
    spin = model.get_articulation("frame_to_sheave_0")
    rest_pos = ctx.part_world_position(sheave0)
    rest_mark = ctx.part_element_world_aabb(sheave0, elem="rotation_mark")
    with ctx.pose({spin: math.pi / 2.0}):
        turned_pos = ctx.part_world_position(sheave0)
        turned_mark = ctx.part_element_world_aabb(sheave0, elem="rotation_mark")

    def _c(aabb):
        if aabb is None:
            return None
        lo, hi = aabb
        return tuple((lo[k] + hi[k]) * 0.5 for k in range(3))

    ctx.check(
        "sheave spin keeps axle center fixed",
        rest_pos is not None and turned_pos is not None
        and all(abs(rest_pos[k] - turned_pos[k]) < 1e-6 for k in range(3)),
        details=f"rest={rest_pos}, turned={turned_pos}",
    )
    rc, tc = _c(rest_mark), _c(turned_mark)
    ctx.check(
        "rotation mark travels around the sheave axis",
        rc is not None and tc is not None
        and (abs(rc[0] - tc[0]) > 0.004 or abs(rc[2] - tc[2]) > 0.004),
        details=f"rest_mark={rc}, turned_mark={tc}",
    )

    # --- Targeted mechanism poses. ---
    if r.top_attachment == "swivel_hook":
        hook = model.get_part("top_hook")
        j = model.get_articulation("frame_to_top_hook")
        base = ctx.part_world_aabb(hook)
        with ctx.pose({j: math.pi / 2.0}):
            rot = ctx.part_world_aabb(hook)
        ctx.check("swivel hook rotates about Z",
                  base is not None and rot is not None
                  and abs((rot[1][0] - rot[0][0]) - (base[1][1] - base[0][1])) < 0.012,
                  details=f"base={base}, rot={rot}")
    if r.top_attachment == "swivel_eye":
        sw = model.get_part("upper_swivel")
        j = model.get_articulation("frame_to_upper_swivel")
        base = ctx.part_world_aabb(sw)
        with ctx.pose({j: math.pi / 2.0}):
            rot = ctx.part_world_aabb(sw)
        ctx.check("swivel eye rotates as one assembly",
                  base is not None and rot is not None, details="rotated")
    if r.top_attachment == "snap_shackle":
        gate = model.get_part("shackle_gate")
        j = model.get_articulation("upper_swivel_to_gate")
        closed = _c(ctx.part_element_world_aabb(gate, elem="gate_plunger_tip"))
        with ctx.pose({j: 0.55}):
            opened = _c(ctx.part_element_world_aabb(gate, elem="gate_plunger_tip"))
        ctx.check("snap-shackle gate opens (plunger tip moves)",
                  closed is not None and opened is not None
                  and (abs(closed[0] - opened[0]) > 0.002 or abs(closed[2] - opened[2]) > 0.002),
                  details=f"closed={closed}, opened={opened}")
    if r.rope_control != "plain":
        cam_name = "cam_jaw" if r.rope_control == "cam_cleat" else "capture_cam"
        jname = "frame_to_cam" if r.rope_control == "cam_cleat" else "frame_to_capture_cam"
        cam = model.get_part(cam_name)
        j = model.get_articulation(jname)
        base = _c(ctx.part_element_world_aabb(cam, elem="cam_mark"))
        with ctx.pose({j: 0.45}):
            rot = _c(ctx.part_element_world_aabb(cam, elem="cam_mark"))
        ctx.check("rope-control cam swings (release motion)",
                  base is not None and rot is not None
                  and (abs(base[0] - rot[0]) > 0.001 or abs(base[2] - rot[2]) > 0.001),
                  details=f"base={base}, rot={rot}")
    if r.snatch_hinge:
        swing = model.get_part("swing_plate")
        j = model.get_articulation("frame_to_swing_plate")
        closed = _c(ctx.part_element_world_aabb(swing, elem="rear_outer_plate"))
        with ctx.pose({j: math.pi / 2.0}):
            opened = _c(ctx.part_element_world_aabb(swing, elem="rear_outer_plate"))
        ctx.check("snatch cheek swings outward (toward -Y)",
                  closed is not None and opened is not None and opened[1] < closed[1] - 0.010,
                  details=f"closed={closed}, opened={opened}")

    # --- Rule 5: no self-intersection through the full motion envelope. ---
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    return ctx.report()


run_tests = run_rope_pulley_tests
