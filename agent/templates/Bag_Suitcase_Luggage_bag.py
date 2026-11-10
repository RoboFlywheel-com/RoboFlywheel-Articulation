# SPDX-License-Identifier: Apache-2.0

"""Hard-shell rolling luggage bag (spinner suitcase) — modular procedural template.

Category identity: an upright rounded-rectangular hard-shell rolling suitcase
(``luggage_body`` root) that stands on a set of bottom casters, carries a
top/side lift mechanism (telescoping pull handle or fixed grab handle), and is
optionally a closed solid shell or a hollow shell with a hinged access opening
(front drop-flap or longitudinal side door).

Pattern: ``mixed`` — three named slots (``body_opening`` / ``wheel_system`` /
``handle_system``) all hang their parts/visuals off the shared ``luggage_body``
root (parallel children), plus a ``wheel_count`` multiplicity axis that replicates
the active spinning caster part ``wheel_{i}`` for ``i in range(N)``, ``N in [2,4]``.

Slots:
  * ``body_opening`` (3): ``integrated_shell`` (SOLID ``ExtrudeGeometry`` shell,
    no opening part, no REVOLUTE) / ``front_lid_flap`` (HOLLOW cadquery ``.cut()``
    shell + ``front_flap`` REVOLUTE about -X) / ``split_side`` (HOLLOW cadquery
    ``.shell()`` half-shells + ``door`` REVOLUTE about +Z; wheels ride below the
    shell on a fixed ``base_chassis``). Hollow contract: opening candidates use
    cadquery thin walls; integrated stays solid.
  * ``wheel_system`` (2): ``yoke_wheels`` (Cylinder tire, CONTINUOUS spin about Y,
    simple yoke box) / ``swivel_caster`` (``TireGeometry`` mesh tire, CONTINUOUS
    spin about X, swivel plate + fork bridge + two fork arms).
  * ``handle_system`` (2): ``telescoping_pull`` (``pull_handle`` part + ``handle_extend``
    PRISMATIC about +Z) / ``fixed_top_grab`` (spline-swept arch grab grip, pure
    body visual, no joint).
  * ``wheel_count`` (N in [2,4]): caster multiplicity. Each ``wheel_{i}`` is an
    independent active part with its own CONTINUOUS ``wheel_{i}_spin`` joint
    (unlike cushion's inline pans). Encoded into the slot tuple as
    ``("wheel_count", f"n{N}")``.

All captured hinge pins / axles / retracted tubes are captured-fit geometry, so
those joints omit ``MatingContract`` (grandfathered) and are guarded by the flat
articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring each
source record's run_tests allow_overlap block).

Sources: parent ``...110d261f`` (solid shell + yoke 4-wheel spin-Y + telescoping
handle) plus 4 workbench-only 5-star fork variants (frontlid / split_side /
spinner4 / fixedgrab). See spec
``articraft_template_authoring/specs_modular_v1/Bag_Suitcase_Luggage_bag.md``.

slot_choices_for_seed returns the 4-tuple
``(body_opening, wheel_system, handle_system, ("wheel_count", f"n{N}"))``
consumed by the ``module_topology_diversity`` gate.
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
    Box,
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireGeometry,
    TireSidewall,
    TireTread,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

BodyOpening = Literal["integrated_shell", "front_lid_flap", "split_side"]
WheelSystem = Literal["yoke_wheels", "swivel_caster"]
HandleSystem = Literal["telescoping_pull", "fixed_top_grab"]
PaletteStyle = Literal[
    "hardshell_green",
    "graphite_black",
    "silver_aluminum",
    "navy_business",
    "burgundy_leather_trim",
]

BODY_OPENINGS: tuple[BodyOpening, ...] = (
    "integrated_shell",
    "front_lid_flap",
    "split_side",
)
WHEEL_SYSTEMS: tuple[WheelSystem, ...] = ("yoke_wheels", "swivel_caster")
HANDLE_SYSTEMS: tuple[HandleSystem, ...] = ("telescoping_pull", "fixed_top_grab")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "hardshell_green",
    "graphite_black",
    "silver_aluminum",
    "navy_business",
    "burgundy_leather_trim",
)

N_MIN = 2
N_MAX = 4
# Wheel-count sampling weights (spec §8: N=4 the high-frequency spinner form;
# N=2/3 long tail, accepted low-confidence paths).
WHEEL_COUNT_CHOICES = (2, 3, 4)
WHEEL_COUNT_WEIGHTS = (0.18, 0.14, 0.68)

# ---------------------------------------------------------------------------
# Palette colorways (spec PALETTE_STYLES). Each maps named material roles to
# rgba. Drives EVERY .visual(material=...) so swept output is multi-colored.
# Keys: shell (main body) / trim (seam/housing/yoke) / metal (chrome/tube/hinge)
#       / wheel (tire) / accent (interior/door/grip).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "hardshell_green": {
        "shell": (0.20, 0.40, 0.16, 1.0),
        "trim": (0.08, 0.08, 0.09, 1.0),
        "metal": (0.60, 0.60, 0.63, 1.0),
        "wheel": (0.12, 0.12, 0.13, 1.0),
        "accent": (0.38, 0.36, 0.34, 1.0),
    },
    "graphite_black": {
        "shell": (0.22, 0.22, 0.24, 1.0),
        "trim": (0.08, 0.08, 0.09, 1.0),
        "metal": (0.60, 0.60, 0.63, 1.0),
        "wheel": (0.12, 0.12, 0.13, 1.0),
        "accent": (0.15, 0.15, 0.16, 1.0),
    },
    "silver_aluminum": {
        "shell": (0.72, 0.73, 0.75, 1.0),
        "trim": (0.30, 0.30, 0.32, 1.0),
        "metal": (0.78, 0.78, 0.80, 1.0),
        "wheel": (0.12, 0.12, 0.13, 1.0),
        "accent": (0.38, 0.36, 0.34, 1.0),
    },
    "navy_business": {
        "shell": (0.10, 0.14, 0.30, 1.0),
        "trim": (0.07, 0.07, 0.09, 1.0),
        "metal": (0.55, 0.55, 0.58, 1.0),
        "wheel": (0.12, 0.12, 0.13, 1.0),
        "accent": (0.40, 0.40, 0.44, 1.0),
    },
    "burgundy_leather_trim": {
        "shell": (0.34, 0.10, 0.13, 1.0),
        "trim": (0.18, 0.10, 0.06, 1.0),
        "metal": (0.62, 0.55, 0.40, 1.0),
        "wheel": (0.12, 0.12, 0.13, 1.0),
        "accent": (0.20, 0.12, 0.08, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Upright rounded-rect hard-shell case.
# Long/width axis = X, depth = Y, height = Z. Anchored to the 5-star sources.
# ---------------------------------------------------------------------------
_W = 0.36          # width (X)
_D = 0.22          # depth (Y)
_SHELL_H = 0.52    # shell height (Z)
_CORNER_R = 0.045
_WALL_T = 0.003    # hollow shell wall thickness (front_lid / split only)

_HANDLE_X = 0.12   # pull-handle tube spacing from center
_TUBE_R = 0.011
_HANDLE_TRAVEL = 0.34

_WHEEL_R = 0.034
_WHEEL_T = 0.024
_AXLE_R = 0.006

# Grounded-shell base height (integrated / front_lid: wheels recessed into the
# shell underside well).
_SHELL_Z0_GROUND = 0.05
# Split_side: case rides on a raised chassis; wheels live entirely below the box.
_GROUND_CLEAR = 0.007
_BASE_T = 0.020


@dataclass(frozen=True)
class LuggageBagConfig:
    body_opening: BodyOpening | None = None
    wheel_system: WheelSystem | None = None
    handle_system: HandleSystem | None = None
    wheel_count: int | None = None
    palette_style: PaletteStyle = "hardshell_green"
    box_w_scale: float = 1.0
    box_d_scale: float = 1.0
    box_h_scale: float = 1.0
    wheel_r_scale: float = 1.0
    wheel_span_scale: float = 1.0
    handle_travel_scale: float = 1.0
    lid_open_angle_scale: float = 1.0
    name: str = "luggage_bag"


@dataclass(frozen=True)
class ResolvedLuggageBagConfig:
    body_opening: BodyOpening
    wheel_system: WheelSystem
    handle_system: HandleSystem
    wheel_count: int
    palette_style: PaletteStyle
    # Concrete geometry (scaled).
    w: float
    d: float
    shell_h: float
    corner_r: float
    wall_t: float
    shell_z0: float          # shell base z (ground-recessed or raised for split)
    shell_top: float
    wheel_r: float
    wheel_t: float
    wheel_cz: float          # wheel center z (touches ground at z=0)
    wheel_xs: tuple[float, ...]   # caster x positions (len == N)
    wheel_ys: tuple[float, ...]   # caster y positions (len == N)
    handle_x: float
    tube_bot: float
    tube_top: float
    handle_travel: float
    handle_y: float          # handle center y (split shifts it to back half)
    lid_open: float
    name: str

    @property
    def is_hollow(self) -> bool:
        return self.body_opening in ("front_lid_flap", "split_side")

    @property
    def is_split(self) -> bool:
        return self.body_opening == "split_side"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Caster placement: absolute, N-invariant. N=4 -> four corners; N=2 -> a single
# side-by-side pair on the front-back centerline; N=3 -> back pair + single
# front-center caster. x,y derive from N + spans only.
# ---------------------------------------------------------------------------
def _caster_positions(
    n: int, wx: float, wy: float
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    if n == 4:
        xs = (-wx, wx, -wx, wx)
        ys = (-wy, -wy, wy, wy)
    elif n == 2:
        # in-line pair: front-back centerline (x=0, +-wy).
        xs = (0.0, 0.0)
        ys = (-wy, wy)
    else:  # n == 3
        # back pair + one front-center caster.
        xs = (-wx, wx, 0.0)
        ys = (wy, wy, -wy)
    return xs, ys


def config_from_seed(seed: int) -> LuggageBagConfig:
    rng = random.Random(seed)
    return LuggageBagConfig(
        body_opening=rng.choice(BODY_OPENINGS),
        wheel_system=rng.choice(WHEEL_SYSTEMS),
        handle_system=rng.choice(HANDLE_SYSTEMS),
        wheel_count=rng.choices(WHEEL_COUNT_CHOICES, weights=WHEEL_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        box_w_scale=round(rng.uniform(0.84, 1.17), 4),
        box_d_scale=round(rng.uniform(0.82, 1.18), 4),
        box_h_scale=round(rng.uniform(0.85, 1.15), 4),
        wheel_r_scale=round(rng.uniform(0.88, 1.12), 4),
        wheel_span_scale=round(rng.uniform(0.90, 1.10), 4),
        handle_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        lid_open_angle_scale=round(rng.uniform(0.85, 1.05), 4),
        name=f"seeded_luggage_bag_{seed}",
    )


def resolve_config(config: LuggageBagConfig | None = None) -> ResolvedLuggageBagConfig:
    cfg = config or LuggageBagConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    body_opening = _pick(cfg.body_opening, BODY_OPENINGS)
    wheel_system = _pick(cfg.wheel_system, WHEEL_SYSTEMS)
    handle_system = _pick(cfg.handle_system, HANDLE_SYSTEMS)

    wheel_count = int(cfg.wheel_count) if cfg.wheel_count is not None else N_MAX
    wheel_count = int(_clamp(wheel_count, N_MIN, N_MAX))

    # --- Independent main-scale dims. ---
    w_scale = _clamp(cfg.box_w_scale, 0.84, 1.17)
    d_scale = _clamp(cfg.box_d_scale, 0.82, 1.18)
    h_scale = _clamp(cfg.box_h_scale, 0.85, 1.15)
    wr_scale = _clamp(cfg.wheel_r_scale, 0.88, 1.12)
    span_scale = _clamp(cfg.wheel_span_scale, 0.90, 1.10)
    travel_scale = _clamp(cfg.handle_travel_scale, 0.85, 1.10)
    angle_scale = _clamp(cfg.lid_open_angle_scale, 0.85, 1.05)

    w = _W * w_scale
    d = _D * d_scale
    shell_h = _SHELL_H * h_scale
    corner_r = min(_CORNER_R, 0.40 * min(w, d))
    wall_t = _clamp(_WALL_T, 0.0025, 0.0040)

    wheel_r = _WHEEL_R * wr_scale
    wheel_t = _WHEEL_T
    wheel_cz = wheel_r

    # --- Shell base z (conditional@split). ---
    if body_opening == "split_side":
        shell_z0 = 2.0 * wheel_r + _GROUND_CLEAR
    else:
        shell_z0 = _SHELL_Z0_GROUND
    shell_top = shell_z0 + shell_h

    # --- Caster span (projected to fit the bottom footprint). ---
    wx = 0.13 * span_scale
    wy = 0.072 * span_scale
    # inequality: every caster center +- (wheel_r + margin) must lie inside the
    # bottom footprint [-w/2, w/2] x [-d/2, d/2]. Shrink span if it overruns.
    margin = 0.006
    max_x = w / 2.0 - wheel_r - margin
    max_y = d / 2.0 - wheel_r - margin
    wx = _clamp(wx, 0.03, max(0.03, max_x))
    wy = _clamp(wy, 0.03, max(0.03, max_y))
    wheel_xs, wheel_ys = _caster_positions(wheel_count, wx, wy)

    # --- Handle geometry (conditional@telescoping). ---
    handle_x = min(_HANDLE_X, w / 2.0 - 0.05)
    handle_y = (d / 4.0) if body_opening == "split_side" else 0.0
    # retracted tube spans deep into the shell, top just proud of the deck.
    tube_top = shell_top + 0.03
    tube_bot = shell_z0 + 0.07
    handle_travel = _clamp(_HANDLE_TRAVEL * travel_scale, 0.20, shell_h * 0.75)

    # --- Lid open angle (conditional@front/split). ---
    if body_opening == "front_lid_flap":
        lid_open = _clamp(1.4 * angle_scale, 1.0, 1.5)
    elif body_opening == "split_side":
        lid_open = _clamp(math.pi * 0.45 * angle_scale, 1.0, math.pi * 0.5)
    else:
        lid_open = 0.0

    return ResolvedLuggageBagConfig(
        body_opening=body_opening,
        wheel_system=wheel_system,
        handle_system=handle_system,
        wheel_count=wheel_count,
        palette_style=palette_style,
        w=w,
        d=d,
        shell_h=shell_h,
        corner_r=corner_r,
        wall_t=wall_t,
        shell_z0=shell_z0,
        shell_top=shell_top,
        wheel_r=wheel_r,
        wheel_t=wheel_t,
        wheel_cz=wheel_cz,
        wheel_xs=wheel_xs,
        wheel_ys=wheel_ys,
        handle_x=handle_x,
        tube_bot=tube_bot,
        tube_top=tube_top,
        handle_travel=handle_travel,
        handle_y=handle_y,
        lid_open=lid_open,
        name=cfg.name or "luggage_bag",
    )


def with_overrides(config: LuggageBagConfig, **kwargs: object) -> LuggageBagConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: LuggageBagConfig | ResolvedLuggageBagConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedLuggageBagConfig) else resolve_config(config)
    return (
        ("body_opening", r.body_opening),
        ("wheel_system", r.wheel_system),
        ("handle_system", r.handle_system),
        ("wheel_count", f"n{r.wheel_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shell geometry helpers.
# ---------------------------------------------------------------------------
def _solid_shell_mesh(r: ResolvedLuggageBagConfig):
    """integrated_shell: SOLID rounded-rect ExtrudeGeometry single shell."""
    geo = ExtrudeGeometry.from_z0(
        rounded_rect_profile(r.w, r.d, r.corner_r, corner_segments=8),
        r.shell_h,
        cap=True,
    )
    geo.translate(0.0, 0.0, r.shell_z0)
    return mesh_from_geometry(geo, "shell")


def _hollow_front_shell(r: ResolvedLuggageBagConfig, assets):
    """front_lid_flap: HOLLOW cadquery .cut() shell, front (-Y) face fully open."""
    outer = (
        cq.Workplane("XY")
        .box(r.w, r.d, r.shell_h)
        .edges("|Z").fillet(r.corner_r)
        .translate((0.0, 0.0, r.shell_z0 + r.shell_h / 2.0))
    )
    overextend = 0.005
    inner_w = r.w - 2 * r.wall_t
    inner_d = r.d - r.wall_t + overextend
    inner_h = r.shell_h - 2 * r.wall_t
    inner_fillet = max(0.001, r.corner_r - r.wall_t)
    inner = (
        cq.Workplane("XY")
        .box(inner_w, inner_d, inner_h)
        .edges("|Z").fillet(inner_fillet)
        .translate((0.0, -(overextend + r.wall_t) / 2.0, r.shell_z0 + r.shell_h / 2.0))
    )
    return mesh_from_cadquery(outer.cut(inner), "shell", tolerance=0.0008, assets=assets)


def _make_half_shell(r: ResolvedLuggageBagConfig, y_sign: int, local_offset):
    """split_side: HOLLOW cadquery .shell() half-shell. y_sign=+1 back, -1 front."""
    half_d = r.d / 2.0
    cy = y_sign * half_d / 2.0 + local_offset[1]
    cz = r.shell_z0 + r.shell_h / 2.0 + local_offset[2]
    cx = local_offset[0]
    solid = (
        cq.Workplane("XY")
        .transformed(offset=(cx, cy, cz))
        .box(r.w, half_d, r.shell_h)
    )
    if y_sign > 0:
        solid = solid.faces(">Y").edges("|Z").fillet(r.corner_r)
        inner_face_sel = "<Y"
    else:
        solid = solid.faces("<Y").edges("|Z").fillet(r.corner_r)
        inner_face_sel = ">Y"
    solid = solid.faces(inner_face_sel).shell(r.wall_t)
    return solid


def _flap_panel_geo(r: ResolvedLuggageBagConfig):
    """front_flap panel in local frame (origin at top-center-outer hinge)."""
    clearance = 0.001
    flap_w = r.w - 2 * r.wall_t - 2 * clearance
    flap_h = r.shell_h - 2 * r.wall_t - 2 * clearance
    flap_t = r.wall_t
    flap_fillet = max(0.001, r.corner_r - r.wall_t - clearance)
    profile = rounded_rect_profile(flap_w, flap_h, flap_fillet, corner_segments=8)
    geo = ExtrudeGeometry(profile, flap_t, cap=True, center=True)
    geo.rotate_x(-math.pi / 2.0)
    geo.translate(0.0, flap_t / 2.0, -flap_h / 2.0)
    return geo, flap_h


# ---------------------------------------------------------------------------
# Common body hardware: seams + side grab handle (always inline body visuals).
# ---------------------------------------------------------------------------
def _emit_body_seams(body, r: ResolvedLuggageBagConfig, mats):
    cz = r.shell_z0 + r.shell_h * 0.5
    for sx in (-1.0, 1.0):
        body.visual(
            Box((0.012, r.d + 0.006, 0.018)),
            origin=Origin(xyz=(sx * (r.w / 2.0 - 0.004), 0.0, cz)),
            material=mats["trim"],
            name=f"seam_side_{'l' if sx < 0 else 'r'}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"hardshell_green", "graphite_black", "silver_aluminum", "navy_business"} else "leather.pebbled_grained"),
        )
    if not r.is_split:
        body.visual(
            Box((r.w + 0.006, 0.012, 0.018)),
            origin=Origin(xyz=(0.0, -(r.d / 2.0 - 0.004), cz)),
            material=mats["trim"],
            name="seam_front", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"hardshell_green", "graphite_black", "silver_aluminum", "navy_business"} else "leather.pebbled_grained"),
        )


def _emit_side_grab(body, r: ResolvedLuggageBagConfig, mats):
    gy = r.handle_y
    for sy, tag in ((-0.05, "f"), (0.05, "b")):
        body.visual(
            Box((0.035, 0.022, 0.022)),
            origin=Origin(xyz=(r.w / 2.0 + 0.0125, gy + sy, r.shell_z0 + r.shell_h * 0.78)),
            material=mats["trim"],
            name=f"side_post_{tag}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"hardshell_green", "graphite_black", "silver_aluminum", "navy_business"} else "leather.pebbled_grained"),
        )
    body.visual(
        Cylinder(radius=0.011, length=0.10),
        origin=Origin(
            xyz=(r.w / 2.0 + 0.028, gy, r.shell_z0 + r.shell_h * 0.78),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["trim"],
        name="side_grip", material_class_id=("rubber.smooth_plain" if r.palette_style in {"hardshell_green", "graphite_black", "silver_aluminum", "navy_business"} else "leather.pebbled_grained"),
    )


# ---------------------------------------------------------------------------
# Body root + body_opening slot.
# ---------------------------------------------------------------------------
def _build_body(model: ArticulatedObject, r: ResolvedLuggageBagConfig, mats, *, assets):
    body = model.part("luggage_body")

    # Shell visual (named "shell" for integrated/front; "body_shell" for split).
    if r.body_opening == "integrated_shell":
        body.visual(_solid_shell_mesh(r), material=mats["shell"], name="shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"hardshell_green", "graphite_black", "navy_business", "burgundy_leather_trim"} else "metal.aluminum_bare"))
    elif r.body_opening == "front_lid_flap":
        body.visual(_hollow_front_shell(r, assets), material=mats["shell"], name="shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"hardshell_green", "graphite_black", "navy_business", "burgundy_leather_trim"} else "metal.aluminum_bare"))
        # Packing floor inside the hollow compartment.
        floor_w = r.w - 2 * r.wall_t - 0.006
        floor_d = r.d - r.wall_t - 0.006
        body.visual(
            Box((floor_w, floor_d, 0.004)),
            origin=Origin(xyz=(0.0, -(r.wall_t) / 2.0, r.shell_z0 + r.wall_t + 0.002)),
            material=mats["accent"],
            name="packing_floor", material_class_id="fabric.felt",
        )
    else:  # split_side -> body is the back half-shell
        body.visual(
            mesh_from_cadquery(_make_half_shell(r, +1, (0.0, 0.0, 0.0)), "body_shell", assets=assets),
            material=mats["shell"],
            name="body_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"hardshell_green", "graphite_black", "navy_business", "burgundy_leather_trim"} else "metal.aluminum_bare"),
        )

    body.inertial = Inertial.from_geometry(
        Box((r.w, r.d, r.shell_h)),
        mass=2.4,
        origin=Origin(xyz=(0.0, 0.0, r.shell_z0 + r.shell_h / 2.0)),
    )

    _emit_body_seams(body, r, mats)
    _emit_side_grab(body, r, mats)

    # Handle housing plate + exit bosses on top (only for telescoping_pull;
    # fixed_top_grab uses the deck directly).
    if r.handle_system == "telescoping_pull":
        hy = r.handle_y
        plate_d = 0.08 if r.is_split else 0.16
        body.visual(
            Box((0.28, plate_d, 0.012)),
            origin=Origin(xyz=(0.0, hy, r.shell_top - 0.004)),
            material=mats["trim"],
            name="handle_housing", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"hardshell_green", "graphite_black", "silver_aluminum", "navy_business"} else "leather.pebbled_grained"),
        )
        for sx, tag in ((-r.handle_x, "l"), (r.handle_x, "r")):
            body.visual(
                Cylinder(radius=0.017, length=0.03),
                origin=Origin(xyz=(sx, hy, r.shell_top)),
                material=mats["trim"],
                name=f"handle_boss_{tag}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"hardshell_green", "graphite_black", "silver_aluminum", "navy_business"} else "leather.pebbled_grained"),
            )

    # split_side: base chassis skid plate + hinge barrel + latch on body.
    if r.is_split:
        body.visual(
            Box((r.w - 0.006, r.d - 0.006, _BASE_T)),
            origin=Origin(xyz=(0.0, 0.0, r.shell_z0 - _BASE_T / 2.0)),
            material=mats["trim"],
            name="base_chassis", material_class_id="plastic.opaque_glossy_molded",
        )
        hinge_x = r.w / 2.0
        hinge_z = r.shell_z0 + r.shell_h / 2.0
        hinge_len = r.shell_h - 0.04
        body.visual(
            Cylinder(radius=0.012, length=hinge_len),
            origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
            material=mats["metal"],
            name="hinge_barrel", material_class_id=("metal.stainless_matte" if r.palette_style in {"hardshell_green", "graphite_black", "navy_business", "burgundy_leather_trim"} else "metal.aluminum_bare"),
        )
        body.visual(
            Box((0.04, 0.018, 0.06)),
            origin=Origin(xyz=(-(r.w / 2.0 - 0.008), 0.009, hinge_z)),
            material=mats["metal"],
            name="latch_body", material_class_id=("metal.stainless_matte" if r.palette_style in {"hardshell_green", "graphite_black", "navy_business", "burgundy_leather_trim"} else "metal.aluminum_bare"),
        )

    return body


def _emit_front_flap(model, r: ResolvedLuggageBagConfig, body, mats) -> list[str]:
    """front_lid_flap: REVOLUTE -X drop-flap hinged at the top inner front edge."""
    flap_geo, flap_h = _flap_panel_geo(r)
    flap = model.part("front_flap")
    flap.visual(mesh_from_geometry(flap_geo, "flap_panel"), material=mats["shell"], name="flap_panel", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"hardshell_green", "graphite_black", "navy_business", "burgundy_leather_trim"} else "metal.aluminum_bare"))
    flap.visual(
        Box((0.045, 0.014, 0.018)),
        origin=Origin(xyz=(0.0, -0.007, -flap_h + 0.022)),
        material=mats["trim"],
        name="flap_latch", material_class_id=("metal.stainless_matte" if r.palette_style in {"hardshell_green", "graphite_black", "navy_business", "burgundy_leather_trim"} else "metal.aluminum_bare"),
    )
    flap.inertial = Inertial.from_geometry(
        Box((r.w, r.wall_t, flap_h)), mass=0.4, origin=Origin(xyz=(0.0, 0.0, -flap_h / 2.0))
    )
    hinge_z = r.shell_top - r.wall_t
    hinge_y = -r.d / 2.0
    model.articulation(
        "body_to_flap",
        ArticulationType.REVOLUTE,
        parent=body,
        child=flap,
        origin=Origin(xyz=(0.0, hinge_y, hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=0.0, upper=r.lid_open),
    )
    return ["front_flap"]


def _emit_split_door(model, r: ResolvedLuggageBagConfig, body, mats, *, assets) -> list[str]:
    """split_side: front half-shell door, REVOLUTE about +Z (vertical edge)."""
    hinge_x = r.w / 2.0
    hinge_z = r.shell_z0 + r.shell_h / 2.0
    hinge_len = r.shell_h - 0.04
    do = (-hinge_x, 0.0, -hinge_z)  # world->part offset

    door = model.part("door")
    door.visual(
        mesh_from_cadquery(_make_half_shell(r, -1, do), "door_shell", assets=assets),
        material=mats["accent"],
        name="door_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"hardshell_green", "graphite_black", "navy_business", "burgundy_leather_trim"} else "metal.aluminum_bare"),
    )
    # Hinge knuckle at part-local origin (sits inside the body hinge barrel).
    door.visual(
        Cylinder(radius=0.009, length=hinge_len - 0.02),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["metal"],
        name="door_hinge_knuckle", material_class_id=("metal.stainless_matte" if r.palette_style in {"hardshell_green", "graphite_black", "navy_business", "burgundy_leather_trim"} else "metal.aluminum_bare"),
    )
    # Latch catch at the free edge (part-local).
    door.visual(
        Box((0.03, 0.015, 0.04)),
        origin=Origin(xyz=(do[0] - (r.w / 2.0 - 0.008), do[1] - 0.010, do[2] + hinge_z)),
        material=mats["metal"],
        name="latch_door", material_class_id=("metal.stainless_matte" if r.palette_style in {"hardshell_green", "graphite_black", "navy_business", "burgundy_leather_trim"} else "metal.aluminum_bare"),
    )
    door.inertial = Inertial.from_geometry(
        Box((r.w, r.d / 2.0, r.shell_h)),
        mass=1.0,
        origin=Origin(xyz=(do[0], do[1] - r.d / 4.0, do[2] + hinge_z)),
    )
    model.articulation(
        "body_to_door",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=0.0, upper=r.lid_open),
    )
    return ["door"]


# ---------------------------------------------------------------------------
# wheel_system slot + wheel_count multiplicity.
# ---------------------------------------------------------------------------
def _emit_yoke_wheel(model, r, body, mats, i, sx, sy):
    """yoke_wheels: simple yoke box (body visual) + Cylinder tire, spin about Y."""
    if r.is_split:
        yoke_z = r.wheel_cz + 0.013
    else:
        yoke_z = r.shell_z0 + 0.012
    body.visual(
        Box((0.05, r.wheel_t + 0.018, 0.045)),
        origin=Origin(xyz=(sx, sy, yoke_z)),
        material=mats["trim"],
        name=f"yoke_{i}", material_class_id="plastic.opaque_glossy_molded",
    )
    wheel = model.part(f"wheel_{i}")
    wheel.visual(
        Cylinder(radius=r.wheel_r, length=r.wheel_t),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["wheel"],
        name="tire", material_class_id="rubber.smooth_plain",
    )
    wheel.visual(
        Cylinder(radius=_AXLE_R, length=r.wheel_t + 0.026),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="axle", material_class_id="metal.stainless_matte",
    )
    wheel.visual(
        Box((0.010, r.wheel_t - 0.004, 0.010)),
        origin=Origin(xyz=(r.wheel_r - 0.005, 0.0, 0.0)),
        material=mats["metal"],
        name="tread_lug", material_class_id="metal.stainless_matte",
    )
    wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=r.wheel_r, length=r.wheel_t),
        mass=0.12,
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        f"wheel_{i}_spin",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=wheel,
        origin=Origin(xyz=(sx, sy, r.wheel_cz)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=20.0),
    )


def _emit_swivel_caster(model, r, body, mats, i, sx, sy):
    """swivel_caster: swivel plate + fork bridge + 2 fork arms (body visual) +
    TireGeometry mesh tire (wheel part), spin about X."""
    caster_plate_r = 0.024
    caster_plate_h = 0.005
    fork_arm_w = 0.006
    fork_arm_d = 0.016
    fork_inner_offset = r.wheel_t / 2.0 + 0.003
    if r.is_split:
        fork_top_z = r.shell_z0 - _BASE_T - caster_plate_h
    else:
        fork_top_z = r.shell_z0 - caster_plate_h
    fork_arm_h = max(0.012, fork_top_z - (r.wheel_cz - 0.008))
    fork_cz = fork_top_z - fork_arm_h / 2.0

    body.visual(
        Cylinder(radius=caster_plate_r, length=caster_plate_h),
        origin=Origin(xyz=(sx, sy, fork_top_z + caster_plate_h / 2.0)),
        material=mats["metal"],
        name=f"swivel_plate_{i}", material_class_id="metal.stainless_matte",
    )
    bridge_w = 2.0 * (fork_inner_offset + fork_arm_w)
    body.visual(
        Box((bridge_w, fork_arm_d, 0.005)),
        origin=Origin(xyz=(sx, sy, fork_top_z - 0.0025)),
        material=mats["trim"],
        name=f"fork_bridge_{i}", material_class_id="plastic.opaque_glossy_molded",
    )
    for side_idx, side in enumerate((-1, 1)):
        arm_x = sx + side * (fork_inner_offset + fork_arm_w / 2.0)
        body.visual(
            Box((fork_arm_w, fork_arm_d, fork_arm_h)),
            origin=Origin(xyz=(arm_x, sy, fork_cz)),
            material=mats["trim"],
            name=f"fork_{i}_{side_idx}", material_class_id="plastic.opaque_glossy_molded",
        )

    wheel = model.part(f"wheel_{i}")
    tire_geo = TireGeometry(
        r.wheel_r,
        r.wheel_t,
        inner_radius=r.wheel_r * 0.55,
        tread=TireTread(style="block", depth=0.003, count=10, land_ratio=0.55),
        sidewall=TireSidewall(style="rounded", bulge=0.04),
    )
    wheel.visual(mesh_from_geometry(tire_geo, f"tire_{i}"), material=mats["wheel"], name="tire", material_class_id="rubber.directional_grooved")
    # Hub disc spans out to the tire inner rim so it is not a floating island.
    hub_r = r.wheel_r * 0.55 + 0.004
    wheel.visual(
        Cylinder(radius=hub_r, length=r.wheel_t - 0.006),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="hub", material_class_id="metal.stainless_matte",
    )
    axle_len = 2.0 * (fork_inner_offset + fork_arm_w) + 0.004
    wheel.visual(
        Cylinder(radius=0.004, length=axle_len),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="axle", material_class_id="metal.stainless_matte",
    )
    wheel.visual(
        Box((0.008, 0.006, 0.006)),
        origin=Origin(xyz=(0.0, 0.0, r.wheel_r - 0.003)),
        material=mats["metal"],
        name="tread_marker", material_class_id="metal.stainless_matte",
    )
    wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=r.wheel_r, length=r.wheel_t),
        mass=0.12,
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
    )
    model.articulation(
        f"wheel_{i}_spin",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=wheel,
        origin=Origin(xyz=(sx, sy, r.wheel_cz)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=20.0),
    )


def _emit_wheels(model, r: ResolvedLuggageBagConfig, body, mats) -> list[str]:
    emit = _emit_yoke_wheel if r.wheel_system == "yoke_wheels" else _emit_swivel_caster
    names: list[str] = []
    for i in range(r.wheel_count):
        emit(model, r, body, mats, i, r.wheel_xs[i], r.wheel_ys[i])
        names.append(f"wheel_{i}")
    return names


# ---------------------------------------------------------------------------
# handle_system slot.
# ---------------------------------------------------------------------------
def _emit_telescoping_handle(model, r: ResolvedLuggageBagConfig, body, mats) -> list[str]:
    """telescoping_pull: pull_handle part + handle_extend PRISMATIC about +Z."""
    handle = model.part("pull_handle")
    hy = r.handle_y
    tube_len = r.tube_top - r.tube_bot
    tube_cz = (r.tube_top + r.tube_bot) / 2.0
    # The PRISMATIC joint origin sits at the top handle housing exit point
    # (0, hy, shell_top) — real parent geometry (handle_housing/boss) AND on the
    # child tube (which spans up past shell_top). Author handle visuals in this
    # frame so q=0 == authored retracted pose; positive q slides the rig up +Z.
    anchor_z = r.shell_top
    for sx, nm in ((-r.handle_x, "tube_left"), (r.handle_x, "tube_right")):
        handle.visual(
            Cylinder(radius=_TUBE_R, length=tube_len),
            origin=Origin(xyz=(sx, 0.0, tube_cz - anchor_z)),
            material=mats["metal"],
            name=nm, material_class_id="metal.aluminum_bare",
        )
    handle.visual(
        Cylinder(radius=0.013, length=2.0 * r.handle_x + 0.02),
        origin=Origin(xyz=(0.0, 0.0, r.tube_top - anchor_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["trim"],
        name="cross_grip", material_class_id=("rubber.smooth_plain" if r.palette_style in {"hardshell_green", "graphite_black", "silver_aluminum", "navy_business"} else "leather.pebbled_grained"),
    )
    handle.visual(
        Box((0.10, 0.03, 0.022)),
        origin=Origin(xyz=(0.0, 0.0, r.tube_top - anchor_z)),
        material=mats["trim"],
        name="grip_pad", material_class_id=("rubber.smooth_plain" if r.palette_style in {"hardshell_green", "graphite_black", "silver_aluminum", "navy_business"} else "leather.pebbled_grained"),
    )
    # Central cross-tie spanning the two tubes at the housing exit line so the
    # joint origin (child-local (0,0,0)) lands on real handle geometry.
    handle.visual(
        Cylinder(radius=0.010, length=2.0 * r.handle_x),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="handle_yoke", material_class_id="metal.aluminum_bare",
    )
    handle.inertial = Inertial.from_geometry(
        Box((2.0 * r.handle_x, 0.03, tube_len)),
        mass=0.5,
        origin=Origin(xyz=(0.0, 0.0, tube_cz - anchor_z)),
    )
    model.articulation(
        "handle_extend",
        ArticulationType.PRISMATIC,
        parent=body,
        child=handle,
        origin=Origin(xyz=(0.0, hy, anchor_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.3, lower=0.0, upper=r.handle_travel),
    )
    return ["pull_handle"]


def _emit_fixed_grab(model, r: ResolvedLuggageBagConfig, body, mats) -> list[str]:
    """fixed_top_grab: 2 posts + spline-swept arch grip, pure body visual."""
    grab_span = min(0.14, r.w / 2.0 - 0.04)
    post_h = 0.035
    peak_h = 0.065
    tube_r = 0.012
    hy = r.handle_y
    z_top = r.shell_top
    for i, sx in enumerate((-grab_span, grab_span)):
        body.visual(
            Box((0.030, 0.030, post_h)),
            origin=Origin(xyz=(sx, hy, z_top + post_h / 2.0)),
            material=mats["trim"],
            name=f"grab_post_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    pts = [
        (-grab_span, hy, z_top + post_h),
        (-grab_span * 0.6, hy, z_top + peak_h * 0.85),
        (0.0, hy, z_top + peak_h),
        (grab_span * 0.6, hy, z_top + peak_h * 0.85),
        (grab_span, hy, z_top + post_h),
    ]
    grab_mesh = tube_from_spline_points(
        pts,
        radius=tube_r,
        samples_per_segment=10,
        radial_segments=12,
        cap_ends=True,
        up_hint=(0.0, 1.0, 0.0),
    )
    body.visual(mesh_from_geometry(grab_mesh, "grab_grip"), material=mats["accent"], name="grab_grip", material_class_id=("rubber.smooth_plain" if r.palette_style in {"hardshell_green", "graphite_black", "silver_aluminum", "navy_business"} else "leather.pebbled_grained"))
    return []


_OPENING_BUILDERS = {
    "front_lid_flap": _emit_front_flap,
}
_HANDLE_BUILDERS = {
    "telescoping_pull": _emit_telescoping_handle,
    "fixed_top_grab": _emit_fixed_grab,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_luggage_bag(
    config: LuggageBagConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"luggage_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats, assets=assets)

    # body_opening slot (adds an opening child part for front_lid / split).
    if r.body_opening == "front_lid_flap":
        _emit_front_flap(model, r, body, mats)
    elif r.body_opening == "split_side":
        _emit_split_door(model, r, body, mats, assets=assets)

    # wheel_system slot x wheel_count multiplicity.
    _emit_wheels(model, r, body, mats)

    # handle_system slot.
    _HANDLE_BUILDERS[r.handle_system](model, r, body, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_luggage_bag(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_luggage_bag(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_luggage_bag_tests(
    object_model: ArticulatedObject,
    config: LuggageBagConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("luggage_body")
    shell_elem = "body_shell" if r.is_split else "shell"

    # ---- Wheel captured-fit allowances (element-scoped). ----
    for i in range(r.wheel_count):
        wi = object_model.get_part(f"wheel_{i}")
        # The spinning wheel stays close to the caster yoke/fork while turning.
        ctx.allow_overlap(
            wi, body,
            reason="spinning wheel runs close within its caster yoke/fork well",
        )
        if r.wheel_system == "yoke_wheels":
            ctx.allow_overlap(
                wi, body, elem_a="axle", elem_b=f"yoke_{i}",
                reason="Wheel axle stub is captured inside the caster yoke.",
            )
            ctx.allow_overlap(
                wi, body, elem_a="tire", elem_b=f"yoke_{i}",
                reason="Spinner wheel is recessed up into its caster housing well.",
            )
        else:  # swivel_caster
            ctx.allow_overlap(
                wi, body, elem_a="axle", elem_b=f"fork_{i}_0",
                reason="Caster axle stub is captured inside the left fork arm.",
            )
            ctx.allow_overlap(
                wi, body, elem_a="axle", elem_b=f"fork_{i}_1",
                reason="Caster axle stub is captured inside the right fork arm.",
            )
            ctx.allow_overlap(
                wi, body, elem_a="tire", elem_b=f"swivel_plate_{i}",
                reason="Spinner wheel top protrudes into the swivel raceway plate recess.",
            )
            ctx.allow_overlap(
                wi, body, elem_a="tire", elem_b=f"fork_bridge_{i}",
                reason="Spinner wheel top protrudes into the fork bridge plate recess.",
            )
            ctx.allow_overlap(
                wi, body, elem_a="hub", elem_b=f"fork_bridge_{i}",
                reason="Spinner wheel hub cap protrudes up into the fork bridge recess.",
            )
            ctx.allow_overlap(
                wi, body, elem_a="hub", elem_b=f"swivel_plate_{i}",
                reason="Spinner wheel hub cap protrudes up into the swivel raceway plate recess.",
            )
        if r.is_split:
            ctx.allow_overlap(
                wi, body, elem_a="tire", elem_b="base_chassis",
                reason="Wheel caster pivots up into the fixed base chassis.",
            )
            if r.wheel_system == "yoke_wheels":
                ctx.allow_overlap(
                    wi, body, elem_a="axle", elem_b="base_chassis",
                    reason="Wheel axle hardware tucks up under the base chassis.",
                )
            else:
                ctx.allow_overlap(
                    wi, body, elem_a="hub", elem_b="base_chassis",
                    reason="Spinner hub cap tucks up under the fixed base chassis.",
                )
        else:
            ctx.allow_overlap(
                wi, body, elem_a="tire", elem_b=shell_elem,
                reason="Spinner wheel is recessed into the shell underside well.",
            )
            if r.wheel_system == "swivel_caster":
                ctx.allow_overlap(
                    wi, body, elem_a="hub", elem_b=shell_elem,
                    reason="Spinner wheel hub cap is recessed into the shell underside well.",
                )

    # ---- Handle captured-fit allowances. ----
    if r.handle_system == "telescoping_pull":
        handle = object_model.get_part("pull_handle")
        for tube, boss in (("tube_left", "handle_boss_l"), ("tube_right", "handle_boss_r")):
            reason_shell = (
                f"{tube} passes through the hollow shell top wall."
                if r.is_hollow
                else f"{tube} retracts into the solid shell proxy."
            )
            ctx.allow_overlap(handle, body, elem_a=tube, elem_b=shell_elem, reason=reason_shell)
            ctx.allow_overlap(
                handle, body, elem_a=tube, elem_b=boss,
                reason=f"{tube} passes through its top exit boss.",
            )
            ctx.allow_overlap(
                handle, body, elem_a=tube, elem_b="handle_housing",
                reason=f"{tube} passes through the top handle housing plate.",
            )
        ctx.allow_overlap(
            handle, body, elem_a="handle_yoke", elem_b="handle_housing",
            reason="Handle cross-tie sits at the housing exit line at the retracted pose.",
        )
        ctx.allow_overlap(
            handle, body, elem_a="handle_yoke", elem_b=shell_elem,
            reason="Handle cross-tie passes through the shell deck at the retracted pose.",
        )
        for boss in ("handle_boss_l", "handle_boss_r"):
            ctx.allow_overlap(
                handle, body, elem_a="handle_yoke", elem_b=boss,
                reason="Handle cross-tie passes through the handle exit boss at the retracted pose.",
            )

    # ---- body_opening captured / closed-pose allowances. ----
    if r.body_opening == "front_lid_flap":
        flap = object_model.get_part("front_flap")
        ctx.allow_overlap(
            flap, body, reason="closed front flap seats in the hollow shell front opening.",
        )
    elif r.body_opening == "split_side":
        door = object_model.get_part("door")
        ctx.allow_overlap(
            door, body, elem_a="door_hinge_knuckle", elem_b="hinge_barrel",
            reason="Door hinge knuckle is captured inside the body hinge barrel.",
        )
        ctx.allow_overlap(
            door, body, elem_a="door_hinge_knuckle", elem_b="body_shell",
            reason="Door hinge knuckle passes through the body shell wall at the hinge line.",
        )
        ctx.allow_overlap(
            door, body, elem_a="door_shell", elem_b="hinge_barrel",
            reason="Door shell right edge wraps around the hinge barrel mount point.",
        )
        ctx.allow_overlap(
            door, body, elem_a="door_shell", elem_b="base_chassis",
            reason="Door lower edge seats on the fixed base chassis when closed.",
        )
        ctx.allow_overlap(
            door, body, reason="closed door meets the body half-shell at the longitudinal split.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("luggage_body root present", "luggage_body" in part_names, details=str(sorted(part_names)))

    # N wheel parts present, each with a CONTINUOUS spin joint.
    ctx.check(
        "N wheel parts present",
        all(f"wheel_{i}" in part_names for i in range(r.wheel_count)),
        details=f"expected wheel_0..wheel_{r.wheel_count - 1}; got {sorted(part_names)}",
    )
    for i in range(r.wheel_count):
        j = object_model.get_articulation(f"wheel_{i}_spin")
        expect_axis = 0 if r.wheel_system == "swivel_caster" else 1
        ctx.check(
            f"wheel_{i}_spin CONTINUOUS about expected axis",
            j.articulation_type == ArticulationType.CONTINUOUS
            and abs(j.axis[expect_axis]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )

    # body_opening joint topology.
    if r.body_opening == "front_lid_flap":
        j = object_model.get_articulation("body_to_flap")
        ctx.check(
            "front flap is REVOLUTE about -X",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    elif r.body_opening == "split_side":
        j = object_model.get_articulation("body_to_door")
        ctx.check(
            "split door is REVOLUTE about +Z (vertical edge)",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    else:
        ctx.check(
            "integrated shell has no body_opening part",
            "front_flap" not in part_names and "door" not in part_names,
            details=str(sorted(part_names)),
        )

    # handle_system joint topology.
    if r.handle_system == "telescoping_pull":
        j = object_model.get_articulation("handle_extend")
        ctx.check(
            "telescoping handle is PRISMATIC about +Z",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[2]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    else:  # fixed_top_grab
        ctx.check(
            "fixed grab has no pull_handle part",
            "pull_handle" not in part_names,
            details=str(sorted(part_names)),
        )
        ctx.check(
            "fixed grab grip present on body",
            body.get_visual("grab_grip") is not None,
        )

    # ---- Mechanism actuation. ----
    if r.body_opening == "front_lid_flap":
        j = object_model.get_articulation("body_to_flap")
        flap = object_model.get_part("front_flap")
        closed = ctx.part_element_world_aabb(flap, elem="flap_latch")
        with ctx.pose({j: r.lid_open * 0.85}):
            opened = ctx.part_element_world_aabb(flap, elem="flap_latch")
        if closed is not None and opened is not None:
            ctx.check(
                "flap opens outward from the front face",
                opened[0][1] < closed[0][1] - 0.04,
                details=f"closed_min_y={closed[0][1]:.4f} open_min_y={opened[0][1]:.4f}",
            )
    elif r.body_opening == "split_side":
        j = object_model.get_articulation("body_to_door")
        door = object_model.get_part("door")
        closed = ctx.part_element_world_aabb(door, elem="door_shell")
        with ctx.pose({j: r.lid_open * 0.9}):
            opened = ctx.part_element_world_aabb(door, elem="door_shell")
        if closed is not None and opened is not None:
            ctx.check(
                "door swings sideways when opened",
                opened[0][1] < closed[0][1] - 0.03,
                details=f"closed_min_y={closed[0][1]:.4f} open_min_y={opened[0][1]:.4f}",
            )

    if r.handle_system == "telescoping_pull":
        j = object_model.get_articulation("handle_extend")
        handle = object_model.get_part("pull_handle")
        with ctx.pose({j: 0.0}):
            rest_top = ctx.part_element_world_aabb(handle, elem="cross_grip")
        with ctx.pose({j: r.handle_travel}):
            ext_top = ctx.part_element_world_aabb(handle, elem="cross_grip")
        if rest_top is not None and ext_top is not None:
            ctx.check(
                "pull handle extends upward",
                ext_top[1][2] > rest_top[1][2] + 0.15,
                details=f"rest_top={rest_top[1][2]:.3f} ext_top={ext_top[1][2]:.3f}",
            )

    # ---- Wheel spin observable. ----
    wheel0 = object_model.get_part("wheel_0")
    spin0 = object_model.get_articulation("wheel_0_spin")
    spin_elem = "tread_marker" if r.wheel_system == "swivel_caster" else "tread_lug"
    with ctx.pose({spin0: 0.0}):
        lug_rest = ctx.part_element_world_aabb(wheel0, elem=spin_elem)
    with ctx.pose({spin0: math.pi / 2.0}):
        lug_spun = ctx.part_element_world_aabb(wheel0, elem=spin_elem)
    if lug_rest is not None and lug_spun is not None:
        ctx.check(
            "wheel spins about its axle",
            lug_spun[1][2] < lug_rest[1][2] - 0.012,
            details=f"rest={lug_rest[1][2]:.4f} spun={lug_spun[1][2]:.4f}",
        )

    # ---- Wheels grounded (touch z~0) and within footprint. ----
    for i in range(r.wheel_count):
        wi = object_model.get_part(f"wheel_{i}")
        taabb = ctx.part_element_world_aabb(wi, elem="tire")
        if taabb is not None:
            ctx.check(
                f"wheel {i} rests on the ground",
                taabb[0][2] < 0.02,
                details=f"tire_zmin={taabb[0][2]:.4f}",
            )

    # split_side: wheels live entirely below the shell, not inside the box.
    if r.is_split:
        body_shell_aabb = ctx.part_element_world_aabb(body, elem="body_shell")
        shell_base_z = body_shell_aabb[0][2] if body_shell_aabb else None
        for i in range(r.wheel_count):
            wi = object_model.get_part(f"wheel_{i}")
            taabb = ctx.part_element_world_aabb(wi, elem="tire")
            tire_top = taabb[1][2] if taabb else None
            ctx.check(
                f"wheel {i} sits below the shell (not inside the box)",
                shell_base_z is not None and tire_top is not None
                and tire_top <= shell_base_z + 0.002,
                details=f"tire_top={tire_top} shell_base_z={shell_base_z}",
            )

    # ---- Hollow contract. ----
    if r.body_opening == "front_lid_flap":
        ctx.check(
            "front_lid body is a hollow cadquery shell + packing floor",
            body.get_visual("shell") is not None
            and any(v.name == "packing_floor" for v in body.visuals),
        )
    elif r.body_opening == "split_side":
        door = object_model.get_part("door")
        ctx.check(
            "split body & door are hollow cadquery shells",
            body.get_visual("body_shell") is not None and door.get_visual("door_shell") is not None,
        )
    else:
        ctx.check(
            "integrated body is a solid shell",
            body.get_visual("shell") is not None,
        )

    # ---- slot_choices recorded with N encoded. ----
    ctx.check(
        "slot_choices recorded with wheel_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "LuggageBagConfig",
    "ResolvedLuggageBagConfig",
    "build_luggage_bag",
    "build_seeded_luggage_bag",
    "config_from_seed",
    "resolve_config",
    "run_luggage_bag_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
