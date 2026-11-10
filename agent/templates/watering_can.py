# SPDX-License-Identifier: Apache-2.0

"""Agricultural / Watering can — modular parametric template.

A watering can = a single thin-walled ``can`` hub (a CadQuery surface-of-
revolution body with a real side wall port) carrying, as host visuals, a
tapered/gooseneck/stubby spout, an optional perforated sprinkler rose, corrugation
rib bands (multiplicity N), rolled rim/foot edges, a fixed rear side handle, a
vertical rolled seam, and the top articulation hardware; plus ONE moving top
mechanism part joined by a REVOLUTE joint.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/watering_can.md`` and the 10
``watering_can`` 5-star records (1 origin + 9 slot forks) synced under
``data/records/``.

Slots (pattern = ``mixed``):
  * ``body_form`` (③ Primary Form Family, 4): cylinder / oval_drum / bulbous /
    conical — the CadQuery-revolved body envelope. oval_drum applies an OCP
    ``GTransform`` Y-scale (source rec_wateringcan_var_body_ovaldrum); conical
    tapers via a linear wall-radius law (rec_..._body_conical).
  * ``spout_form`` (③, 3): long_straight (``_frustum_tube``) / gooseneck
    (``tube_from_spline_points`` S-arch) / stubby (short low-taper frustum).
  * ``spout_end`` (① skeleton, 2): rose_sprinkler (perforated cadquery rose) /
    open_nozzle (picture-true bare open mouth — the reference has no rose).
  * ``top_mechanism`` (② joint, 3): swing_bail (1 REVOLUTE +Y strap) /
    d_handle (1 REVOLUTE +Y rigid D) / hinged_lid (1 REVOLUTE -Y half-lid at the
    mouth). Every candidate keeps ≥1 non-fixed revolute.
  * ``rib_count`` (N in [2,10]): corrugation rib bands, FIXED host visuals
    (Rule 1), radii derived per-z from the body wall (Rule 4).

Every host decoration is a ``can`` visual (Rule 1). The three pivots are
captured-pin geometry (washer-in-lug / boss-in-lug / knuckle-on-rod), so they
omit ``MatingContract`` (grandfathered, guarded by element-scoped
``allow_overlap`` mirroring each source's run_tests) and the flat
articulation-origin baseline. All body-derived quantities flow from the single
``_body_outer_x(form, z)`` wall law (Contract 3c/3e).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    CylinderGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    sweep_profile_along_spline,
    tube_from_spline_points,
)

__modular__ = True

BodyForm = Literal["cylinder", "oval_drum", "bulbous", "conical"]
SpoutForm = Literal["long_straight", "gooseneck", "stubby"]
SpoutEnd = Literal["rose_sprinkler", "open_nozzle"]
TopMechanism = Literal["swing_bail", "d_handle", "hinged_lid"]
PaletteStyle = Literal[
    "galvanized_zinc",
    "rusted_steel",
    "enamel_green",
    "enamel_red",
    "cream",
    "copper",
    "plastic_green",
]

BODY_FORMS: tuple[BodyForm, ...] = ("cylinder", "oval_drum", "bulbous", "conical")
SPOUT_FORMS: tuple[SpoutForm, ...] = ("long_straight", "gooseneck", "stubby")
SPOUT_ENDS: tuple[SpoutEnd, ...] = ("rose_sprinkler", "open_nozzle")
TOP_MECHANISMS: tuple[TopMechanism, ...] = ("swing_bail", "d_handle", "hinged_lid")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "galvanized_zinc",
    "rusted_steel",
    "enamel_green",
    "enamel_red",
    "cream",
    "copper",
    "plastic_green",
)

N_MIN = 2
N_MAX = 10
# Rib-band multiplicity weights (spec §8: small N high-frequency, dense tail rare).
_RIB_WEIGHTS = (3, 4, 4, 3, 2, 2, 1, 1, 1)  # N = 2..10

# Palettes drive every .visual(material=mats[...]). Keys: body sheet / bright
# worn trim (rim/foot/ribs/rose/seam) / dark pivot hardware.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "galvanized_zinc": {
        "body": (0.62, 0.63, 0.66, 1.0),
        "accent": (0.80, 0.81, 0.83, 1.0),
        "hardware": (0.12, 0.12, 0.14, 1.0),
    },
    "rusted_steel": {
        "body": (0.50, 0.36, 0.24, 1.0),
        "accent": (0.72, 0.68, 0.58, 1.0),
        "hardware": (0.08, 0.07, 0.06, 1.0),
    },
    "enamel_green": {
        "body": (0.16, 0.42, 0.28, 1.0),
        "accent": (0.86, 0.88, 0.83, 1.0),
        "hardware": (0.09, 0.10, 0.09, 1.0),
    },
    "enamel_red": {
        "body": (0.62, 0.14, 0.12, 1.0),
        "accent": (0.90, 0.88, 0.83, 1.0),
        "hardware": (0.10, 0.09, 0.09, 1.0),
    },
    "cream": {
        "body": (0.90, 0.86, 0.75, 1.0),
        "accent": (0.55, 0.50, 0.42, 1.0),
        "hardware": (0.16, 0.14, 0.11, 1.0),
    },
    "copper": {
        "body": (0.72, 0.45, 0.20, 1.0),
        "accent": (0.86, 0.63, 0.34, 1.0),
        "hardware": (0.20, 0.12, 0.08, 1.0),
    },
    "plastic_green": {
        "body": (0.28, 0.55, 0.34, 1.0),
        "accent": (0.19, 0.40, 0.24, 1.0),
        "hardware": (0.10, 0.11, 0.10, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Body real-world geometry (meters). z is world-up; the body is revolved about
# +Z, the spout routed along +X. Key rest heights on the can.
# ---------------------------------------------------------------------------
PORT_Z = 0.150  # spout wall port height
LUG_Z = 0.208  # bail / D-handle pivot height (side lugs)
FOOT_Z = 0.018  # rolled foot height
SHOULDER_Z = 0.268  # top of the rib band region
RIM_Z = 0.289  # rolled top rim height
MOUTH_Z = 0.287  # hinged-lid hinge-rod height (seated in the solid rim wall)
SPOUT_BODY_PORT_RADIUS = 0.034
SPOUT_EMBED = 0.020  # how far the spout root sinks inside the +X wall

# Source-true (radius, z) revolve profiles (radius along +X in the XZ plane).
_CYL_PROFILE: list[tuple[float, float]] = [
    (0.008, 0.016),
    (0.132, 0.004),
    (0.148, 0.004),
    (0.163, 0.020),
    (0.168, 0.155),
    (0.165, 0.268),
    (0.176, 0.284),
    (0.165, 0.300),
    (0.146, 0.292),
    (0.143, 0.262),
    (0.143, 0.030),
]
_BUL_PROFILE: list[tuple[float, float]] = [
    (0.008, 0.016),
    (0.118, 0.004),
    (0.143, 0.004),
    (0.156, 0.018),
    (0.180, 0.052),
    (0.204, 0.098),
    (0.202, 0.140),
    (0.185, 0.178),
    (0.162, 0.212),
    (0.140, 0.240),
    (0.132, 0.256),
    (0.136, 0.272),
    (0.145, 0.284),
    (0.138, 0.294),
    (0.122, 0.280),
    (0.116, 0.254),
    (0.124, 0.236),
    (0.146, 0.208),
    (0.166, 0.174),
    (0.178, 0.138),
    (0.180, 0.096),
    (0.160, 0.050),
    (0.136, 0.028),
    (0.116, 0.030),
]
_CON_PROFILE: list[tuple[float, float]] = [
    (0.008, 0.016),
    (0.068, 0.004),
    (0.082, 0.004),
    (0.095, 0.020),
    (0.132, 0.150),
    (0.155, 0.235),
    (0.170, 0.268),
    (0.175, 0.282),
    (0.170, 0.298),
    (0.150, 0.292),
    (0.148, 0.262),
    (0.076, 0.030),
]

# Outer-wall radius control points (z, r) per revolve shape; single source for
# every body-derived quantity (spout root, ring radii, lug y). oval_drum shares
# the cylinder X-profile (its GTransform only scales Y).
_OUTER_CONTROL: dict[str, list[tuple[float, float]]] = {
    "cyl": [(0.020, 0.161), (0.155, 0.168), (0.268, 0.166), (0.300, 0.164)],
    "bul": [
        (0.020, 0.156),
        (0.052, 0.180),
        (0.098, 0.204),
        (0.140, 0.202),
        (0.178, 0.185),
        (0.212, 0.162),
        (0.256, 0.132),
        (0.284, 0.145),
        (0.300, 0.138),
    ],
    "con": [(0.020, 0.095), (0.150, 0.134), (0.268, 0.170), (0.300, 0.176)],
}
_PROFILE_BY_KEY: dict[str, list[tuple[float, float]]] = {
    "cyl": _CYL_PROFILE,
    "bul": _BUL_PROFILE,
    "con": _CON_PROFILE,
}
# body_form -> (revolve/profile key, Y-scale, mouth inner opening radius)
_FORM_TABLE: dict[BodyForm, tuple[str, float, float]] = {
    "cylinder": ("cyl", 1.0, 0.140),
    "oval_drum": ("cyl", 0.72, 0.140),
    "bulbous": ("bul", 1.0, 0.116),
    "conical": ("con", 1.0, 0.145),
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _interp(control: list[tuple[float, float]], z: float) -> float:
    """Piecewise-linear interpolation of (z, r) control points, end-clamped."""
    if z <= control[0][0]:
        return control[0][1]
    if z >= control[-1][0]:
        return control[-1][1]
    for (z0, r0), (z1, r1) in zip(control, control[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0) if z1 > z0 else 0.0
            return r0 + t * (r1 - r0)
    return control[-1][1]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class WateringCanConfig:
    body_form: BodyForm | None = None
    spout_form: SpoutForm | None = None
    spout_end: SpoutEnd | None = None
    top_mechanism: TopMechanism | None = None
    rib_count: int | None = None
    palette_style: PaletteStyle = "galvanized_zinc"
    body_width_scale: float = 1.0
    spout_length_scale: float = 1.0
    handle_height_scale: float = 1.0
    name: str = "watering_can"


@dataclass(frozen=True)
class ResolvedWateringCanConfig:
    body_form: BodyForm
    spout_form: SpoutForm
    spout_end: SpoutEnd
    top_mechanism: TopMechanism
    rib_count: int
    palette_style: PaletteStyle
    profile_key: str
    y_scale: float
    mouth_inner_r: float
    width_scale: float
    spout_length_scale: float
    handle_height_scale: float
    name: str


def config_from_seed(seed: int) -> WateringCanConfig:
    rng = random.Random(seed)
    return WateringCanConfig(
        body_form=rng.choice(BODY_FORMS),
        spout_form=rng.choice(SPOUT_FORMS),
        spout_end=rng.choice(SPOUT_ENDS),
        top_mechanism=rng.choice(TOP_MECHANISMS),
        rib_count=rng.choices(range(N_MIN, N_MAX + 1), weights=_RIB_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        body_width_scale=round(rng.uniform(0.94, 1.08), 4),
        spout_length_scale=round(rng.uniform(0.85, 1.20), 4),
        handle_height_scale=round(rng.uniform(0.90, 1.12), 4),
        name=f"seeded_watering_can_{seed}",
    )


def resolve_config(config: WateringCanConfig | None = None) -> ResolvedWateringCanConfig:
    cfg = config or WateringCanConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    spout_form = _pick(cfg.spout_form, SPOUT_FORMS)
    spout_end = _pick(cfg.spout_end, SPOUT_ENDS)
    top_mechanism = _pick(cfg.top_mechanism, TOP_MECHANISMS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    rib_count = int(cfg.rib_count) if cfg.rib_count is not None else 3
    rib_count = int(_clamp(rib_count, N_MIN, N_MAX))

    profile_key, y_scale, mouth_inner_r = _FORM_TABLE[body_form]

    width_scale = _clamp(cfg.body_width_scale, 0.94, 1.08)
    spout_length_scale = _clamp(cfg.spout_length_scale, 0.85, 1.20)
    handle_height_scale = _clamp(cfg.handle_height_scale, 0.90, 1.12)

    return ResolvedWateringCanConfig(
        body_form=body_form,
        spout_form=spout_form,
        spout_end=spout_end,
        top_mechanism=top_mechanism,
        rib_count=rib_count,
        palette_style=palette_style,
        profile_key=profile_key,
        y_scale=y_scale,
        mouth_inner_r=mouth_inner_r,
        width_scale=width_scale,
        spout_length_scale=spout_length_scale,
        handle_height_scale=handle_height_scale,
        name=cfg.name or "watering_can",
    )


def with_overrides(config: WateringCanConfig, **kwargs: object) -> WateringCanConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: WateringCanConfig | ResolvedWateringCanConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedWateringCanConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("spout_form", r.spout_form),
        ("spout_end", r.spout_end),
        ("top_mechanism", r.top_mechanism),
        ("rib_count", f"n{r.rib_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Body-derived quantities (all from _body_outer_x — Contract 3c/3e).
# ---------------------------------------------------------------------------
def _body_outer_x(r: ResolvedWateringCanConfig, z: float) -> float:
    """Outer wall radius (+X direction, before Y-scale) at height z."""
    return _interp(_OUTER_CONTROL[r.profile_key], z) * r.width_scale


def _spout_root_x(r: ResolvedWateringCanConfig) -> float:
    """+X wall x where the spout tube root sinks in at the port height."""
    return _body_outer_x(r, PORT_Z) - SPOUT_EMBED


# ---------------------------------------------------------------------------
# Body shell (CadQuery revolve; oval GTransform; +X wall port cut).
# ---------------------------------------------------------------------------
def _scaled_profile(r: ResolvedWateringCanConfig) -> list[tuple[float, float]]:
    ws = r.width_scale
    return [(radius * ws, z) for radius, z in _PROFILE_BY_KEY[r.profile_key]]


def _port_cutter_x0(r: ResolvedWateringCanConfig) -> float:
    """Inner start x of the +X port cutter (guarantees a through-wall cut)."""
    return _body_outer_x(r, PORT_Z) - 0.07


def _body_shell_solid(r: ResolvedWateringCanConfig, *, cut_port: bool = True) -> cq.Workplane:
    shell = (
        cq.Workplane("XZ").polyline(_scaled_profile(r)).close().revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )
    if r.y_scale != 1.0:
        # Non-uniform Y scale for the oval-drum body (rec_..._body_ovaldrum L100-124).
        from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform
        from OCP.gp import gp_GTrsf

        gtrsf = gp_GTrsf()
        gtrsf.SetValue(1, 1, 1.0)
        gtrsf.SetValue(2, 2, r.y_scale)
        gtrsf.SetValue(3, 3, 1.0)
        op = BRepBuilderAPI_GTransform(shell.val().wrapped, gtrsf, True)
        shell = cq.Workplane("XY").newObject([cq.Shape.cast(op.Shape())])
    if not cut_port:
        return shell
    x0 = _port_cutter_x0(r)
    port_cutter = (
        cq.Workplane("YZ").circle(SPOUT_BODY_PORT_RADIUS).extrude(0.14).translate((x0, 0.0, PORT_Z))
    )
    return shell.cut(port_cutter)


def _elliptical_torus(
    rx: float, ry: float, tube_r: float, *, n_path: int = 72, n_tube: int = 10
) -> MeshGeometry:
    """Elliptical torus (rx along X, ry along Y). rec_..._body_ovaldrum L127-167."""
    geom = MeshGeometry()
    rings: list[list[int]] = []
    for i in range(n_path):
        t = 2.0 * math.pi * i / n_path
        ct, st = math.cos(t), math.sin(t)
        cx, cy = rx * ct, ry * st
        tx, ty = -rx * st, ry * ct
        tl = math.sqrt(tx * tx + ty * ty)
        tx, ty = tx / tl, ty / tl
        nx, ny = ty, -tx
        ring: list[int] = []
        for j in range(n_tube):
            a = 2.0 * math.pi * j / n_tube
            ca, sa = math.cos(a), math.sin(a)
            ring.append(
                geom.add_vertex(cx + tube_r * ca * nx, cy + tube_r * ca * ny, tube_r * sa)
            )
        rings.append(ring)
    for i in range(n_path):
        ni = (i + 1) % n_path
        for j in range(n_tube):
            nj = (j + 1) % n_tube
            a_, b_, c_, d_ = rings[i][j], rings[ni][j], rings[ni][nj], rings[i][nj]
            geom.add_face(a_, b_, c_)
            geom.add_face(a_, c_, d_)
    return geom


def _ring_visual(
    can, r: ResolvedWateringCanConfig, *, z: float, radius: float, tube: float, name: str, material,
    n_tube: int = 10,
) -> None:
    """A rolled rim/foot/rib torus, circular or elliptical to hug the body."""
    if r.y_scale == 1.0:
        geom = TorusGeometry(radius, tube, radial_segments=72, tubular_segments=n_tube)
    else:
        geom = _elliptical_torus(radius, radius * r.y_scale, tube, n_tube=n_tube)
    can.visual(
        mesh_from_geometry(geom, f"watering_can_{name}"),
        origin=Origin(xyz=(0.0, 0.0, z)),
        name=name, material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
        material=material,
    )


# ---------------------------------------------------------------------------
# Spout geometry (frustum tube helper reused from all sources).
# ---------------------------------------------------------------------------
def _frustum_tube(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    outer_start: float,
    outer_end: float,
    wall: float,
    *,
    segments: int = 44,
) -> MeshGeometry:
    """Hollow tapered tube between two 3D points, open annular ends. (origin L107-168)."""
    sx, sy, sz = start
    ex, ey, ez = end
    ax, ay, az = ex - sx, ey - sy, ez - sz
    length = math.sqrt(ax * ax + ay * ay + az * az)
    axis = (ax / length, ay / length, az / length)
    u = (0.0, 1.0, 0.0)
    v = (
        axis[1] * u[2] - axis[2] * u[1],
        axis[2] * u[0] - axis[0] * u[2],
        axis[0] * u[1] - axis[1] * u[0],
    )
    vl = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    v = (v[0] / vl, v[1] / vl, v[2] / vl)
    inner_start = max(outer_start - wall, outer_start * 0.55)
    inner_end = max(outer_end - wall, outer_end * 0.50)
    geom = MeshGeometry()
    rings: list[list[int]] = [[], [], [], []]
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        ca, sa = math.cos(a), math.sin(a)
        radial = (u[0] * ca + v[0] * sa, u[1] * ca + v[1] * sa, u[2] * ca + v[2] * sa)
        for ring, center, radius in (
            (0, start, outer_start),
            (1, end, outer_end),
            (2, start, inner_start),
            (3, end, inner_end),
        ):
            rings[ring].append(
                geom.add_vertex(
                    center[0] + radial[0] * radius,
                    center[1] + radial[1] * radius,
                    center[2] + radial[2] * radius,
                )
            )
    for i in range(segments):
        ni = (i + 1) % segments
        geom.add_face(rings[0][i], rings[0][ni], rings[1][ni])
        geom.add_face(rings[0][i], rings[1][ni], rings[1][i])
        geom.add_face(rings[2][i], rings[3][i], rings[3][ni])
        geom.add_face(rings[2][i], rings[3][ni], rings[2][ni])
        geom.add_face(rings[0][i], rings[2][i], rings[2][ni])
        geom.add_face(rings[0][i], rings[2][ni], rings[0][ni])
        geom.add_face(rings[1][i], rings[1][ni], rings[3][ni])
        geom.add_face(rings[1][i], rings[3][ni], rings[3][i])
    return geom


def _spout_tip_and_angle(
    r: ResolvedWateringCanConfig,
) -> tuple[tuple[float, float, float], float]:
    """Return the spout tip point and its pitch angle (for rose orientation)."""
    root_x = _spout_root_x(r)
    ls = r.spout_length_scale
    if r.spout_form == "gooseneck":
        spline = _gooseneck_spline(r)
        tip, prev = spline[-1], spline[-2]
    elif r.spout_form == "stubby":
        tip = (root_x + 0.140 * ls, 0.0, 0.190)
        prev = (root_x, 0.0, PORT_Z)
    else:  # long_straight
        tip = (root_x + 0.370 * ls, 0.0, 0.205)
        prev = (root_x, 0.0, PORT_Z)
    angle = math.atan2(tip[2] - prev[2], tip[0] - prev[0])
    return tip, angle


def _gooseneck_spline(r: ResolvedWateringCanConfig) -> list[tuple[float, float, float]]:
    root_x = _spout_root_x(r)
    ls = r.spout_length_scale
    return [
        (root_x, 0.0, PORT_Z),
        (root_x + 0.060, 0.0, 0.250),
        (root_x + 0.180 * ls, 0.0, 0.360),
        (root_x + 0.280 * ls, 0.0, 0.330),
        (root_x + 0.340 * ls, 0.0, 0.280),
    ]


def _emit_spout(can, r: ResolvedWateringCanConfig, mats) -> None:
    root_x = _spout_root_x(r)
    ls = r.spout_length_scale
    if r.spout_form == "gooseneck":
        can.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    _gooseneck_spline(r),
                    radius=0.038,
                    samples_per_segment=20,
                    radial_segments=22,
                    cap_ends=False,
                ),
                "watering_can_gooseneck_spout",
            ),
            name="spout_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
            material=mats["body"],
        )
        can.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    [(root_x, 0.0, PORT_Z), (root_x + 0.030, 0.0, 0.182)],
                    radius=0.051,
                    samples_per_segment=10,
                    radial_segments=22,
                    cap_ends=False,
                ),
                "watering_can_spout_collar",
            ),
            name="spout_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
            material=mats["body"],
        )
    elif r.spout_form == "stubby":
        can.visual(
            mesh_from_geometry(
                _frustum_tube(
                    (root_x, 0.0, PORT_Z), (root_x + 0.140 * ls, 0.0, 0.190), 0.055, 0.048, 0.010
                ),
                "watering_can_stubby_spout",
            ),
            name="spout_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
            material=mats["body"],
        )
        can.visual(
            mesh_from_geometry(
                _frustum_tube(
                    (root_x + 0.023, 0.0, 0.153), (root_x + 0.065, 0.0, 0.159), 0.067, 0.059, 0.008
                ),
                "watering_can_spout_collar",
            ),
            name="spout_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
            material=mats["body"],
        )
    else:  # long_straight
        can.visual(
            mesh_from_geometry(
                _frustum_tube(
                    (root_x, 0.0, PORT_Z), (root_x + 0.370 * ls, 0.0, 0.205), 0.045, 0.024, 0.010
                ),
                "watering_can_tapered_spout",
            ),
            name="spout_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
            material=mats["body"],
        )
        can.visual(
            mesh_from_geometry(
                _frustum_tube(
                    (root_x + 0.027, 0.0, 0.154), (root_x + 0.075, 0.0, 0.161), 0.057, 0.049, 0.008
                ),
                "watering_can_spout_collar",
            ),
            name="spout_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
            material=mats["body"],
        )


def _rose_plate() -> cq.Workplane:
    """Perforated sprinkler rose plate, local normal +X (origin L171-187)."""
    holes: list[tuple[float, float]] = [(0.0, 0.0)]
    for radius, count, phase in ((0.016, 6, 0.0), (0.031, 12, math.pi / 12.0), (0.043, 16, 0.0)):
        for i in range(count):
            a = phase + 2.0 * math.pi * i / count
            holes.append((radius * math.cos(a), radius * math.sin(a)))
    return (
        cq.Workplane("YZ")
        .circle(0.055)
        .extrude(0.012)
        .faces(">X")
        .workplane(centerOption="CenterOfMass")
        .pushPoints(holes)
        .hole(0.0052)
    )


def _emit_spout_end(can, r: ResolvedWateringCanConfig, mats, *, assets) -> None:
    if r.spout_end != "rose_sprinkler":
        return  # open_nozzle: the frustum/gooseneck already reads as an open pipe mouth.
    tip, angle = _spout_tip_and_angle(r)
    can.visual(
        mesh_from_cadquery(
            _rose_plate(), "watering_can_perforated_rose", assets=assets, tolerance=0.001
        ),
        origin=Origin(xyz=tip, rpy=(0.0, -angle, 0.0)),
        name="rose_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
        material=mats["accent"],
    )


# ---------------------------------------------------------------------------
# Static host decorations on `can` (Rule 1).
# ---------------------------------------------------------------------------
def _emit_body_and_decorations(can, r: ResolvedWateringCanConfig, mats, *, assets) -> None:
    can.visual(
        mesh_from_cadquery(
            _body_shell_solid(r), "watering_can_body_shell", assets=assets, tolerance=0.001
        ),
        name="body_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
        material=mats["body"],
    )
    _ring_visual(
        can, r, z=RIM_Z, radius=_body_outer_x(r, RIM_Z) + 0.004, tube=0.006,
        name="top_rim", material=mats["accent"], n_tube=12,
    )
    _ring_visual(
        can, r, z=FOOT_Z, radius=_body_outer_x(r, FOOT_Z), tube=0.004,
        name="rolled_foot", material=mats["accent"], n_tube=10,
    )
    # Corrugation rib bands (multiplicity, FIXED host visuals, host-conformal radii).
    for i in range(r.rib_count):
        t = (i + 1) / (r.rib_count + 1)
        z = FOOT_Z + t * (SHOULDER_Z - FOOT_Z)
        _ring_visual(
            can, r, z=z, radius=_body_outer_x(r, z) + 0.002, tube=0.0032,
            name=f"body_seam_{i}", material=mats["accent"] if i % 2 == 1 else mats["body"],
            n_tube=8,
        )
    # Fixed rear side handle, soldered to the -X wall at both ends.
    rb = _body_outer_x(r, 0.080)
    rt = _body_outer_x(r, 0.255)
    rear_handle = tube_from_spline_points(
        [
            (-(rb - 0.018), 0.0, 0.080),
            (-(rb + 0.070), 0.0, 0.115),
            (-(rt + 0.072), 0.0, 0.205),
            (-(rt - 0.012), 0.0, 0.255),
        ],
        radius=0.010,
        samples_per_segment=16,
        radial_segments=16,
        cap_ends=True,
    )
    can.visual(
        mesh_from_geometry(rear_handle, "watering_can_rear_handle"),
        name="rear_handle", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
        material=mats["body"],
    )
    # Vertical rolled sheet seam, host-conformal, on the rear-left wall (azimuth
    # 135°) — clear of the spout (+X), rear handle (-X) and the ±Y pivot arms.
    ys = r.y_scale
    cphi, sphi = math.cos(math.radians(135.0)), math.sin(math.radians(135.0))
    seam = sweep_profile_along_spline(
        [
            (_body_outer_x(r, z) * cphi, _body_outer_x(r, z) * ys * sphi, z)
            for z in (0.045, 0.145, 0.260)
        ],
        profile=rounded_rect_profile(0.007, 0.004, 0.0015),
        samples_per_segment=8,
        cap_profile=True,
        up_hint=(0.0, 0.0, 1.0),
    )
    can.visual(
        mesh_from_geometry(seam, "watering_can_vertical_sheet_seam"),
        name="vertical_seam", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
        material=mats["accent"],
    )


def _max_wall_y_over(r: ResolvedWateringCanConfig, z0: float, z1: float) -> float:
    """Widest wall radius (in Y, after y_scale) over the z-span a handle passes."""
    best = 0.0
    steps = 12
    for k in range(steps + 1):
        z = z0 + (z1 - z0) * k / steps
        best = max(best, _body_outer_x(r, z) * r.y_scale)
    return best


def _pivot_y(r: ResolvedWateringCanConfig) -> float:
    """Y where the bail washers / D-handle bosses sit — clear of the WIDEST wall
    the handle passes over (rim flare included), so straight arms never clip."""
    return _max_wall_y_over(r, LUG_Z, RIM_Z + 0.012) + 0.022


def _emit_bail_pivot_hardware(can, r: ResolvedWateringCanConfig, mats) -> None:
    """Side lug pegs + dark rivet heads — the bail / D-handle pivot (origin L288-304).

    Each lug is a horizontal peg bridging the +Y/-Y wall out to the pivot line, so
    it both anchors on the shell (inner end embedded) and reaches the washer/boss.
    """
    pivot_y = _pivot_y(r)
    wall_y = _body_outer_x(r, LUG_Z) * r.y_scale
    peg_len = (pivot_y - wall_y) + 0.030  # inner end sinks ~0.015 into the wall
    peg_center = wall_y - 0.015 + peg_len / 2.0
    for idx, sign in enumerate((-1.0, 1.0)):
        lug = (
            CylinderGeometry(0.014, peg_len, radial_segments=24, closed=True)
            .rotate_x(math.pi / 2.0)
            .translate(0.0, sign * peg_center, LUG_Z)
        )
        can.visual(mesh_from_geometry(lug, f"watering_can_bail_lug_{idx}"),
                   name=f"bail_lug_{idx}", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"), material=mats["body"])
        # Rivet head slightly PROUD of the lug boss (radius > lug) so its surface
        # intersects the lug — a fully-enclosed thinner rivet reads as an island.
        rivet = (
            CylinderGeometry(0.016, 0.018, radial_segments=20, closed=True)
            .rotate_x(math.pi / 2.0)
            .translate(0.0, sign * pivot_y, LUG_Z)
        )
        can.visual(mesh_from_geometry(rivet, f"watering_can_bail_rivet_{idx}"),
                   name=f"bail_rivet_{idx}", material_class_id="metal.blackened_gunmetal", material=mats["hardware"])


# ---------------------------------------------------------------------------
# Top mechanisms (each emits exactly one moving part + one REVOLUTE joint).
# ---------------------------------------------------------------------------
_BAIL_LIMIT = 0.95  # swing-bail strap (rad); wide strap clears the body all travel.
_DHANDLE_LIMIT = 0.5  # rigid D-handle (rad); inward-bowed arms dip into the body sooner.
_LID_UPPER = 1.5  # hinged half-lid open angle (rad).


def _emit_swing_bail(model, can, r: ResolvedWateringCanConfig, mats) -> str:
    """Swing bail strap, 1 REVOLUTE about +Y at the lug line (origin L325-361)."""
    bs = _pivot_y(r)
    apex = 0.220 * r.handle_height_scale
    bail = model.part("bail_handle")
    band = sweep_profile_along_spline(
        [
            (0.0, -bs, 0.0),
            (0.0, -(bs + 0.010), 0.075),
            (0.0, -(bs - 0.049), 0.185),
            (0.0, 0.0, apex),
            (0.0, (bs - 0.049), 0.185),
            (0.0, (bs + 0.010), 0.075),
            (0.0, bs, 0.0),
        ],
        profile=rounded_rect_profile(0.022, 0.008, 0.0025),
        samples_per_segment=14,
        cap_profile=True,
        up_hint=(1.0, 0.0, 0.0),
    )
    for y in (-bs, bs):
        band.merge(
            CylinderGeometry(0.019, 0.010, radial_segments=28, closed=True)
            .rotate_x(math.pi / 2.0)
            .translate(0.0, y, 0.0)
        )
    bail.visual(mesh_from_geometry(band, "watering_can_pivoting_bail_handle"),
                name="bail_band", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"), material=mats["body"])
    model.articulation(
        "can_to_bail",
        ArticulationType.REVOLUTE,
        parent=can,
        child=bail,
        origin=Origin(xyz=(0.0, 0.0, LUG_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=2.0, lower=-_BAIL_LIMIT, upper=_BAIL_LIMIT),
    )
    return "bail_band"


def _emit_d_handle(model, can, r: ResolvedWateringCanConfig, mats) -> str:
    """Rigid D-handle pivoting on the same lug axis (rec_..._handle_dhandle L325-400)."""
    lug_y = _pivot_y(r)
    hhs = r.handle_height_scale
    top = 0.185 * hhs
    crown = 0.200 * hhs
    geom = MeshGeometry()
    for sign in (-1.0, 1.0):
        geom.merge(
            tube_from_spline_points(
                [
                    (0.0, sign * lug_y, 0.0),
                    (0.0, sign * lug_y, 0.050),
                    (0.0, sign * lug_y, 0.095),
                    (0.0, sign * (lug_y - 0.044), 0.140),
                    (0.0, sign * (lug_y - 0.094), top),
                ],
                radius=0.008,
                samples_per_segment=12,
                radial_segments=14,
                cap_ends=False,
            )
        )
    geom.merge(
        tube_from_spline_points(
            [
                (0.0, -(lug_y - 0.094), top),
                (0.0, -(lug_y - 0.139), 0.196 * hhs),
                (0.0, 0.0, crown),
                (0.0, (lug_y - 0.139), 0.196 * hhs),
                (0.0, (lug_y - 0.094), top),
            ],
            radius=0.013,
            samples_per_segment=10,
            radial_segments=14,
            cap_ends=True,
        )
    )
    for y in (-lug_y, lug_y):
        geom.merge(
            CylinderGeometry(0.015, 0.012, radial_segments=28, closed=True)
            .rotate_x(math.pi / 2.0)
            .translate(0.0, y, 0.0)
        )
    d_handle = model.part("d_handle")
    d_handle.visual(mesh_from_geometry(geom, "watering_can_d_handle_body"),
                    name="d_handle_body", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"), material=mats["body"])
    model.articulation(
        "can_to_dhandle",
        ArticulationType.REVOLUTE,
        parent=can,
        child=d_handle,
        origin=Origin(xyz=(0.0, 0.0, LUG_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=6.0, velocity=2.0, lower=-_DHANDLE_LIMIT, upper=_DHANDLE_LIMIT
        ),
    )
    return "d_handle_body"


def _emit_hinged_lid(model, can, r: ResolvedWateringCanConfig, mats, *, assets) -> str:
    """Hinged half-lid over the fill mouth, 1 REVOLUTE about -Y (rec_..._lid_hinged L367-414).

    A full-diameter hinge rod on `can` (ends embedded in the walls) anchors the
    pivot; the lid carries knuckles captured on the rod (captured-pin, grandfathered).
    """
    # Rod ends sink into the solid rim wall (between inner & outer wall radius).
    rod_half = max(0.05, _body_outer_x(r, MOUTH_Z) * r.y_scale - 0.008)
    can.visual(
        mesh_from_geometry(
            CylinderGeometry(0.004, 2.0 * rod_half, radial_segments=20, closed=True)
            .rotate_x(math.pi / 2.0)
            .translate(0.0, 0.0, MOUTH_Z),
            "watering_can_lid_hinge_rod",
        ),
        name="lid_hinge_rod", material_class_id="metal.blackened_gunmetal",
        material=mats["hardware"],
    )
    lid_r = r.mouth_inner_r * r.width_scale * 0.88
    if r.y_scale == 1.0:
        disk = cq.Workplane("XY").circle(lid_r).extrude(0.004)
    else:
        disk = cq.Workplane("XY").ellipse(lid_r, lid_r * r.y_scale).extrude(0.004)
    cutter = (
        cq.Workplane("XY").center(-lid_r, 0.0).rect(lid_r * 2.0, lid_r * 2.2 + 0.02).extrude(0.012)
    )
    plate = disk.cut(cutter)
    grip = cq.Workplane("XY").center(lid_r - 0.012, 0.0).rect(0.024, 0.036).extrude(0.014)
    plate = plate.union(grip)
    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(plate, "watering_can_half_lid_plate", assets=assets, tolerance=0.001),
        name="lid_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
        material=mats["body"],
    )
    # Knuckles capturing the rod (give the lid part real contact with `can`).
    for idx, y in enumerate((-0.024, 0.024)):
        lid.visual(
            mesh_from_geometry(
                CylinderGeometry(0.007, 0.016, radial_segments=20, closed=True)
                .rotate_x(math.pi / 2.0)
                .translate(0.0, y, 0.0),
                f"watering_can_lid_knuckle_{idx}",
            ),
            name=f"lid_knuckle_{idx}", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_zinc", "rusted_steel", "enamel_green", "enamel_red", "cream", "copper"} else "plastic.opaque_glossy_molded"),
            material=mats["accent"],
        )
    model.articulation(
        "can_to_lid",
        ArticulationType.REVOLUTE,
        parent=can,
        child=lid,
        origin=Origin(xyz=(0.0, 0.0, MOUTH_Z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=_LID_UPPER),
    )
    return "lid_plate"


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_watering_can(
    config: WateringCanConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"category": "Agricultural", "small_class": "Watering can"},
    )
    mats = {
        key: model.material(f"watering_can_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    can = model.part("can")
    _emit_body_and_decorations(can, r, mats, assets=assets)
    _emit_spout(can, r, mats)
    _emit_spout_end(can, r, mats, assets=assets)

    # Pivot hardware is conditional on the mechanism (no idle/floating hardware).
    if r.top_mechanism in ("swing_bail", "d_handle"):
        _emit_bail_pivot_hardware(can, r, mats)

    if r.top_mechanism == "swing_bail":
        _emit_swing_bail(model, can, r, mats)
    elif r.top_mechanism == "d_handle":
        _emit_d_handle(model, can, r, mats)
    else:
        _emit_hinged_lid(model, can, r, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_watering_can(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_watering_can(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_watering_can_tests(
    object_model: ArticulatedObject,
    config: WateringCanConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    can = object_model.get_part("can")

    # ---- Captured-pin allowances (element-scoped, mirroring source run_tests). ----
    if r.top_mechanism == "swing_bail":
        moving = object_model.get_part("bail_handle")
        for idx in (0, 1):
            ctx.allow_overlap(
                can, moving, elem_a=f"bail_lug_{idx}", elem_b="bail_band",
                reason="The bail pivot washer is captured by the side lug/rivet stack.",
            )
            ctx.allow_overlap(
                can, moving, elem_a=f"bail_rivet_{idx}", elem_b="bail_band",
                reason="The dark rivet head is the same captured pivot stack as the washer.",
            )
    elif r.top_mechanism == "d_handle":
        moving = object_model.get_part("d_handle")
        for idx in (0, 1):
            ctx.allow_overlap(
                can, moving, elem_a=f"bail_lug_{idx}", elem_b="d_handle_body",
                reason="The D-handle pivot boss is captured by the side lug/rivet stack.",
            )
            ctx.allow_overlap(
                can, moving, elem_a=f"bail_rivet_{idx}", elem_b="d_handle_body",
                reason="The dark rivet head is the same captured pivot stack as the boss.",
            )
    else:  # hinged_lid
        moving = object_model.get_part("lid")
        for idx in (0, 1):
            ctx.allow_overlap(
                can, moving, elem_a="lid_hinge_rod", elem_b=f"lid_knuckle_{idx}",
                reason="The lid hinge knuckle is captured on the full-diameter hinge rod.",
            )
        ctx.allow_overlap(
            can, moving, elem_a="lid_hinge_rod", elem_b="lid_plate",
            reason="The half-lid plate closes down onto the mouth hinge rod.",
        )
        ctx.allow_overlap(
            can, moving, elem_a="top_rim", elem_b="lid_plate",
            reason="The closed half-lid seats on the rolled top rim of the mouth.",
        )

    # ---- Compiler baseline + Rule 5 motion gate. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    # ---- Identity / structure. ----
    ctx.check(
        "asset stays a watering can",
        object_model.meta.get("small_class") == "Watering can",
        details=f"meta={object_model.meta}",
    )
    for vis in ("body_shell", "spout_tube", "rear_handle", "vertical_seam", "top_rim"):
        ctx.check(f"visible watering-can subassembly: {vis}", can.get_visual(vis) is not None)

    rib_visuals = [v.name for v in can.visuals if v.name.startswith("body_seam_")]
    ctx.check(
        "N corrugation rib bands inlined (Rule 1 multiplicity)",
        len(rib_visuals) == r.rib_count,
        details=f"ribs={sorted(rib_visuals)} expected N={r.rib_count}",
    )

    has_rose = any(v.name == "rose_plate" for v in can.visuals)
    if r.spout_end == "rose_sprinkler":
        ctx.check("rose sprinkler plate present", has_rose)
    else:
        ctx.check("open nozzle has no rose plate", not has_rose)

    # Spout wall port really cuts the +X wall (inequality proof, spec §7).
    wall_at_port = _body_outer_x(r, PORT_Z)
    x0 = _port_cutter_x0(r)
    ctx.check(
        "spout port cutter spans through the +X wall",
        x0 < wall_at_port < x0 + 0.14 and x0 > 0.0,
        details=f"x0={x0:.4f} wall={wall_at_port:.4f} reach={x0 + 0.14:.4f}",
    )

    # ---- Mechanism joint topology + one targeted motion assertion. ----
    if r.top_mechanism == "swing_bail":
        j = object_model.get_articulation("can_to_bail")
        bail = object_model.get_part("bail_handle")
        ctx.check(
            "bail is REVOLUTE about +Y, bidirectional",
            j.articulation_type == ArticulationType.REVOLUTE
            and abs(j.axis[1]) > 0.99
            and j.motion_limits.lower < 0.0 < j.motion_limits.upper,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        rim = ctx.part_element_world_aabb(can, elem="top_rim")
        bail_box = ctx.part_world_aabb(bail)
        ctx.check(
            "upright bail rises above the rolled rim",
            bail_box is not None and rim is not None and bail_box[1][2] > rim[1][2] + 0.10,
            details=f"bail_top={bail_box[1][2] if bail_box else None} rim_top={rim[1][2] if rim else None}",
        )
        rest = ctx.part_world_aabb(bail)
        with ctx.pose({j: 0.7}):
            swung = ctx.part_world_aabb(bail)
        ctx.check(
            "positive bail swing moves the handle toward the spout (+X)",
            rest is not None and swung is not None and swung[1][0] > rest[1][0] + 0.08,
            details=f"rest_xmax={rest[1][0] if rest else None} swung_xmax={swung[1][0] if swung else None}",
        )
    elif r.top_mechanism == "d_handle":
        j = object_model.get_articulation("can_to_dhandle")
        dh = object_model.get_part("d_handle")
        ctx.check(
            "D-handle is REVOLUTE about +Y, bidirectional",
            j.articulation_type == ArticulationType.REVOLUTE
            and abs(j.axis[1]) > 0.99
            and j.motion_limits.lower < 0.0 < j.motion_limits.upper,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        rest = ctx.part_world_aabb(dh)
        with ctx.pose({j: j.motion_limits.upper * 0.9}):
            swung = ctx.part_world_aabb(dh)
        ctx.check(
            "positive D-handle swing moves the grip toward the spout (+X)",
            rest is not None and swung is not None and swung[1][0] > rest[1][0] + 0.04,
            details=f"rest_xmax={rest[1][0] if rest else None} swung_xmax={swung[1][0] if swung else None}",
        )
    else:  # hinged_lid
        j = object_model.get_articulation("can_to_lid")
        lid = object_model.get_part("lid")
        ctx.check(
            "hinged lid is REVOLUTE about -Y, opens upward only",
            j.articulation_type == ArticulationType.REVOLUTE
            and abs(j.axis[1]) > 0.99
            and j.motion_limits.lower == 0.0
            and j.motion_limits.upper > 0.5,
            details=f"type={j.articulation_type} axis={tuple(j.axis)} limits={j.motion_limits}",
        )
        closed = ctx.part_world_aabb(lid)
        with ctx.pose({j: _LID_UPPER * 0.8}):
            opened = ctx.part_world_aabb(lid)
        ctx.check(
            "hinged lid flips up to open the fill mouth",
            closed is not None and opened is not None and opened[1][2] > closed[1][2] + 0.03,
            details=f"closed_top={closed[1][2] if closed else None} open_top={opened[1][2] if opened else None}",
        )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded with rib_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "WateringCanConfig",
    "ResolvedWateringCanConfig",
    "build_watering_can",
    "build_seeded_watering_can",
    "config_from_seed",
    "resolve_config",
    "run_watering_can_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
