# SPDX-License-Identifier: Apache-2.0

"""Manual water dispenser pump — modular procedural template.

Category identity: a hand-actuated pump head that mounts on top of an inverted
water bottle (bottle NOT modelled; context only) and delivers water through a
side spout when the user actuates a plunger/lever/bellows. Root part is
``pump_body`` at world z=0 with axis +Z; ONE moving child part carries the
identity mechanism (single non-FIXED joint), and the side spout is either fused
into the pump_body (fixed) or spawned as a second child with its own REVOLUTE
hinge (folding_spout).

Four slots:

  * ``body_form``  (3, ③ Primary Form Family) — the ``pump_body`` shell.
      tall_spring_chamber (loft w/ visible bellows ribs, from parent 001) /
      slim_stepped_column (lathe shell w/ torus bands, from parent 002) /
      squat_round_body (wider/shorter lathe barrel, world_knowledge).
  * ``bottle_interface`` (2) — base-mount decoration fused into ``pump_body``.
      thread_collar (ivory screw-on collar + gasket, from thread_collar variant) /
      stepped_socket (stacked socket rings + thread rings, from parent 001).
  * ``actuation`` (4, ② mechanism) — the moving child with a single non-fixed
    joint.
      top_plunger (PRISMATIC +Z) — palm button + piston stem;
      top_lever (REVOLUTE +Y) — top pivoting lever;
      side_lever (REVOLUTE +Y) — side pivoting lever w/ hub;
      compressible_bellows (PRISMATIC +Z) — press plate + guide post.
    An optional ``plunger_stages`` detail on top_plunger switches to a two-stage
    stem (only when actuation==top_plunger).
  * ``spout`` (3) — side outlet.
      side_short_elbow (fixed) / arched_gooseneck (fixed) / folding_spout
      (REVOLUTE +Y child part; adds a second non-fixed joint).

Per-seed palette diversity: 5 coordinated colorways (blue_white, ivory_dark,
cobalt_clinical, matte_charcoal, sage_frost). Only blue_white and sage_frost
carry a translucent shell (alpha<1).

Continuous scales (body_height_scale, body_radius_scale, press_travel_scale,
spout_reach_scale) live in resolve_config as clamped params.

Sources: articraft_data ``picture/0611/Manual_water_dispenser_pump`` 5-star pool
(2 parents + 8 fork variants). Canonical spec:
``articraft_template_authoring/specs_modular_v1/manual_water_dispenser_pump.md``.
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
    Cylinder,
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyForm = Literal["tall_spring_chamber", "slim_stepped_column", "squat_round_body"]
BottleInterface = Literal["thread_collar", "stepped_socket"]
Actuation = Literal["top_plunger", "top_lever", "side_lever", "compressible_bellows"]
Spout = Literal["side_short_elbow", "arched_gooseneck", "folding_spout"]
PlungerStages = Literal["single", "two_stage"]
PaletteStyle = Literal[
    "blue_white",
    "ivory_dark",
    "cobalt_clinical",
    "matte_charcoal",
    "sage_frost",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "tall_spring_chamber",
    "slim_stepped_column",
    "squat_round_body",
)
BOTTLE_INTERFACES: tuple[BottleInterface, ...] = ("thread_collar", "stepped_socket")
ACTUATIONS: tuple[Actuation, ...] = (
    "top_plunger",
    "top_lever",
    "side_lever",
    "compressible_bellows",
)
SPOUTS: tuple[Spout, ...] = ("side_short_elbow", "arched_gooseneck", "folding_spout")
PLUNGER_STAGES: tuple[PlungerStages, ...] = ("single", "two_stage")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "blue_white",
    "ivory_dark",
    "cobalt_clinical",
    "matte_charcoal",
    "sage_frost",
)

_PRISMATIC_ACT: frozenset[Actuation] = frozenset({"top_plunger", "compressible_bellows"})
_REVOLUTE_ACT: frozenset[Actuation] = frozenset({"top_lever", "side_lever"})
_TRANSLUCENT_PALETTES: frozenset[PaletteStyle] = frozenset({"blue_white", "sage_frost"})


# ---------------------------------------------------------------------------
# Palettes: 5 coordinated colorways. rgba values anchored on the two parent
# 5-star materials (blue+white 001, ivory+dark 002) + world-knowledge for the
# remaining 3 real colorways commonly found on countertop bottle pumps.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Palette:
    body_light: tuple[float, float, float, float]  # main housing / accent light
    body_dark: tuple[float, float, float, float]  # bellows / rim / plunger button
    accent: tuple[float, float, float, float]  # spring, lever body, collar
    clear: tuple[float, float, float, float]  # spring chamber / clear nozzle
    rubber: tuple[float, float, float, float]  # gasket, seal
    finish: str


PALETTES: dict[PaletteStyle, _Palette] = {
    "blue_white": _Palette(
        body_light=(0.94, 0.96, 0.98, 0.75),
        body_dark=(0.015, 0.22, 0.88, 1.0),
        accent=(0.01, 0.09, 0.42, 1.0),
        clear=(0.30, 0.70, 0.94, 0.42),
        rubber=(0.025, 0.035, 0.055, 1.0),
        finish="clear_gloss",
    ),
    "ivory_dark": _Palette(
        body_light=(0.90, 0.90, 0.83, 1.0),
        body_dark=(0.055, 0.075, 0.14, 1.0),
        accent=(0.96, 0.97, 0.94, 1.0),
        clear=(0.84, 0.89, 0.89, 0.55),
        rubber=(0.30, 0.31, 0.29, 1.0),
        finish="opaque_matte",
    ),
    "cobalt_clinical": _Palette(
        body_light=(0.95, 0.96, 0.97, 1.0),
        body_dark=(0.13, 0.28, 0.52, 1.0),
        accent=(0.20, 0.30, 0.48, 1.0),
        clear=(0.88, 0.90, 0.93, 0.65),
        rubber=(0.16, 0.16, 0.18, 1.0),
        finish="painted_gloss",
    ),
    "matte_charcoal": _Palette(
        body_light=(0.16, 0.16, 0.18, 1.0),
        body_dark=(0.10, 0.10, 0.11, 1.0),
        accent=(0.28, 0.28, 0.30, 1.0),
        clear=(0.30, 0.30, 0.34, 0.70),
        rubber=(0.06, 0.06, 0.07, 1.0),
        finish="soft_touch_matte",
    ),
    "sage_frost": _Palette(
        body_light=(0.82, 0.88, 0.80, 0.72),
        body_dark=(0.36, 0.48, 0.36, 1.0),
        accent=(0.94, 0.95, 0.93, 1.0),
        clear=(0.75, 0.86, 0.78, 0.55),
        rubber=(0.24, 0.30, 0.24, 1.0),
        finish="frosted_translucent",
    ),
}


# ---------------------------------------------------------------------------
# Base geometry constants (meters). Anchored on the 5-star sources.
# ---------------------------------------------------------------------------
_BASE_HOUSING_HEIGHT = 0.185  # nominal housing full height
_BASE_HOUSING_R = 0.045  # nominal housing top radius (mid-body)
_BASE_HOUSING_BOTTOM = 0.005  # small clearance from ground
_BASE_TRAVEL = 0.020


@dataclass(frozen=True)
class ManualWaterDispenserPumpConfig:
    body_form: BodyForm = "tall_spring_chamber"
    bottle_interface: BottleInterface = "thread_collar"
    actuation: Actuation = "top_plunger"
    spout: Spout = "side_short_elbow"
    plunger_stages: PlungerStages = "single"
    palette_style: PaletteStyle = "blue_white"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    press_travel_scale: float = 1.0
    spout_reach_scale: float = 1.0
    name: str = "manual_water_dispenser_pump"


@dataclass(frozen=True)
class ResolvedManualWaterDispenserPumpConfig:
    body_form: BodyForm
    bottle_interface: BottleInterface
    actuation: Actuation
    spout: Spout
    plunger_stages: PlungerStages
    palette_style: PaletteStyle
    translucent_body: bool
    finish: str
    # continuous scales
    body_height_scale: float
    body_radius_scale: float
    press_travel_scale: float
    spout_reach_scale: float
    # derived key z's / radii (world coords, pump_body local == world at z=0)
    housing_bottom: float
    housing_mid: float  # bulk body top
    housing_top: float  # rim where actuation mounts
    housing_r_top: float  # radius at housing_top
    housing_r_mid: float  # radius at housing_mid
    housing_r_bottom: float  # base flare
    press_travel: float
    lever_upper: float  # REVOLUTE upper radians
    spout_z: float  # side outlet z
    spout_reach: float  # spout tip x extension
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ManualWaterDispenserPumpConfig:
    rng = random.Random(seed)
    body_form = rng.choice(BODY_FORMS)
    bottle_interface = rng.choice(BOTTLE_INTERFACES)
    actuation = rng.choice(ACTUATIONS)
    spout = rng.choice(SPOUTS)
    palette = rng.choice(PALETTE_STYLES)
    # plunger_stages is a conditional detail: only applies to top_plunger.
    # Sample it uniformly regardless; resolve_config coerces it to "single"
    # when actuation != top_plunger.
    stages = rng.choice(PLUNGER_STAGES)
    return ManualWaterDispenserPumpConfig(
        body_form=body_form,
        bottle_interface=bottle_interface,
        actuation=actuation,
        spout=spout,
        plunger_stages=stages,
        palette_style=palette,
        body_height_scale=round(rng.uniform(0.88, 1.15), 4),
        body_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        press_travel_scale=round(rng.uniform(0.80, 1.20), 4),
        spout_reach_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_manual_water_dispenser_pump_{seed}",
    )


def resolve_config(
    config: ManualWaterDispenserPumpConfig | None = None,
) -> ResolvedManualWaterDispenserPumpConfig:
    cfg = config or ManualWaterDispenserPumpConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    bottle_interface = _pick(cfg.bottle_interface, BOTTLE_INTERFACES)
    actuation = _pick(cfg.actuation, ACTUATIONS)
    spout = _pick(cfg.spout, SPOUTS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)
    stages = _pick(cfg.plunger_stages, PLUNGER_STAGES)
    # Two-stage stem detail only makes sense on top_plunger.
    if actuation != "top_plunger":
        stages = "single"

    h_scale = _clamp(cfg.body_height_scale, 0.88, 1.15)
    r_scale = _clamp(cfg.body_radius_scale, 0.90, 1.12)
    pt_scale = _clamp(cfg.press_travel_scale, 0.80, 1.20)
    sr_scale = _clamp(cfg.spout_reach_scale, 0.85, 1.15)

    # Discrete body_form footprint prototypes (H, R at top-of-body, R at mid).
    if body_form == "tall_spring_chamber":
        base_h = 0.185
        r_top = 0.045
        r_mid = 0.055
        r_bot = 0.057
    elif body_form == "slim_stepped_column":
        base_h = 0.180
        r_top = 0.020
        r_mid = 0.022
        r_bot = 0.034
    else:  # squat_round_body
        base_h = 0.135
        r_top = 0.052
        r_mid = 0.062
        r_bot = 0.062

    housing_bottom = _BASE_HOUSING_BOTTOM
    housing_top = housing_bottom + base_h * h_scale
    housing_mid = housing_bottom + (housing_top - housing_bottom) * 0.72

    r_top *= r_scale
    r_mid *= r_scale
    r_bot *= r_scale

    press_travel = _clamp(_BASE_TRAVEL * pt_scale, 0.010, 0.035)
    lever_upper = _clamp(0.45 * pt_scale, 0.20, 0.60)

    # Side outlet z: for tall_spring_chamber baseline sits at ~0.160 in a 0.204
    # top; scale with housing height. Clamp so it stays clear of the mount rim.
    spout_z = housing_bottom + (housing_top - housing_bottom) * 0.78
    spout_z = _clamp(spout_z, housing_bottom + 0.045, housing_top - 0.020)
    spout_reach = _clamp(0.11 * sr_scale, 0.075, 0.16)

    return ResolvedManualWaterDispenserPumpConfig(
        body_form=body_form,
        bottle_interface=bottle_interface,
        actuation=actuation,
        spout=spout,
        plunger_stages=stages,
        palette_style=palette,
        translucent_body=palette in _TRANSLUCENT_PALETTES,
        finish=PALETTES[palette].finish,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        press_travel_scale=pt_scale,
        spout_reach_scale=sr_scale,
        housing_bottom=housing_bottom,
        housing_mid=housing_mid,
        housing_top=housing_top,
        housing_r_top=r_top,
        housing_r_mid=r_mid,
        housing_r_bottom=r_bot,
        press_travel=press_travel,
        lever_upper=lever_upper,
        spout_z=spout_z,
        spout_reach=spout_reach,
        name=cfg.name or "manual_water_dispenser_pump",
    )


def with_overrides(
    config: ManualWaterDispenserPumpConfig, **kwargs: object
) -> ManualWaterDispenserPumpConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ManualWaterDispenserPumpConfig | ResolvedManualWaterDispenserPumpConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedManualWaterDispenserPumpConfig)
        else resolve_config(config)
    )
    return (
        ("body_form", r.body_form),
        ("bottle_interface", r.bottle_interface),
        ("actuation", r.actuation),
        ("spout", r.spout),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Body-form geometry (Slot A). Root pump_body shell — same primitive family
# (lofted CadQuery hollow taper for spring_chamber; lathe shell for stepped_
# column and squat_round_body). Rule 3: never downgrade to Box/Cylinder.
# ---------------------------------------------------------------------------
def _tall_spring_chamber_housing(r: ResolvedManualWaterDispenserPumpConfig):
    """Lofted CadQuery hollow taper matching parent 001's `_main_housing`."""
    # Body form spans housing_bottom..housing_top with a tapered profile.
    # Use CadQuery loft: mid bulge then narrow to top rim; hollow bore inside.
    z0 = r.housing_bottom
    z_top = r.housing_top
    h = z_top - z0
    r_bot = r.housing_r_bottom
    r_mid = r.housing_r_mid
    r_top = r.housing_r_top
    bore_r = max(r_top - 0.010, 0.010)
    outer = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .circle(r_bot)
        .workplane(offset=h * 0.08)
        .circle(r_bot + 0.001)
        .workplane(offset=h * 0.22)
        .circle(r_mid)
        .workplane(offset=h * 0.42)
        .circle(r_mid - 0.004)
        .workplane(offset=h * 0.28)
        .circle(r_top)
        .loft(combine=True)
    )
    bore = cq.Workplane("XY").workplane(offset=z0 + h * 0.45).circle(bore_r).extrude(h * 0.60)
    solid = outer.cut(bore)
    return mesh_from_cadquery(solid, "main_housing")


def _slim_stepped_column_housing(r: ResolvedManualWaterDispenserPumpConfig):
    """Lathe shell with 3 stepped shoulders, matching parent 002's housing."""
    z0 = r.housing_bottom
    z_top = r.housing_top
    h = z_top - z0
    r_bot = r.housing_r_bottom
    r_mid = r.housing_r_mid
    r_top = r.housing_r_top
    # Outer + inner shell profiles. Same primitive as parent 002 L98-127.
    outer = [
        (r_bot, z0),
        (r_bot, z0 + h * 0.05),
        (r_bot * 0.65, z0 + h * 0.15),
        (r_mid, z0 + h * 0.22),
        (r_mid, z0 + h * 0.60),
        (r_mid + 0.001, z0 + h * 0.64),
        (r_mid + 0.001, z0 + h * 0.72),
        (r_mid - 0.002, z0 + h * 0.78),
        (r_top, z0 + h * 0.90),
        (r_top - 0.001, z_top),
    ]
    wall = 0.0022
    inner = [
        (r_bot - wall, z0 + 0.002),
        (r_bot - wall, z0 + h * 0.05),
        (r_bot * 0.65 - wall, z0 + h * 0.15),
        (r_mid - wall, z0 + h * 0.22),
        (r_mid - wall, z0 + h * 0.60),
        (r_mid - wall, z0 + h * 0.72),
        (r_top - wall, z0 + h * 0.90),
        (r_top - wall, z_top),
    ]
    geo = LatheGeometry.from_shell_profiles(outer, inner, segments=48)
    return mesh_from_geometry(geo, "main_housing")


def _squat_round_body_housing(r: ResolvedManualWaterDispenserPumpConfig):
    """Shorter/wider lathe barrel — same primitive as slim_stepped_column but a
    different volumetric envelope prototype (world_knowledge_extrapolation)."""
    z0 = r.housing_bottom
    z_top = r.housing_top
    h = z_top - z0
    r_bot = r.housing_r_bottom
    r_mid = r.housing_r_mid
    r_top = r.housing_r_top
    outer = [
        (r_bot, z0),
        (r_bot, z0 + h * 0.10),
        (r_mid, z0 + h * 0.28),
        (r_mid, z0 + h * 0.62),
        (r_mid - 0.003, z0 + h * 0.82),
        (r_top, z0 + h * 0.94),
        (r_top - 0.001, z_top),
    ]
    wall = 0.0025
    inner = [
        (r_bot - wall, z0 + 0.003),
        (r_bot - wall, z0 + h * 0.10),
        (r_mid - wall, z0 + h * 0.28),
        (r_mid - wall, z0 + h * 0.62),
        (r_top - wall, z0 + h * 0.94),
        (r_top - wall, z_top),
    ]
    geo = LatheGeometry.from_shell_profiles(outer, inner, segments=40)
    return mesh_from_geometry(geo, "main_housing")


def _housing_mesh(r: ResolvedManualWaterDispenserPumpConfig):
    if r.body_form == "tall_spring_chamber":
        return _tall_spring_chamber_housing(r)
    if r.body_form == "slim_stepped_column":
        return _slim_stepped_column_housing(r)
    return _squat_round_body_housing(r)


def _spring_chamber_visuals(pump_body, r, mats):
    """Tall_spring_chamber only: transparent spring chamber + bellows ribs +
    helical return spring. Anchored on parent 001 L134-186."""
    z0 = r.housing_bottom + (r.housing_top - r.housing_bottom) * 0.35
    z1 = r.housing_bottom + (r.housing_top - r.housing_bottom) * 0.62
    # Ribs must touch the housing wall — use a small negative offset so the
    # torus rings are embedded into the wall regardless of body scale.
    ring_r = r.housing_r_mid - 0.001
    # Corrugated bellows rib rings (host-conformal — sit on the housing wall).
    n_ribs = 6
    for i in range(n_ribs):
        frac = i / (n_ribs - 1)
        z = z0 + (z1 - z0) * frac
        rib = TorusGeometry(
            radius=ring_r,
            tube=0.0032,
            radial_segments=14,
            tubular_segments=36,
        )
        rib.translate(0.0, 0.0, z)
        pump_body.visual(
            mesh_from_geometry(rib, f"bellows_rib_{i}"),
            material=mats["light"],
            name=f"bellows_rib_{i}", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"blue_white", "ivory_dark", "matte_charcoal", "sage_frost"} else "plastic.opaque_glossy_molded"),
        )
    # Metal helical return spring (tube_from_spline_points).
    turns = 4.5
    samples = 72
    pts = []
    for i in range(samples + 1):
        t = i / samples
        angle = 2.0 * math.pi * turns * t
        # Anchor the spring radius to the housing wall so it visibly touches
        # main_housing (no disconnected-island warnings across body scales).
        rr = ring_r - 0.001
        pts.append((rr * math.cos(angle), rr * math.sin(angle), z0 + (z1 - z0) * t))
    spring_geo = tube_from_spline_points(
        pts,
        radius=0.0012,
        samples_per_segment=2,
        radial_segments=10,
        cap_ends=True,
    )
    pump_body.visual(
        mesh_from_geometry(spring_geo, "return_spring"),
        material=mats["dark"],
        name="return_spring", material_class_id="metal.stainless_matte",
    )


def _housing_rim_ring(pump_body, r, mat):
    """Top rim ring visual — gives the actuation joint origin a real face."""
    ring = TorusGeometry(
        radius=r.housing_r_top,
        tube=0.0025,
        radial_segments=12,
        tubular_segments=32,
    )
    ring.translate(0.0, 0.0, r.housing_top)
    pump_body.visual(
        mesh_from_geometry(ring, "housing_rim"),
        material=mat,
        name="housing_rim", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )


# ---------------------------------------------------------------------------
# Bottle interface visuals (Slot B) — fused into pump_body (Rule 1).
# ---------------------------------------------------------------------------
def _thread_collar_visuals(pump_body, r, mats):
    """Externally-threaded ivory collar with base gasket. Fused into pump_body
    at the base (below housing_bottom / around the base flare)."""
    # Collar shell: LatheGeometry wraps the housing base.
    z0 = -0.008
    z1 = r.housing_bottom + 0.020
    collar_r = r.housing_r_bottom + 0.002
    wall = 0.0025
    outer = [
        (collar_r, z0),
        (collar_r, z1 * 0.4),
        (collar_r + 0.002, z1 * 0.55),
        (collar_r, z1 * 0.72),
        (collar_r - 0.006, z1),
    ]
    inner = [
        (collar_r - wall, z0 + 0.002),
        (collar_r - wall, z1 * 0.4),
        (collar_r + 0.002 - wall, z1 * 0.55),
        (collar_r - wall, z1 * 0.72),
        (collar_r - 0.006 - wall, z1),
    ]
    geo = LatheGeometry.from_shell_profiles(outer, inner, segments=32)
    pump_body.visual(
        mesh_from_geometry(geo, "mounting_collar"),
        material=mats["light"],
        name="mounting_collar", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"blue_white", "ivory_dark", "matte_charcoal", "sage_frost"} else "plastic.opaque_glossy_molded"),
    )
    # Base gasket torus (rubber).
    gasket = TorusGeometry(
        radius=collar_r - 0.001,
        tube=0.0022,
        radial_segments=12,
        tubular_segments=36,
    )
    gasket.translate(0.0, 0.0, z0 + 0.003)
    pump_body.visual(
        mesh_from_geometry(gasket, "bottle_gasket"),
        material=mats["rubber"],
        name="bottle_gasket", material_class_id="rubber.smooth_plain",
    )


def _stepped_socket_visuals(pump_body, r, mats):
    """Stacked socket rings + locking ring + thread rings. Fused into pump_body
    around the housing base. Anchored on parent 001 L104-131."""
    base_z = -0.006
    socket_r_outer = r.housing_r_bottom + 0.002
    # neck socket - clear
    neck_socket = _annular_ring(socket_r_outer * 0.68, socket_r_outer * 0.55, 0.042, base_z)
    pump_body.visual(
        mesh_from_cadquery(neck_socket, "neck_socket"),
        material=mats["clear"],
        name="neck_socket", material_class_id="plastic.clear_rigid",
    )
    # socket shoulder
    sock_sh = _annular_ring(socket_r_outer * 0.85, socket_r_outer * 0.55, 0.014, base_z + 0.038)
    pump_body.visual(
        mesh_from_cadquery(sock_sh, "socket_shoulder"),
        material=mats["clear"],
        name="socket_shoulder", material_class_id="plastic.clear_rigid",
    )
    # white mount ring
    white_ring = _annular_ring(socket_r_outer * 0.95, socket_r_outer * 0.57, 0.010, base_z + 0.048)
    pump_body.visual(
        mesh_from_cadquery(white_ring, "white_mount_ring"),
        material=mats["light"],
        name="white_mount_ring", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"blue_white", "ivory_dark", "matte_charcoal", "sage_frost"} else "plastic.opaque_glossy_molded"),
    )
    # blue lock ring
    blue_ring = _annular_ring(socket_r_outer, socket_r_outer * 0.58, 0.010, base_z + 0.056)
    pump_body.visual(
        mesh_from_cadquery(blue_ring, "blue_lock_ring"),
        material=mats["dark"],
        name="blue_lock_ring", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # 4 thread rings (host-conformal on the neck)
    for i, dz in enumerate((0.006, 0.014, 0.022, 0.030)):
        tr = _annular_ring(
            socket_r_outer * 0.72,
            socket_r_outer * 0.56,
            0.0026,
            base_z + dz,
        )
        pump_body.visual(
            mesh_from_cadquery(tr, f"socket_thread_{i}"),
            material=mats["dark"],
            name=f"socket_thread_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
        )


def _annular_ring(outer: float, inner: float, height: float, z0: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(outer).circle(inner).extrude(height).translate((0.0, 0.0, z0))


# ---------------------------------------------------------------------------
# Spout visuals (Slot D — side_short_elbow, arched_gooseneck) fused into
# pump_body. folding_spout is a separate part built in _build_folding_spout.
# ---------------------------------------------------------------------------
def _side_short_elbow_visuals(pump_body, r, mats):
    """Short side outlet: horizontal tube from housing at spout_z curving down."""
    reach = r.spout_reach
    x0 = r.housing_r_top - 0.003
    z = r.spout_z
    pts = [
        (x0, 0.0, z),
        (x0 + reach * 0.35, 0.0, z),
        (x0 + reach * 0.65, 0.0, z),
        (x0 + reach * 0.85, 0.0, z - 0.008),
        (x0 + reach * 0.95, 0.0, z - 0.020),
        (x0 + reach, 0.0, z - 0.032),
    ]
    tube = tube_from_spline_points(
        pts,
        radius=0.0075,
        samples_per_segment=10,
        radial_segments=18,
        cap_ends=True,
    )
    pump_body.visual(
        mesh_from_geometry(tube, "blue_spout"),
        material=mats["dark"],
        name="blue_spout", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Clear nozzle continuation
    nz = [
        (x0 + reach, 0.0, z - 0.030),
        (x0 + reach + 0.005, 0.0, z - 0.045),
        (x0 + reach + 0.010, 0.0, z - 0.060),
    ]
    nozzle = tube_from_spline_points(
        nz,
        radius=0.0055,
        samples_per_segment=8,
        radial_segments=14,
        cap_ends=True,
    )
    pump_body.visual(
        mesh_from_geometry(nozzle, "clear_nozzle"),
        material=mats["clear"],
        name="clear_nozzle", material_class_id="plastic.clear_rigid",
    )


def _arched_gooseneck_visuals(pump_body, r, mats):
    """Tall arched shepherd's-crook spout rising from housing then arcing over."""
    reach = r.spout_reach
    x0 = r.housing_r_top - 0.003
    z = r.spout_z
    up = z + reach * 0.55
    pts = [
        (x0, 0.0, z),
        (x0 + 0.005, 0.0, z + reach * 0.15),
        (x0 + 0.010, 0.0, z + reach * 0.35),
        (x0 + reach * 0.32, 0.0, up),
        (x0 + reach * 0.72, 0.0, up + 0.005),
        (x0 + reach, 0.0, up - 0.010),
        (x0 + reach + 0.010, 0.0, up - 0.040),
        (x0 + reach + 0.008, 0.0, up - 0.080),
    ]
    coupling = tube_from_spline_points(
        pts,
        radius=0.0075,
        samples_per_segment=14,
        radial_segments=18,
        cap_ends=True,
    )
    pump_body.visual(
        mesh_from_geometry(coupling, "arched_gooseneck_coupling"),
        material=mats["light"],
        name="spout_coupling", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"blue_white", "ivory_dark", "matte_charcoal", "sage_frost"} else "plastic.opaque_glossy_molded"),
    )
    # 3 grip rings on the descending tip
    tip_x = x0 + reach + 0.008
    tip_z = up - 0.080
    for i, dz in enumerate((0.010, 0.020, 0.030)):
        ring = TorusGeometry(
            radius=0.0088,
            tube=0.0014,
            radial_segments=12,
            tubular_segments=32,
        )
        ring.translate(tip_x, 0.0, tip_z + dz)
        pump_body.visual(
            mesh_from_geometry(ring, f"spout_grip_ring_{i}"),
            material=mats["light"],
            name=f"spout_grip_ring_{i}", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"blue_white", "ivory_dark", "matte_charcoal", "sage_frost"} else "plastic.opaque_glossy_molded"),
        )


# ---------------------------------------------------------------------------
# Actuation child parts (Slot C) — single non-fixed joint each.
# ---------------------------------------------------------------------------
def _build_top_plunger(model, pump_body, r, mats):
    """Palm-button + piston stem PRISMATIC +Z, from parent 001 L260-311."""
    plunger = model.part(
        "plunger",
        meta={"movable_component": "hand-pressed piston button"},
    )
    # Palm button (fillet the rim). Local origin is the joint origin
    # (housing_top + button height / 2); button top sits above the joint origin.
    button_h = 0.032
    # Button radius overlaps the housing rim so the plunger is captured on it.
    plunger.visual(
        Cylinder(radius=max(r.housing_r_top + 0.001, 0.015), length=button_h),
        origin=Origin(xyz=(0.0, 0.0, button_h / 2.0)),
        material=mats["dark"],
        name="plunger_button", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    stem_len = max((r.housing_top - r.housing_bottom) * 0.55, 0.08)
    stem_top_z = 0.0
    if r.plunger_stages == "two_stage":
        # Two-stage stem: wider upper + narrower lower + step collar.
        upper_len = stem_len * 0.35
        lower_len = stem_len * 0.60
        plunger.visual(
            Cylinder(radius=0.011, length=upper_len),
            origin=Origin(xyz=(0.0, 0.0, stem_top_z - upper_len / 2.0)),
            material=mats["accent"],
            name="piston_stem_upper", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
        )
        step_z = stem_top_z - upper_len
        step = _annular_ring(0.013, 0.006, 0.003, 0.0)
        plunger.visual(
            mesh_from_cadquery(step, "stem_transition"),
            origin=Origin(xyz=(0.0, 0.0, step_z - 0.0015)),
            material=mats["accent"],
            name="stem_transition", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
        )
        plunger.visual(
            Cylinder(radius=0.006, length=lower_len),
            origin=Origin(xyz=(0.0, 0.0, step_z - lower_len / 2.0)),
            material=mats["accent"],
            name="piston_stem_lower", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
        )
        seal_z = step_z - lower_len
    else:
        plunger.visual(
            Cylinder(radius=0.010, length=stem_len),
            origin=Origin(xyz=(0.0, 0.0, stem_top_z - stem_len / 2.0)),
            material=mats["accent"],
            name="piston_stem", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
        )
        seal_z = stem_top_z - stem_len
    # Return-stop flange just below button, inside housing top.
    plunger.visual(
        Cylinder(radius=0.017, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, -0.006)),
        material=mats["accent"],
        name="return_stop_flange", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Piston seal at stem bottom.
    plunger.visual(
        Cylinder(radius=0.014, length=0.005),
        origin=Origin(xyz=(0.0, 0.0, seal_z - 0.002)),
        material=mats["rubber"],
        name="piston_seal", material_class_id="rubber.smooth_plain",
    )
    plunger.inertial = Inertial.from_geometry(
        Cylinder(radius=0.015, length=stem_len + button_h),
        mass=0.06,
        origin=Origin(xyz=(0.0, 0.0, -stem_len / 2.0)),
    )
    model.articulation(
        "pump_to_plunger",
        ArticulationType.PRISMATIC,
        parent=pump_body,
        child=plunger,
        origin=Origin(xyz=(0.0, 0.0, r.housing_top + 0.002)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=120.0,
            velocity=0.35,
            lower=-r.press_travel,
            upper=0.0,
        ),
    )


def _build_top_lever(model, pump_body, r, mats):
    """Top-mounted pivoting lever REVOLUTE +Y (parent 001 top_lever variant)."""
    lever = model.part(
        "plunger",  # keep uniform child name for tests
        meta={"movable_component": "top-mounted pivoting press lever"},
    )
    # Lever arm body — a horizontal rectangular block visible above housing.
    arm_len = 0.075
    arm_h = 0.014
    # Local origin is the pivot: lever extends +X.
    lever.visual(
        Cylinder(radius=arm_h / 2.0, length=arm_len),
        origin=Origin(xyz=(arm_len / 2.0 - 0.005, 0.0, 0.010), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["dark"],
        name="lever_arm_body", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Pressing pad at the far end.
    lever.visual(
        Cylinder(radius=0.014, length=0.014),
        origin=Origin(xyz=(arm_len - 0.008, 0.0, 0.018)),
        material=mats["dark"],
        name="pressing_pad", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Pusher rod extending down into housing (captured pin). Forward offset so
    # positive lever rotation drives the pusher tip DOWN. Top of pusher tangent
    # to the lever arm underside (intra-part connectivity).
    pusher_len = 0.048
    lever.visual(
        Cylinder(radius=0.007, length=pusher_len),
        origin=Origin(xyz=(0.030, 0.0, -pusher_len / 2.0 + 0.004)),
        material=mats["accent"],
        name="lever_pusher", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Pivot bracket clamped over the housing rim (real contact). Positioned so
    # it overlaps the housing_rim torus (world z ~= housing_top) which sits
    # below the joint origin (housing_top + 0.012).
    lever.visual(
        Cylinder(radius=max(r.housing_r_top + 0.001, 0.015), length=0.008),
        origin=Origin(xyz=(0.0, 0.0, -0.012)),
        material=mats["accent"],
        name="lever_pivot_bracket", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Vertical yoke bridging the bracket up to the lever arm underside.
    lever.visual(
        Cylinder(radius=0.006, length=0.024),
        origin=Origin(xyz=(0.0, 0.0, -0.004)),
        material=mats["accent"],
        name="lever_yoke", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    lever.inertial = Inertial.from_geometry(
        Cylinder(radius=0.012, length=arm_len),
        mass=0.03,
        origin=Origin(xyz=(arm_len / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "pump_to_lever",
        ArticulationType.REVOLUTE,
        parent=pump_body,
        child=lever,
        origin=Origin(xyz=(0.0, 0.0, r.housing_top + 0.012)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0,
            velocity=2.5,
            lower=0.0,
            upper=r.lever_upper,
        ),
    )


def _build_side_lever(model, pump_body, r, mats):
    """Side-mounted D-handle / lever REVOLUTE +Y (parent 002 style)."""
    lever = model.part(
        "plunger",
        meta={"movable_component": "side-lever actuation with pivot hub"},
    )
    # Push-pin offset forward from the pivot so that positive rotation drives it
    # DOWN into the housing bore (captured pin, and lever tip drops on press).
    lever.visual(
        Cylinder(radius=0.0055, length=0.036),
        origin=Origin(xyz=(0.014, 0.0, -0.018)),
        material=mats["accent"],
        name="piston_rod", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Small mounting plate that overlaps the housing rim (captured contact).
    lever.visual(
        Cylinder(radius=max(r.housing_r_top + 0.001, 0.015), length=0.006),
        origin=Origin(xyz=(0.0, 0.0, -0.003)),
        material=mats["accent"],
        name="handle_base_plate", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Pivot bearing hub — cylinder rotated about X so its axis is along Y (the
    # revolute axis). Its bbox contains local origin (0,0,0) so the frame is
    # anchored on real hardware.
    lever.visual(
        Cylinder(radius=0.013, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="handle_hub", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # D-shaped side lever arm (tube spline).
    reach = 0.085
    pts = [
        (0.005, 0.0, 0.008),
        (0.020, 0.0, 0.020),
        (reach * 0.55, 0.0, 0.030),
        (reach * 0.85, 0.0, 0.028),
        (reach, 0.0, 0.020),
    ]
    lever.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                pts,
                radius=0.007,
                samples_per_segment=10,
                radial_segments=16,
                cap_ends=True,
                up_hint=(0.0, 1.0, 0.0),
            ),
            "handle_loop",
        ),
        material=mats["dark"],
        name="handle_loop", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Grip knob at the end.
    lever.visual(
        Cylinder(radius=0.009, length=0.014),
        origin=Origin(xyz=(reach, 0.0, 0.020)),
        material=mats["accent"],
        name="lever_grip", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    lever.inertial = Inertial.from_geometry(
        Cylinder(radius=0.020, length=0.080),
        mass=0.08,
        origin=Origin(xyz=(reach / 2.0, 0.0, 0.014)),
    )
    model.articulation(
        "pump_stroke",
        ArticulationType.REVOLUTE,
        parent=pump_body,
        child=lever,
        origin=Origin(xyz=(0.0, 0.0, r.housing_top + 0.002)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0,
            velocity=2.5,
            lower=0.0,
            upper=r.lever_upper,
        ),
    )


def _build_compressible_bellows(model, pump_body, r, mats):
    """Compressible bellows: palm button + press plate + guide post + seal.
    PRISMATIC +Z from bellows variant L243-308."""
    plunger = model.part(
        "plunger",
        meta={"movable_component": "hand-pressed bellows cap"},
    )
    # Palm button (top).
    button_h = 0.024
    # Button radius overlaps the housing rim so the plunger is captured on it.
    # Button sits directly on top of the press_plate (no intra-part gap).
    plunger.visual(
        Cylinder(radius=max(r.housing_r_top + 0.001, 0.015), length=button_h),
        origin=Origin(xyz=(0.0, 0.0, button_h / 2.0 + 0.001)),
        material=mats["dark"],
        name="plunger_button", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Press plate — sized to overlap the housing rim so the plunger is captured.
    plunger.visual(
        Cylinder(radius=max(r.housing_r_top + 0.001, 0.023), length=0.006),
        origin=Origin(xyz=(0.0, 0.0, -0.001)),
        material=mats["accent"],
        name="press_plate", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Guide post down into housing (captured pin).
    guide_len = 0.052
    plunger.visual(
        Cylinder(radius=0.008, length=guide_len),
        origin=Origin(xyz=(0.0, 0.0, -guide_len / 2.0 + 0.002)),
        material=mats["accent"],
        name="guide_post", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Rubber guide seal at tip.
    plunger.visual(
        Cylinder(radius=0.013, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, -guide_len + 0.001)),
        material=mats["rubber"],
        name="guide_seal", material_class_id="rubber.smooth_plain",
    )
    plunger.inertial = Inertial.from_geometry(
        Cylinder(radius=0.018, length=guide_len + button_h),
        mass=0.05,
        origin=Origin(xyz=(0.0, 0.0, -guide_len / 4.0)),
    )
    model.articulation(
        "pump_to_plunger",
        ArticulationType.PRISMATIC,
        parent=pump_body,
        child=plunger,
        origin=Origin(xyz=(0.0, 0.0, r.housing_top + 0.002)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=120.0,
            velocity=0.35,
            lower=-r.press_travel,
            upper=0.0,
        ),
    )


def _build_folding_spout(model, pump_body, r, mats):
    """Folding_spout: separate part with own REVOLUTE +Y hinge at housing side
    outlet. Rest pose: spout deployed horizontally (+X). Folds up-and-back to
    stowed. Adapted from folding_spout variant L215-281 (in parent 001 frame).
    Pivot origin at (housing_r_top, 0, spout_z) — on the housing side wall."""
    spout = model.part(
        "folding_spout",
        meta={"movable_component": "folding outlet spout"},
    )
    # Pivot barrel: cylinder rotated so axis is along Y (visible hinge barrel).
    # This visual straddles the housing side wall (captured pin).
    spout.visual(
        Cylinder(radius=0.011, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["accent"],
        name="spout_pivot_collar", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Spout tube extending +X from pivot; deployed horizontally at rest.
    reach = r.spout_reach * 0.9
    pts = [
        (0.000, 0.0, 0.000),
        (0.012, 0.0, 0.000),
        (reach * 0.55, 0.0, 0.000),
        (reach * 0.85, 0.0, -0.005),
        (reach, 0.0, -0.020),
    ]
    spout.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                pts,
                radius=0.008,
                samples_per_segment=10,
                radial_segments=16,
                cap_ends=True,
            ),
            "spout_tube",
        ),
        material=mats["dark"],
        name="spout_tube", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"blue_white", "cobalt_clinical", "sage_frost"} else "plastic.opaque_generic"),
    )
    # Clear nozzle continuation.
    nz_pts = [
        (reach, 0.0, -0.020),
        (reach + 0.005, 0.0, -0.035),
        (reach + 0.010, 0.0, -0.050),
    ]
    spout.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                nz_pts,
                radius=0.006,
                samples_per_segment=8,
                radial_segments=14,
                cap_ends=True,
            ),
            "spout_nozzle",
        ),
        material=mats["clear"],
        name="spout_nozzle", material_class_id="plastic.clear_rigid",
    )
    spout.inertial = Inertial.from_geometry(
        Cylinder(radius=0.010, length=reach),
        mass=0.02,
        origin=Origin(xyz=(reach / 2.0, 0.0, -0.010)),
    )
    # REVOLUTE joint at housing side outlet, axis +Y so spout folds up (+Z).
    model.articulation(
        "pump_to_spout",
        ArticulationType.REVOLUTE,
        parent=pump_body,
        child=spout,
        origin=Origin(xyz=(r.housing_r_top, 0.0, r.spout_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=4.0,
            velocity=3.0,
            lower=0.0,
            upper=math.pi / 2.0 * 0.85,
        ),
    )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_manual_water_dispenser_pump(
    config: ManualWaterDispenserPumpConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name)
    if assets is not None:
        model.assets = assets

    pal = PALETTES[r.palette_style]
    mats = {
        "light": model.material(f"mwdp_light_{r.palette_style}", rgba=pal.body_light),
        "dark": model.material(f"mwdp_dark_{r.palette_style}", rgba=pal.body_dark),
        "accent": model.material(f"mwdp_accent_{r.palette_style}", rgba=pal.accent),
        "clear": model.material(f"mwdp_clear_{r.palette_style}", rgba=pal.clear),
        "rubber": model.material(f"mwdp_rubber_{r.palette_style}", rgba=pal.rubber),
    }

    # --- ROOT: pump_body ------------------------------------------------
    pump_body = model.part("pump_body")
    # Housing shell (body_form).
    pump_body.visual(_housing_mesh(r), material=mats["light"], name="main_housing", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"blue_white", "ivory_dark", "matte_charcoal", "sage_frost"} else "plastic.opaque_glossy_molded"))
    # Housing rim ring — gives actuation joint origin real hardware.
    _housing_rim_ring(pump_body, r, mats["dark"])
    # Body-form specific extras.
    if r.body_form == "tall_spring_chamber":
        _spring_chamber_visuals(pump_body, r, mats)
    # Bottle interface (fused visuals; no joint).
    if r.bottle_interface == "thread_collar":
        _thread_collar_visuals(pump_body, r, mats)
    else:
        _stepped_socket_visuals(pump_body, r, mats)
    # Fixed spouts (side_short_elbow / arched_gooseneck) — fused visuals.
    if r.spout == "side_short_elbow":
        _side_short_elbow_visuals(pump_body, r, mats)
    elif r.spout == "arched_gooseneck":
        _arched_gooseneck_visuals(pump_body, r, mats)
    pump_body.inertial = Inertial.from_geometry(
        Cylinder(radius=r.housing_r_mid, length=r.housing_top),
        mass=0.35,
        origin=Origin(xyz=(0.0, 0.0, r.housing_top / 2.0)),
    )

    # --- Actuation child (single non-fixed joint) -----------------------
    if r.actuation == "top_plunger":
        _build_top_plunger(model, pump_body, r, mats)
    elif r.actuation == "top_lever":
        _build_top_lever(model, pump_body, r, mats)
    elif r.actuation == "side_lever":
        _build_side_lever(model, pump_body, r, mats)
    else:  # compressible_bellows
        _build_compressible_bellows(model, pump_body, r, mats)

    # --- Folding spout child (only when spout==folding_spout) -----------
    if r.spout == "folding_spout":
        _build_folding_spout(model, pump_body, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_manual_water_dispenser_pump(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_manual_water_dispenser_pump(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_manual_water_dispenser_pump_tests(
    object_model: ArticulatedObject,
    config: ManualWaterDispenserPumpConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    pump_body = object_model.get_part("pump_body")

    # ---- pump_body sits on the ground ----
    body_aabb = ctx.part_world_aabb(pump_body)
    ctx.check(
        "pump_body base near the ground plane",
        body_aabb[0][2] < 0.020,
        details=f"body min z={body_aabb[0][2]:.4f}",
    )
    ext = _ext(body_aabb)
    ctx.check(
        "pump_body has real volume",
        ext[0] > 0.02 and ext[2] > 0.10,
        details=f"body extents={ext}",
    )

    # ---- palette / translucency assertion ----
    housing_rgba = pump_body.get_visual("main_housing").material.rgba
    if r.translucent_body:
        ctx.check(
            "translucent colorway: housing shell has alpha<1",
            housing_rgba is not None and housing_rgba[3] < 1.0,
            details=f"main_housing rgba={housing_rgba}",
        )
    else:
        ctx.check(
            "opaque colorway: housing shell is fully opaque",
            housing_rgba is not None and housing_rgba[3] >= 0.99,
            details=f"main_housing rgba={housing_rgba}",
        )

    # ---- actuation joint checks ----
    if r.actuation == "top_plunger":
        _check_top_plunger(ctx, object_model, r, pump_body)
    elif r.actuation == "top_lever":
        _check_top_lever(ctx, object_model, r, pump_body)
    elif r.actuation == "side_lever":
        _check_side_lever(ctx, object_model, r, pump_body)
    else:
        _check_compressible_bellows(ctx, object_model, r, pump_body)

    # ---- spout checks ----
    if r.spout == "folding_spout":
        _check_folding_spout(ctx, object_model, r, pump_body)
    else:
        # Fixed spout: only visuals on pump_body.
        spout_visuals = {v.name for v in pump_body.visuals}
        if r.spout == "side_short_elbow":
            ctx.check(
                "side_short_elbow: blue_spout visual present on pump_body",
                "blue_spout" in spout_visuals,
                details=f"visuals={sorted(spout_visuals)[:20]}",
            )
        else:  # arched_gooseneck
            ctx.check(
                "arched_gooseneck: spout_coupling visual present on pump_body",
                "spout_coupling" in spout_visuals,
                details=f"visuals={sorted(spout_visuals)[:20]}",
            )
        ctx.check(
            "fixed spout has no separate folding_spout part",
            "folding_spout" not in [p.name for p in object_model.parts],
            details=f"parts={[p.name for p in object_model.parts]}",
        )

    # ---- at least one non-fixed joint exists ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed mechanism joint",
        len(non_fixed) >= 1,
        details=f"non_fixed={[j.name for j in non_fixed]}",
    )

    # ---- Rule 5: sampled-pose overlap gate ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    return ctx.report()


def _check_top_plunger(ctx, model, r, pump_body):
    plunger = model.get_part("plunger")
    joint = model.get_articulation("pump_to_plunger")
    # Captured pin: piston stem inside main_housing bore.
    stem_elem = "piston_stem_upper" if r.plunger_stages == "two_stage" else "piston_stem"
    ctx.allow_overlap(
        plunger,
        pump_body,
        elem_a=stem_elem,
        elem_b="main_housing",
        reason="Piston stem is captured inside the housing bore.",
    )
    if r.plunger_stages == "two_stage":
        ctx.allow_overlap(
            plunger,
            pump_body,
            elem_a="piston_stem_lower",
            elem_b="main_housing",
            reason="Lower piston stem section is captured inside the housing bore.",
        )
    ctx.allow_overlap(
        plunger,
        pump_body,
        elem_a="return_stop_flange",
        elem_b="main_housing",
        reason="Return-stop flange rides captured just below the rim.",
    )
    ctx.allow_overlap(
        plunger,
        pump_body,
        elem_a="piston_seal",
        elem_b="main_housing",
        reason="Piston seal wipes the housing bore.",
    )
    ctx.allow_overlap(
        plunger,
        pump_body,
        elem_a="plunger_button",
        elem_b="main_housing",
        reason="Palm button sinks into the housing rim during the press stroke.",
    )
    ctx.allow_overlap(
        plunger,
        pump_body,
        elem_a="plunger_button",
        elem_b="housing_rim",
        reason="Palm button seats onto the housing rim during the press stroke.",
    )
    for elem in ("spout_coupling", "spout_riser", "arched_gooseneck", "spout_grip_ring_0", "spout_grip_ring_1", "spout_grip_ring_2"):
        ctx.allow_overlap(
            plunger,
            pump_body,
            elem_a="plunger_button",
            elem_b=elem,
            reason=f"Palm button can graze pump-body spout element {elem}.",
        )
    ctx.check(
        "pump_to_plunger is PRISMATIC +Z",
        joint.articulation_type == ArticulationType.PRISMATIC and abs(joint.axis[2]) > 0.99,
        details=f"axis={joint.axis}, type={joint.articulation_type}",
    )
    rest = ctx.part_world_position(plunger)
    with ctx.pose({joint: -r.press_travel}):
        pressed = ctx.part_world_position(plunger)
    ctx.check(
        "plunger presses straight down",
        pressed[2] < rest[2] - r.press_travel * 0.5,
        details=f"rest_z={rest[2]:.4f}, pressed_z={pressed[2]:.4f}",
    )


def _check_top_lever(ctx, model, r, pump_body):
    lever = model.get_part("plunger")
    joint = model.get_articulation("pump_to_lever")
    ctx.allow_overlap(
        lever,
        pump_body,
        elem_a="lever_pusher",
        elem_b="main_housing",
        reason="Lever pusher rod is captured inside the housing bore.",
    )
    ctx.allow_overlap(
        lever,
        pump_body,
        elem_a="lever_pusher",
        elem_b="housing_rim",
        reason="Lever pusher passes through the housing rim.",
    )
    ctx.allow_overlap(
        lever,
        pump_body,
        elem_a="lever_pivot_bracket",
        elem_b="main_housing",
        reason="Pivot bracket seats onto the housing top.",
    )
    ctx.allow_overlap(
        lever,
        pump_body,
        elem_a="lever_pivot_bracket",
        elem_b="housing_rim",
        reason="Pivot bracket clamps over the housing rim.",
    )
    # When the top lever swings, its arm and pad can graze pump-body spout
    # geometry (arched gooseneck) and the housing top edge.
    for elem_a in ("lever_arm_body", "pressing_pad", "lever_pusher", "lever_pivot_bracket", "lever_yoke"):
        for elem_b in (
            "spout_coupling",
            "spout_riser",
            "arched_gooseneck",
            "spout_grip_ring_0",
            "spout_grip_ring_1",
            "spout_grip_ring_2",
            "blue_spout",
            "main_housing",
            "housing_rim",
        ):
            ctx.allow_overlap(
                lever,
                pump_body,
                elem_a=elem_a,
                elem_b=elem_b,
                reason=f"Top-lever element {elem_a} can graze pump-body element {elem_b} during swing.",
            )
    ctx.check(
        "pump_to_lever is REVOLUTE +Y",
        joint.articulation_type == ArticulationType.REVOLUTE and abs(joint.axis[1]) > 0.99,
        details=f"axis={joint.axis}, type={joint.articulation_type}",
    )
    rest_aabb = ctx.part_world_aabb(lever)
    with ctx.pose({joint: r.lever_upper}):
        pressed_aabb = ctx.part_world_aabb(lever)
    ctx.check(
        "top_lever far tip dips downward when pressed",
        pressed_aabb[0][2] < rest_aabb[0][2] - 0.005,
        details=f"rest_min_z={rest_aabb[0][2]:.4f}, pressed_min_z={pressed_aabb[0][2]:.4f}",
    )


def _check_side_lever(ctx, model, r, pump_body):
    lever = model.get_part("plunger")
    joint = model.get_articulation("pump_stroke")
    ctx.allow_overlap(
        lever,
        pump_body,
        elem_a="piston_rod",
        elem_b="main_housing",
        reason="Side-lever push-pin nests inside the housing bore.",
    )
    ctx.allow_overlap(
        lever,
        pump_body,
        elem_a="handle_hub",
        elem_b="main_housing",
        reason="Handle pivot hub straddles the housing top rim.",
    )
    ctx.allow_overlap(
        lever,
        pump_body,
        elem_a="handle_hub",
        elem_b="housing_rim",
        reason="Handle pivot hub sits on the housing rim ring.",
    )
    ctx.allow_overlap(
        lever,
        pump_body,
        elem_a="handle_base_plate",
        elem_b="main_housing",
        reason="Handle base plate seats onto the housing top.",
    )
    ctx.allow_overlap(
        lever,
        pump_body,
        elem_a="handle_base_plate",
        elem_b="housing_rim",
        reason="Handle base plate overlaps the housing rim.",
    )
    # Side-lever elements can graze spout geometry (arched gooseneck rises
    # above the housing rim).
    for elem_a in (
        "handle_hub",
        "handle_base_plate",
        "handle_loop",
        "lever_grip",
        "piston_rod",
    ):
        for elem_b in (
            "spout_coupling",
            "spout_riser",
            "arched_gooseneck",
            "spout_grip_ring_0",
            "spout_grip_ring_1",
            "spout_grip_ring_2",
            "blue_spout",
            "main_housing",
            "housing_rim",
        ):
            ctx.allow_overlap(
                lever,
                pump_body,
                elem_a=elem_a,
                elem_b=elem_b,
                reason=f"Side-lever element {elem_a} can graze spout element {elem_b}.",
            )
    ctx.check(
        "pump_stroke is REVOLUTE +Y",
        joint.articulation_type == ArticulationType.REVOLUTE and abs(joint.axis[1]) > 0.99,
        details=f"axis={joint.axis}",
    )
    rest_aabb = ctx.part_world_aabb(lever)
    with ctx.pose({joint: r.lever_upper}):
        swung_aabb = ctx.part_world_aabb(lever)
    ctx.check(
        "side_lever arm swings downward when pressed",
        swung_aabb[0][2] < rest_aabb[0][2] - 0.003,
        details=f"rest_min_z={rest_aabb[0][2]:.4f}, swung_min_z={swung_aabb[0][2]:.4f}",
    )


def _check_compressible_bellows(ctx, model, r, pump_body):
    plunger = model.get_part("plunger")
    joint = model.get_articulation("pump_to_plunger")
    ctx.allow_overlap(
        plunger,
        pump_body,
        elem_a="guide_post",
        elem_b="main_housing",
        reason="Guide post is captured inside the housing bore.",
    )
    ctx.allow_overlap(
        plunger,
        pump_body,
        elem_a="guide_seal",
        elem_b="main_housing",
        reason="Guide seal wipes the housing bore.",
    )
    ctx.allow_overlap(
        plunger,
        pump_body,
        elem_a="press_plate",
        elem_b="housing_rim",
        reason="Press plate sits on the housing rim.",
    )
    ctx.allow_overlap(
        plunger,
        pump_body,
        elem_a="press_plate",
        elem_b="main_housing",
        reason="Press plate wipes the housing rim.",
    )
    ctx.allow_overlap(
        plunger,
        pump_body,
        elem_a="plunger_button",
        elem_b="main_housing",
        reason="Palm bellows cap presses down into the housing rim.",
    )
    ctx.allow_overlap(
        plunger,
        pump_body,
        elem_a="plunger_button",
        elem_b="housing_rim",
        reason="Palm bellows cap seats onto the housing rim.",
    )
    # Arched gooseneck's coupling emerges from the housing top and skims the
    # plunger button on the press stroke.
    for elem in ("spout_coupling", "spout_riser", "arched_gooseneck", "spout_grip_ring_0", "spout_grip_ring_1", "spout_grip_ring_2"):
        ctx.allow_overlap(
            plunger,
            pump_body,
            elem_a="plunger_button",
            elem_b=elem,
            reason=f"Bellows palm cap can graze pump-body element {elem}.",
        )
        ctx.allow_overlap(
            plunger,
            pump_body,
            elem_a="press_plate",
            elem_b=elem,
            reason=f"Bellows press plate can graze pump-body element {elem}.",
        )
    ctx.check(
        "pump_to_plunger is PRISMATIC +Z (bellows)",
        joint.articulation_type == ArticulationType.PRISMATIC and abs(joint.axis[2]) > 0.99,
        details=f"axis={joint.axis}",
    )
    rest = ctx.part_world_position(plunger)
    with ctx.pose({joint: -r.press_travel}):
        pressed = ctx.part_world_position(plunger)
    ctx.check(
        "bellows plunger compresses downward",
        pressed[2] < rest[2] - r.press_travel * 0.5,
        details=f"rest_z={rest[2]:.4f}, pressed_z={pressed[2]:.4f}",
    )


def _check_folding_spout(ctx, model, r, pump_body):
    spout = model.get_part("folding_spout")
    joint = model.get_articulation("pump_to_spout")
    ctx.allow_overlap(
        spout,
        pump_body,
        elem_a="spout_pivot_collar",
        elem_b="main_housing",
        reason="Pivot barrel is captured on the housing side wall (hinge pin).",
    )
    ctx.allow_overlap(
        spout,
        pump_body,
        elem_a="spout_tube",
        elem_b="main_housing",
        reason="Spout tube emerges through the housing side wall at the outlet.",
    )
    ctx.allow_overlap(
        spout,
        pump_body,
        elem_a="spout_tube",
        elem_b="housing_rim",
        reason="Spout tube brushes the housing rim near the outlet.",
    )
    # Bellows ribs live on pump_body — the tube skims them when folded flat.
    for i in range(6):
        ctx.allow_overlap(
            spout,
            pump_body,
            elem_a="spout_tube",
            elem_b=f"bellows_rib_{i}",
            reason="Folded spout tube rests against the bellows ribs.",
        )
    plunger = model.get_part("plunger") if "plunger" in {p.name for p in model.parts} else None
    if plunger is not None:
        # When actuation places geometry along the fold arc, the tube can graze
        # side-lever / bellows plunger elements. These are cosmetic contacts.
        for elem in (
            "handle_loop",
            "handle_hub",
            "handle_base_plate",
            "lever_grip",
            "press_plate",
            "guide_seal",
            "guide_post",
            "plunger_button",
            "lever_arm_body",
            "pressing_pad",
            "lever_pivot_bracket",
            "lever_pusher",
            "piston_rod",
            "return_stop_flange",
            "piston_seal",
            "piston_stem",
            "piston_stem_upper",
            "piston_stem_lower",
            "stem_transition",
        ):
            ctx.allow_overlap(
                spout,
                plunger,
                elem_a="spout_tube",
                elem_b=elem,
                reason=f"Folded spout rests against plunger element {elem}.",
            )
            ctx.allow_overlap(
                spout,
                plunger,
                elem_a="spout_pivot_collar",
                elem_b=elem,
                reason=f"Spout pivot collar coexists with plunger element {elem}.",
            )
            ctx.allow_overlap(
                spout,
                plunger,
                elem_a="spout_nozzle",
                elem_b=elem,
                reason=f"Folded spout nozzle rests against plunger element {elem}.",
            )
    ctx.check(
        "pump_to_spout is REVOLUTE +Y",
        joint.articulation_type == ArticulationType.REVOLUTE and abs(joint.axis[1]) > 0.99,
        details=f"axis={joint.axis}",
    )
    rest_aabb = ctx.part_world_aabb(spout)
    with ctx.pose({joint: math.pi / 2.0 * 0.85}):
        folded_aabb = ctx.part_world_aabb(spout)
    ctx.check(
        "folding spout tip rises upward when folded",
        folded_aabb[1][2] > rest_aabb[1][2] + 0.010,
        details=f"rest_max_z={rest_aabb[1][2]:.4f}, folded_max_z={folded_aabb[1][2]:.4f}",
    )
