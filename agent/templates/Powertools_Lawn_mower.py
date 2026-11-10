# SPDX-License-Identifier: Apache-2.0

"""Lawn mower — modular procedural template.

Walk-behind push lawn mower. The always-on identity is:

  * a hollow revolved ``deck`` shell (LatheGeometry) as the root,
  * a CONTINUOUS vertical ``blade`` spin under the deck center,
  * >=1 CONTINUOUS wheel-spin joint about the lateral (Y) axis, and
  * a REVOLUTE handle fold kept on **every** seed.

Topology is *mixed*: ``deck`` is the root and three structural slots plus one
multiplicity axis hang off it (star graph, not a serial chain — so we build
the deck directly and dispatch each slot's module factory onto it rather than
running the ``_modular`` chain assembler):

  deck (root)
    +- [Slot A power-unit] gas_engine / corded_electric / battery_brushless
    |     -> power housing FIXED to deck + ``blade`` CONTINUOUS (vertical Z)
    +- [multiplicity] {pos}_wheel_{i}  (WHEEL_SPECS loop, each CONTINUOUS)
    |     N in {3, 4}: N=3 = single centered front caster + 2 rear wheels
    +- [Slot B grass-collection] side_discharge (REVOLUTE deflector)
    |     / rear_bag (REVOLUTE door + folded bag visuals) / mulch_plug (visuals)
    +- [Slot C handle] u_handle_fold (REVOLUTE) / loop_bullhorn (REVOLUTE)
          / telescoping_2seg (REVOLUTE fold + PRISMATIC slide)

Adopted 5-star sources (see spec Module Source Index):
  S1 parent (adebd312)  gas_engine + u_handle_fold + deck/blade/wheel skeleton
  S2 var_electric       corded_electric motor cover + power cord
  S3 var_battery        battery_brushless compact motor (battery folded to deck)
  S4 var_sidechute      side_discharge curved deflector panel (REVOLUTE)
  S5 var_rearbag        rear_bag spring door (REVOLUTE) + tubular bag frame
  S6 var_mulchplug      mulch_plug curved insert + cover panel (deck visuals)
  S7 var_telehandle     telescoping_2seg lower_handle + upper_grip (PRISMATIC)
  S8 var_loophandle     loop_bullhorn D-loop grip
  S9 var_3wheel         wheel_count N=3 centered front caster + 2 rear
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from math import atan2, cos, pi, sin, sqrt
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    LatheGeometry,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireGeometry,
    TireGroove,
    TireSidewall,
    TireTread,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
    tube_from_spline_points,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


# --------------------------------------------------------------------------- #
# Shared layout constants (verbatim from the parent skeleton)
# --------------------------------------------------------------------------- #

DECK_TOP_Z = 0.228  # top plane of the spindle boss / engine seating plane
HANDLE_PIVOT = (-0.28, 0.0, 0.17)
HANDLE_FOLD_LOWER = -2.27  # ~-130 deg: handle lies nearly flat over the deck

# Side-discharge chute (right / -Y side of the deck).
CHUTE_HINGE = (0.0, -0.235, 0.105)
CHUTE_OPEN_UPPER = 1.2  # ~69 deg: deflector swings outward and upward

# Telescoping handle: junction + prismatic slide (var_telehandle).
HANDLE_JUNCTION = (-0.40, 0.0, 0.355)
HANDLE_SLIDE_AXIS = (-0.745, 0.0, 0.667)
HANDLE_SLIDE_UPPER = 0.12  # 12 cm of height adjustment travel

# (part name, x, side(+1 left / -1 right / 0 centered caster),
#  wheel center z = tire radius, tire width, rim radius, rim width)
WHEEL_SPECS_4 = [
    ("front_wheel_0", 0.19, 1.0, 0.100, 0.045, 0.076, 0.040),
    ("front_wheel_1", 0.19, -1.0, 0.100, 0.045, 0.076, 0.040),
    ("rear_wheel_0", -0.19, 1.0, 0.125, 0.050, 0.094, 0.044),
    ("rear_wheel_1", -0.19, -1.0, 0.125, 0.050, 0.094, 0.044),
]
WHEEL_SPECS_3 = [
    # Front caster pushed forward to x=0.345 so its tire (r~0.080) clears the
    # widest scaled deck shell (radius 0.230*1.12=0.258) with margin; the fork
    # arm bridges the gap back to the shell.
    ("front_caster", 0.345, 0.0, 0.085, 0.038, 0.065, 0.034),
    ("rear_wheel_0", -0.19, 1.0, 0.125, 0.050, 0.094, 0.044),
    ("rear_wheel_1", -0.19, -1.0, 0.125, 0.050, 0.094, 0.044),
]


def _wheel_specs(wheel_count: int) -> list[tuple[str, float, float, float, float, float, float]]:
    """Single source of truth for the wheel multiplicity (N in {3, 4})."""
    return WHEEL_SPECS_3 if wheel_count == 3 else WHEEL_SPECS_4


# --------------------------------------------------------------------------- #
# Module enums
# --------------------------------------------------------------------------- #

PowerUnitModule = Literal["gas_engine", "corded_electric", "battery_brushless"]
GrassCollectionModule = Literal["side_discharge", "rear_bag", "mulch_plug"]
HandleModule = Literal["u_handle_fold", "telescoping_2seg", "loop_bullhorn"]
PaletteStyle = Literal["orange", "red", "green", "black"]

_POWER_CHOICES: tuple[PowerUnitModule, ...] = (
    "gas_engine",
    "corded_electric",
    "battery_brushless",
)
_COLLECTION_CHOICES: tuple[GrassCollectionModule, ...] = (
    "side_discharge",
    "rear_bag",
    "mulch_plug",
)
_HANDLE_CHOICES: tuple[HandleModule, ...] = (
    "u_handle_fold",
    "telescoping_2seg",
    "loop_bullhorn",
)
_PALETTE_CHOICES: tuple[PaletteStyle, ...] = ("orange", "red", "green", "black")
_WHEEL_COUNT_CHOICES: tuple[int, ...] = (3, 4)


# --------------------------------------------------------------------------- #
# Palette presets — REQUIRED per-seed palette diversity (>=3 materials).
# Every preset supplies the full named-material set so every `.visual(...)`
# can pass `material=`. Brands: orange (gas), red, green, black/graphite.
# --------------------------------------------------------------------------- #

Rgba = tuple[float, float, float, float]


def _palette(deck: Rgba, accent: Rgba) -> dict[str, Rgba]:
    return {
        "deck_body": deck,
        "accent": accent,
        "engine_black": (0.09, 0.09, 0.10, 1.0),
        "panel_dark": (0.04, 0.04, 0.05, 1.0),
        "steel_gray": (0.62, 0.63, 0.66, 1.0),
        "blade_steel": (0.55, 0.56, 0.58, 1.0),
        "hub_gray": (0.55, 0.56, 0.58, 1.0),
        "tire_rubber": (0.07, 0.07, 0.08, 1.0),
        "handle_black": (0.10, 0.10, 0.11, 1.0),
        "cable_black": (0.04, 0.04, 0.04, 1.0),
        "grip_foam": (0.13, 0.13, 0.14, 1.0),
        "motor_gray": (0.30, 0.31, 0.33, 1.0),
        "cord_orange": (0.95, 0.45, 0.05, 1.0),
        "battery_accent": (0.95, 0.78, 0.10, 1.0),
        "bag_fabric": (0.16, 0.18, 0.20, 1.0),
    }


PALETTE_PRESETS: dict[PaletteStyle, dict[str, Rgba]] = {
    "orange": _palette((0.72, 0.21, 0.08, 1.0), (0.74, 0.14, 0.09, 1.0)),
    "red": _palette((0.66, 0.09, 0.08, 1.0), (0.85, 0.72, 0.10, 1.0)),
    "green": _palette((0.13, 0.36, 0.16, 1.0), (0.93, 0.78, 0.06, 1.0)),
    "black": _palette((0.10, 0.11, 0.12, 1.0), (0.78, 0.36, 0.04, 1.0)),
}

# Identity name map: factories pass the registered material NAME to each
# `.visual(material=...)`; the per-seed rgba is bound once in build_lawn_mower
# via `model.material(name, rgba=...)`, so referencing by name resolves the
# right color for the sampled palette_style.
_MAT = {name: name for name in _palette((0, 0, 0, 1), (0, 0, 0, 1))}


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class LawnMowerConfig:
    power_unit: PowerUnitModule = "gas_engine"
    grass_collection: GrassCollectionModule = "side_discharge"
    handle: HandleModule = "u_handle_fold"
    palette_style: PaletteStyle = "orange"
    wheel_count: int = 4
    deck_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedLawnMowerConfig:
    power_unit: PowerUnitModule
    grass_collection: GrassCollectionModule
    handle: HandleModule
    palette_style: PaletteStyle
    wheel_count: int
    deck_scale: float
    palette: dict[str, Rgba] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Procedural sampling
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> LawnMowerConfig:
    """Deterministic per-seed slot draw.

    ``seed == 0`` is not special: it is sampled like any other seed. All four
    structural axes (power-unit / grass-collection / handle / wheel_count) and
    the palette / deck scale are drawn from the same ``random.Random(seed)``.
    """
    rng = random.Random(seed)
    power_unit = rng.choice(_POWER_CHOICES)
    grass_collection = rng.choice(_COLLECTION_CHOICES)
    handle = rng.choice(_HANDLE_CHOICES)
    palette_style = rng.choice(_PALETTE_CHOICES)
    wheel_count = rng.choice(_WHEEL_COUNT_CHOICES)
    deck_scale = round(rng.uniform(0.9, 1.12), 4)
    return LawnMowerConfig(
        power_unit=power_unit,
        grass_collection=grass_collection,
        handle=handle,
        palette_style=palette_style,
        wheel_count=wheel_count,
        deck_scale=deck_scale,
    )


def resolve_config(config: LawnMowerConfig) -> ResolvedLawnMowerConfig:
    """Validate enums, clamp the continuous scale, and bind the palette."""
    power_unit = config.power_unit or "gas_engine"
    grass_collection = config.grass_collection or "side_discharge"
    handle = config.handle or "u_handle_fold"
    palette_style = config.palette_style or "orange"

    if power_unit not in _POWER_CHOICES:
        raise ValueError(f"Unsupported power_unit: {power_unit}")
    if grass_collection not in _COLLECTION_CHOICES:
        raise ValueError(f"Unsupported grass_collection: {grass_collection}")
    if handle not in _HANDLE_CHOICES:
        raise ValueError(f"Unsupported handle: {handle}")
    if palette_style not in PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_style: {palette_style}")

    wheel_count = int(config.wheel_count)
    if wheel_count not in _WHEEL_COUNT_CHOICES:
        raise ValueError(f"Unsupported wheel_count (must be 3 or 4): {wheel_count}")

    deck_scale = max(0.9, min(float(config.deck_scale), 1.12))

    return ResolvedLawnMowerConfig(
        power_unit=power_unit,
        grass_collection=grass_collection,
        handle=handle,
        palette_style=palette_style,
        wheel_count=wheel_count,
        deck_scale=deck_scale,
        palette=dict(PALETTE_PRESETS[palette_style]),
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Return (slot, module) picks for the module_topology_diversity gate.

    Includes ``wheel_count`` so multiplicity contributes to topology diversity:
    3 power x 3 collection x 3 handle x 2 wheel_count = 54 distinct tuples.
    """
    r = resolve_config(config_from_seed(seed))
    return [
        ("power_unit", r.power_unit),
        ("grass_collection", r.grass_collection),
        ("handle", r.handle),
        ("wheel_count", f"n{r.wheel_count}"),
    ]


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def _mirror_y(
    points: list[tuple[float, float, float]], side: float
) -> list[tuple[float, float, float]]:
    return [(x, side * y, z) for x, y, z in points]


def _build_curved_panel(
    width: float,
    height: float,
    outward: float,
    thickness: float,
    n: int = 8,
) -> MeshGeometry:
    """Curved thin deflector panel (verbatim from var_sidechute).

    Local frame: origin at top-center. Panel extends in -Z and curves toward
    -Y with a quadratic profile (y = -k*s^2, z = -s).
    """
    mesh = MeshGeometry()
    hw = width / 2.0
    k = outward / (height * height) if height > 0 else 0.0

    curve: list[tuple[float, float, float, float]] = []
    for i in range(n + 1):
        s = (i / n) * height
        yc = -k * s * s
        zc = -s
        ny_raw, nz_raw = -1.0, 2.0 * k * s
        norm = sqrt(ny_raw * ny_raw + nz_raw * nz_raw)
        curve.append((yc, zc, ny_raw / norm, nz_raw / norm))

    m = n + 1
    for x in (-hw, hw):
        for yc, zc, ny, nz in curve:
            mesh.add_vertex(x, yc + 0.5 * thickness * ny, zc + 0.5 * thickness * nz)
            mesh.add_vertex(x, yc - 0.5 * thickness * ny, zc - 0.5 * thickness * nz)

    base_right = 2 * m
    for i in range(n):
        lo0, li0 = i * 2, i * 2 + 1
        lo1, li1 = (i + 1) * 2, (i + 1) * 2 + 1
        ro0, ri0 = base_right + i * 2, base_right + i * 2 + 1
        ro1, ri1 = base_right + (i + 1) * 2, base_right + (i + 1) * 2 + 1
        mesh.add_face(lo0, ro0, lo1)
        mesh.add_face(lo1, ro0, ro1)
        mesh.add_face(li0, li1, ri0)
        mesh.add_face(li1, ri1, ri0)
        mesh.add_face(lo0, lo1, li0)
        mesh.add_face(li0, lo1, li1)
        mesh.add_face(ro0, ri0, ro1)
        mesh.add_face(ri0, ri1, ro1)

    lo0, li0 = 0, 1
    ro0, ri0 = base_right, base_right + 1
    mesh.add_face(lo0, li0, ro0)
    mesh.add_face(li0, ri0, ro0)
    loN, liN = 2 * n, 2 * n + 1
    roN, riN = base_right + 2 * n, base_right + 2 * n + 1
    mesh.add_face(loN, roN, liN)
    mesh.add_face(liN, roN, riN)
    return mesh


def _curved_shell_arc(
    r_inner: float,
    r_outer: float,
    arc_start_deg: float,
    arc_end_deg: float,
    height: float,
    *,
    segments: int = 12,
) -> MeshGeometry:
    """Annular-sector solid following the deck shell at the rear (mulch plug).

    Built as a parametric MeshGeometry arc (same curved-shell fidelity as the
    var_mulchplug cadquery sector, without the cadquery dependency). Vertices:
    for each angle sample an inner+outer pair at z=0 and at z=height.
    """
    a1 = arc_start_deg * pi / 180.0
    a2 = arc_end_deg * pi / 180.0
    mesh = MeshGeometry()

    # vertex index layout per angle sample i: [out_bot, out_top, in_bot, in_top]
    def _idx(i: int, ring: int) -> int:
        return i * 4 + ring

    for i in range(segments + 1):
        t = i / segments
        a = a1 + (a2 - a1) * t
        ox, oy = r_outer * cos(a), r_outer * sin(a)
        ix, iy = r_inner * cos(a), r_inner * sin(a)
        mesh.add_vertex(ox, oy, 0.0)
        mesh.add_vertex(ox, oy, height)
        mesh.add_vertex(ix, iy, 0.0)
        mesh.add_vertex(ix, iy, height)

    for i in range(segments):
        ob0, ot0, ib0, it0 = (_idx(i, k) for k in range(4))
        ob1, ot1, ib1, it1 = (_idx(i + 1, k) for k in range(4))
        # outer wall
        mesh.add_face(ob0, ob1, ot0)
        mesh.add_face(ot0, ob1, ot1)
        # inner wall
        mesh.add_face(ib0, it0, ib1)
        mesh.add_face(it0, it1, ib1)
        # top
        mesh.add_face(ot0, ot1, it0)
        mesh.add_face(it0, ot1, it1)
        # bottom
        mesh.add_face(ob0, ib0, ob1)
        mesh.add_face(ob1, ib0, ib1)

    # end caps (start and end angle)
    ob, ot, ib, it = (_idx(0, k) for k in range(4))
    mesh.add_face(ob, ot, ib)
    mesh.add_face(ib, ot, it)
    ob, ot, ib, it = (_idx(segments, k) for k in range(4))
    mesh.add_face(ob, ib, ot)
    mesh.add_face(ot, ib, it)
    return mesh


# --------------------------------------------------------------------------- #
# Deck (root) + shared brackets
# --------------------------------------------------------------------------- #


def _build_deck(model: ArticulatedObject, r: ResolvedLawnMowerConfig):
    """Hollow revolved deck shell + spindle boss + apron + wheel/handle mounts.

    Adapted verbatim from the parent (LatheGeometry shell). ``deck_scale``
    scales only the shell radial profile uniformly in plan; the seating plane
    and mount z stay fixed so all downstream interfaces remain coincident.
    """
    p = _MAT
    s = r.deck_scale
    deck = model.part("deck")

    outer = [
        (0.230, 0.042),
        (0.230, 0.120),
        (0.222, 0.150),
        (0.205, 0.176),
        (0.178, 0.197),
        (0.140, 0.212),
        (0.095, 0.220),
        (0.055, 0.2235),
    ]
    inner = [
        (0.224, 0.042),
        (0.224, 0.117),
        (0.216, 0.146),
        (0.199, 0.171),
        (0.172, 0.191),
        (0.135, 0.206),
        (0.092, 0.2135),
        (0.055, 0.217),
    ]
    shell = LatheGeometry.from_shell_profiles(
        [(rad * s, z) for rad, z in outer],
        [(rad * s, z) for rad, z in inner],
        segments=80,
    )
    deck.visual(mesh_from_geometry(shell, "deck_shell"), material=p["deck_body"], name="shell", material_class_id="metal.paint_coated")

    boss = LatheGeometry.from_shell_profiles(
        [(0.115, 0.205), (0.115, DECK_TOP_Z)],
        [(0.025, 0.205), (0.025, DECK_TOP_Z)],
        segments=64,
    )
    deck.visual(
        mesh_from_geometry(boss, "deck_spindle_boss"),
        material=p["deck_body"],
        name="spindle_boss", material_class_id="metal.paint_coated",
    )

    # Spindle bearing collar at the boss top: a real bearing ring with a center
    # bore the crankshaft passes through. Its inner wall sits ~12mm from the
    # spindle axis, so the FIXED ``power_mount`` joint origin at (0,0,DECK_TOP_Z)
    # lands within tolerance of solid deck hardware (was 25mm into the open bore).
    bearing_cap = LatheGeometry.from_shell_profiles(
        [(0.034, DECK_TOP_Z - 0.012), (0.034, DECK_TOP_Z + 0.004)],
        [(0.012, DECK_TOP_Z - 0.012), (0.012, DECK_TOP_Z + 0.004)],
        segments=48,
    )
    deck.visual(
        mesh_from_geometry(bearing_cap, "deck_spindle_bearing"),
        material=p["steel_gray"],
        name="spindle_bearing", material_class_id="metal.steel_bare",
    )

    # Rear apron: front face extended forward to x=-0.20 so it always overlaps
    # the deck shell rear (radius as low as 0.207 at min scale 0.9), keeping the
    # whole rear cluster (handle brackets, pivot rod, bag frame) one support
    # island with the shell.
    deck.visual(
        Box((0.105, 0.30, 0.085)),
        origin=Origin(xyz=(-0.2525, 0.0, 0.0875)),
        material=p["deck_body"],
        name="rear_apron", material_class_id="metal.paint_coated",
    )

    # Wheel mounts: centered front caster fork (N=3) + corner axle brackets.
    for name, wx, side, wz, _tw, _wr, _ww in _wheel_specs(r.wheel_count):
        if side == 0.0:
            # Caster support: a high bracket arm cantilevers forward from the
            # deck shell front (x as low as 0.207 at min scale) to x=0.255, which
            # stays clear of the tire back (~0.261). Its front face overlaps the
            # shell -> one support island. Two side fork plates (y=+-0.033 clears
            # the 0.019 tire half-width) straddle the wheel and bridge the arm
            # down to the axle, so the bracket never intrudes into the tire.
            arm_back = 0.18
            arm_front = 0.255
            arm_len = arm_front - arm_back
            deck.visual(
                Box((arm_len, 0.076, 0.028)),
                origin=Origin(xyz=(arm_back + 0.5 * arm_len, 0.0, 0.168)),
                material=p["panel_dark"],
                name=f"{name}_bracket", material_class_id="metal.paint_coated",
            )
            for fork_i, fork_side in enumerate((1.0, -1.0)):
                deck.visual(
                    Box((0.112, 0.006, 0.100)),
                    origin=Origin(xyz=(0.306, fork_side * 0.033, 0.126)),
                    material=p["panel_dark"],
                    name=f"{name}_fork_{fork_i}", material_class_id="metal.paint_coated",
                )
            deck.visual(
                Cylinder(radius=0.008, length=0.072),
                origin=Origin(xyz=(wx, 0.0, wz), rpy=(pi / 2.0, 0.0, 0.0)),
                material=p["steel_gray"],
                name=f"{name}_axle", material_class_id="metal.steel_bare",
            )
        else:
            # Lateral mount tracks the scaled shell edge so the wheel stays
            # outboard of the (radius 0.230*s) shell at every scale. The bracket
            # bridges from inside the shell (y=0.165) out to the scaled edge, and
            # the axle reaches the wheel center (kept in sync via _lateral_wheel_y).
            wheel_y = _lateral_wheel_y(side, s, _tw)
            # Inner face reaches y=0.05 so the bracket always overlaps the
            # circular shell at the wheel's x (shell reaches y~0.082 at x=0.19,
            # min scale) -> one support island. Outer face stops just inboard of
            # the hub/tire; the axle crosses into the hub bore.
            bracket_in = 0.05
            bracket_out = abs(wheel_y) - 0.5 * _ww - 0.024
            deck.visual(
                Box((0.05, bracket_out - bracket_in, 0.10)),
                origin=Origin(xyz=(wx, side * 0.5 * (bracket_in + bracket_out), wz)),
                material=p["panel_dark"],
                name=f"{name}_bracket", material_class_id="metal.paint_coated",
            )
            deck.visual(
                Cylinder(radius=0.0105, length=(abs(wheel_y) - bracket_out) + 0.02),
                origin=Origin(xyz=(wx, side * 0.5 * (bracket_out + abs(wheel_y)), wz), rpy=(pi / 2.0, 0.0, 0.0)),
                material=p["steel_gray"],
                name=f"{name}_axle", material_class_id="metal.steel_bare",
            )

    # Handlebar pivot brackets + bolt bosses.
    for i, side in enumerate((1.0, -1.0)):
        deck.visual(
            Box((0.05, 0.014, 0.11)),
            origin=Origin(xyz=(-0.285, side * 0.135, 0.155)),
            material=p["panel_dark"],
            name=f"handle_bracket_{i}", material_class_id="metal.paint_coated",
        )
        deck.visual(
            Cylinder(radius=0.014, length=0.055),
            origin=Origin(
                xyz=(HANDLE_PIVOT[0], side * 0.1475, HANDLE_PIVOT[2]),
                rpy=(pi / 2.0, 0.0, 0.0),
            ),
            material=p["steel_gray"],
            name=f"handle_bolt_boss_{i}", material_class_id="metal.steel_bare",
        )
    # Continuous hinge pivot rod spanning the two bolt bosses at HANDLE_PIVOT.
    # It carries the lateral fold axle and places real deck hardware on the
    # ``handlebar_fold`` joint origin (centerline y=0), where previously the
    # nearest deck geometry was ~40mm away between the two side bosses.
    deck.visual(
        Cylinder(radius=0.011, length=0.30),
        origin=Origin(
            xyz=(HANDLE_PIVOT[0], 0.0, HANDLE_PIVOT[2]),
            rpy=(pi / 2.0, 0.0, 0.0),
        ),
        material=p["steel_gray"],
        name="handle_pivot_rod", material_class_id="metal.steel_bare",
    )
    return deck


# --------------------------------------------------------------------------- #
# Shared blade (always-on CONTINUOUS vertical spin)
# --------------------------------------------------------------------------- #


def _build_blade(model: ArticulatedObject, r: ResolvedLawnMowerConfig, *, power_part):
    """Vertical blade hanging from the crankshaft; CONTINUOUS about Z.

    Parent is the power housing (engine / motor). The crankshaft is captured
    inside the power housing proxy (declared overlap).
    """
    p = _MAT
    blade = model.part("blade")
    blade.visual(
        Box((0.38, 0.05, 0.006)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=p["blade_steel"],
        name="blade_bar", material_class_id="metal.steel_bare",
    )
    blade.visual(
        Cylinder(radius=0.030, length=0.02),
        origin=Origin(xyz=(0.0, 0.0, 0.012)),
        material=p["panel_dark"],
        name="blade_hub", material_class_id="metal.paint_coated",
    )
    blade.visual(
        Cylinder(radius=0.012, length=0.175),
        origin=Origin(xyz=(0.0, 0.0, 0.095)),
        material=p["steel_gray"],
        name="crankshaft", material_class_id="metal.steel_bare",
    )
    # Drive spindle on the power unit: the output shaft drops from the motor
    # body down through the deck bore into the cutting chamber and ends at the
    # blade-spin bearing. Adding it to the power part places real parent
    # hardware on the blade_spin joint origin (z=-0.153 in power frame), which
    # otherwise sat 153mm below the motor body. r=0.011 < boss bore r=0.025
    # keeps the clearance fit; the blade crankshaft (r=0.012) nests just inside.
    power_part.visual(
        Cylinder(radius=0.011, length=0.170),
        origin=Origin(xyz=(0.0, 0.0, -0.068)),
        material=p["steel_gray"],
        name="drive_spindle", material_class_id="metal.steel_bare",
    )
    power_part.visual(
        Cylinder(radius=0.020, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, -0.153)),
        material=p["panel_dark"],
        name="blade_bearing", material_class_id="metal.paint_coated",
    )
    model.articulation(
        "blade_spin",
        ArticulationType.CONTINUOUS,
        parent=power_part,
        child=blade,
        origin=Origin(xyz=(0.0, 0.0, -0.153)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=25.0, velocity=320.0),
        mating=MatingContract(
            parent_face_geometry="blade_bearing",
            parent_face_side="negative_z",
            child_face_geometry="blade_hub",
            child_face_side="positive_z",
            contact_tol=0.05,
        ),
    )
    return blade


# --------------------------------------------------------------------------- #
# Slot A: power-unit factories
# --------------------------------------------------------------------------- #


def _build_power_gas_engine(model: ArticulatedObject, r: ResolvedLawnMowerConfig, deck):
    """Single-cylinder gas engine + recoil + fuel tank (parent verbatim)."""
    p = _MAT
    engine = model.part("engine")
    engine.visual(
        Box((0.26, 0.24, 0.18)),
        origin=Origin(xyz=(0.0, 0.0, 0.09)),
        material=p["engine_black"],
        name="power_housing", material_class_id="metal.paint_coated",
    )
    for i, side in enumerate((1.0, -1.0)):
        engine.visual(
            Box((0.18, 0.014, 0.10)),
            origin=Origin(xyz=(0.0, side * 0.117, 0.085)),
            material=p["panel_dark"],
            name=f"recessed_panel_{i}", material_class_id="metal.paint_coated",
        )
    engine.visual(
        Box((0.22, 0.20, 0.04)),
        origin=Origin(xyz=(0.0, 0.0, 0.20)),
        material=p["engine_black"],
        name="top_shroud", material_class_id="metal.paint_coated",
    )
    engine.visual(
        Cylinder(radius=0.082, length=0.034),
        origin=Origin(xyz=(-0.01, 0.0, 0.235)),
        material=p["panel_dark"],
        name="recoil_cover", material_class_id="plastic.opaque_glossy_molded",
    )
    engine.visual(
        Cylinder(radius=0.028, length=0.012),
        origin=Origin(xyz=(-0.01, 0.0, 0.254)),
        material=p["engine_black"],
        name="recoil_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    engine.visual(
        Box((0.05, 0.025, 0.02)),
        origin=Origin(xyz=(0.06, 0.045, 0.243)),
        material=p["engine_black"],
        name="starter_handle", material_class_id="plastic.opaque_glossy_molded",
    )
    engine.visual(
        Cylinder(radius=0.026, length=0.02),
        origin=Origin(xyz=(0.09, -0.072, 0.226)),
        material=p["panel_dark"],
        name="fuel_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    engine.visual(
        Cylinder(radius=0.015, length=0.016),
        origin=Origin(xyz=(0.05, 0.124, 0.05), rpy=(pi / 2.0, 0.0, 0.0)),
        material=p["accent"],
        name="primer_bulb", material_class_id="rubber.smooth_plain",
    )
    engine.visual(
        Box((0.06, 0.05, 0.07)),
        origin=Origin(xyz=(-0.12, 0.105, 0.135)),
        material=p["panel_dark"],
        name="air_filter_box", material_class_id="plastic.opaque_glossy_molded",
    )
    engine.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    (-0.09, 0.105, 0.092),
                    (-0.16, 0.120, 0.030),
                    (-0.23, 0.133, -0.005),
                    (-0.285, 0.140, -0.003),
                ],
                radius=0.0035,
                samples_per_segment=10,
                radial_segments=10,
            ),
            "engine_throttle_cable",
        ),
        material=p["cable_black"],
        name="throttle_cable", material_class_id="tech.cable_pipe_bundle",
    )
    model.articulation(
        "power_mount",
        ArticulationType.FIXED,
        parent=deck,
        child=engine,
        origin=Origin(xyz=(0.0, 0.0, DECK_TOP_Z)),
        mating=MatingContract(
            parent_face_geometry="spindle_boss",
            parent_face_side="positive_z",
            child_face_geometry="power_housing",
            child_face_side="negative_z",
            contact_tol=0.002,
        ),
    )
    return engine


def _build_power_corded_electric(model: ArticulatedObject, r: ResolvedLawnMowerConfig, deck):
    """Low-profile electric motor dome cover + trailing cord (var_electric)."""
    p = _MAT
    # Deck cord guide routing the power cord toward the handle.
    deck.visual(
        Box((0.022, 0.024, 0.026)),
        origin=Origin(xyz=(-0.265, -0.10, 0.143)),
        material=p["panel_dark"],
        name="cord_guide", material_class_id="plastic.opaque_glossy_molded",
    )

    motor = model.part("motor")
    motor_cover = LatheGeometry.from_shell_profiles(
        [
            (0.098, 0.000),
            (0.098, 0.010),
            (0.092, 0.013),
            (0.092, 0.035),
            (0.088, 0.065),
            (0.078, 0.090),
            (0.060, 0.108),
            (0.036, 0.118),
            (0.010, 0.123),
        ],
        [
            (0.088, 0.000),
            (0.088, 0.010),
            (0.086, 0.013),
            (0.086, 0.033),
            (0.082, 0.062),
            (0.072, 0.086),
            (0.055, 0.103),
            (0.031, 0.112),
            (0.007, 0.116),
        ],
        segments=64,
    )
    motor.visual(
        mesh_from_geometry(motor_cover, "motor_cover"),
        material=p["engine_black"],
        name="power_housing", material_class_id="plastic.opaque_glossy_molded",
    )
    for i in range(4):
        angle = pi / 4.0 + i * (pi / 2.0)
        motor.visual(
            Box((0.006, 0.002, 0.055)),
            origin=Origin(xyz=(0.088 * sin(angle), 0.088 * cos(angle), 0.060), rpy=(0.0, 0.0, -angle)),
            material=p["panel_dark"],
            name=f"vent_slot_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    motor.visual(
        Cylinder(radius=0.088, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
        material=p["motor_gray"],
        name="shaft_bearing", material_class_id="metal.aluminum_bare",
    )
    motor.visual(
        Cylinder(radius=0.012, length=0.016),
        origin=Origin(xyz=(-0.088, 0.0, 0.025), rpy=(0.0, pi / 2.0, 0.0)),
        material=p["motor_gray"],
        name="cord_grommet", material_class_id="rubber.smooth_plain",
    )
    motor.visual(
        Box((0.050, 0.030, 0.004)),
        origin=Origin(xyz=(0.0, 0.0, 0.121)),
        material=p["motor_gray"],
        name="label_plate", material_class_id="metal.aluminum_bare",
    )
    # Short power-cord pigtail: from the grommet it loops rearward to the
    # operator's left, staying ABOVE the deck top plane (motor-local z >= 0.005,
    # i.e. world z >= ~0.233) the whole way, and ends in the clear gap between
    # the centered rear grass bag (y within +-0.11) and the rear-left wheel
    # (centered y = -0.25). This avoids the shell, apron, bag, and wheels.
    motor.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    (-0.088, 0.0, 0.025),
                    (-0.13, -0.06, 0.040),
                    (-0.17, -0.11, 0.045),
                    # Keep the tail at |y|<=0.135: the folded handle side
                    # tubes (|y|>=0.165) sweep through the old (-0.20,-0.15)
                    # / (-0.21,-0.17) tail region around fold ~-1.9 rad.
                    (-0.20, -0.13, 0.035),
                    (-0.235, -0.135, 0.018),
                ],
                radius=0.006,
                samples_per_segment=10,
                radial_segments=10,
            ),
            "motor_power_cord",
        ),
        material=p["cord_orange"],
        name="power_cord", material_class_id="tech.cable_pipe_bundle",
    )
    model.articulation(
        "power_mount",
        ArticulationType.FIXED,
        parent=deck,
        child=motor,
        origin=Origin(xyz=(0.0, 0.0, DECK_TOP_Z)),
        mating=MatingContract(
            parent_face_geometry="spindle_boss",
            parent_face_side="positive_z",
            child_face_geometry="power_housing",
            child_face_side="negative_z",
            contact_tol=0.002,
        ),
    )
    return motor


def _build_power_battery_brushless(model: ArticulatedObject, r: ResolvedLawnMowerConfig, deck):
    """Compact brushless motor hub + removable battery pack (var_battery).

    The battery pack does not articulate, so per Rule 1 ("if it doesn't move,
    it isn't a part") it is fused into the deck visuals (cradle rails + pack)
    rather than attached as a FIXED part.
    """
    p = _MAT
    motor = model.part("motor")
    motor.visual(
        Cylinder(radius=0.058, length=0.068),
        origin=Origin(xyz=(0.0, 0.0, 0.034)),
        material=p["engine_black"],
        name="power_housing", material_class_id="plastic.opaque_glossy_molded",
    )
    motor.visual(
        Cylinder(radius=0.050, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, 0.073)),
        material=p["motor_gray"],
        name="motor_cap", material_class_id="metal.aluminum_bare",
    )
    for i in range(4):
        angle = pi / 4.0 + i * (pi / 2.0)
        motor.visual(
            Box((0.065, 0.005, 0.032)),
            origin=Origin(xyz=(0.052 * sin(angle), 0.052 * cos(angle), 0.034), rpy=(0.0, 0.0, -angle)),
            material=p["panel_dark"],
            name=f"motor_vent_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    motor.visual(
        Box((0.030, 0.040, 0.028)),
        origin=Origin(xyz=(-0.066, 0.0, 0.030)),
        material=p["panel_dark"],
        name="motor_controller", material_class_id="plastic.opaque_glossy_molded",
    )
    motor.visual(
        Cylinder(radius=0.088, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
        material=p["motor_gray"],
        name="shaft_bearing", material_class_id="metal.aluminum_bare",
    )
    model.articulation(
        "power_mount",
        ArticulationType.FIXED,
        parent=deck,
        child=motor,
        origin=Origin(xyz=(0.0, 0.0, DECK_TOP_Z)),
        mating=MatingContract(
            parent_face_geometry="spindle_boss",
            parent_face_side="positive_z",
            child_face_geometry="power_housing",
            child_face_side="negative_z",
            contact_tol=0.002,
        ),
    )

    # Battery cradle + removable pack, fused into the deck behind the motor.
    # Shifted back to x=-0.16 so the pack's front face clears the motor's rear
    # controller box (back face ~x=-0.081) instead of interpenetrating it.
    bx = -0.16
    # Rails span from the spindle-boss top (front x=-0.095 rests on the boss,
    # radius 0.115, and clears the motor shaft bearing r=0.088) back under the
    # shifted pack, so the pack stays one support island with the deck.
    for i, side in enumerate((1.0, -1.0)):
        deck.visual(
            Box((0.145, 0.014, 0.028)),
            origin=Origin(xyz=(-0.1675, side * 0.052, DECK_TOP_Z + 0.014)),
            material=p["panel_dark"],
            name=f"battery_rail_{i}", material_class_id="metal.paint_coated",
        )
    deck.visual(
        Box((0.145, 0.120, 0.058)),
        origin=Origin(xyz=(bx, 0.0, DECK_TOP_Z + 0.043)),
        material=p["engine_black"],
        name="battery_body", material_class_id="plastic.opaque_glossy_molded",
    )
    deck.visual(
        Box((0.100, 0.070, 0.005)),
        origin=Origin(xyz=(bx, 0.0, DECK_TOP_Z + 0.0745)),
        material=p["battery_accent"],
        name="battery_label", material_class_id="plastic.opaque_generic",
    )
    deck.visual(
        Box((0.008, 0.032, 0.018)),
        origin=Origin(xyz=(-0.205, 0.0, DECK_TOP_Z + 0.060)),
        material=p["battery_accent"],
        name="battery_latch", material_class_id="plastic.opaque_glossy_molded",
    )
    return motor


_POWER_FACTORIES = {
    "gas_engine": _build_power_gas_engine,
    "corded_electric": _build_power_corded_electric,
    "battery_brushless": _build_power_battery_brushless,
}


# --------------------------------------------------------------------------- #
# Wheels (multiplicity; each CONTINUOUS about lateral Y)
# --------------------------------------------------------------------------- #


def _lateral_wheel_y(side: float, deck_scale: float, tire_width: float) -> float:
    """Outboard wheel-center y that keeps the tire inboard face clear of the
    scaled shell edge (radius 0.230*deck_scale). Centered caster -> y=0."""
    if side == 0.0:
        return 0.0
    shell_r = 0.230 * deck_scale
    return side * (shell_r + 0.012 + 0.015 + 0.5 * tire_width + 0.006)


def _build_wheels(model: ArticulatedObject, r: ResolvedLawnMowerConfig, deck):
    p = _MAT
    for name, wx, side, wz, tw, wr, ww in _wheel_specs(r.wheel_count):
        wheel = model.part(name)
        yaw = side * pi / 2.0 if side != 0.0 else pi / 2.0
        wheel.visual(
            mesh_from_geometry(
                WheelGeometry(
                    wr,
                    ww,
                    rim=WheelRim(inner_radius=wr * 0.66, flange_height=0.006, flange_thickness=0.003),
                    hub=WheelHub(radius=0.024, width=ww + 0.004, cap_style="domed"),
                    face=WheelFace(dish_depth=0.004, front_inset=0.002),
                    spokes=WheelSpokes(style="straight", count=6, thickness=0.004, window_radius=0.006),
                    bore=WheelBore(style="round", diameter=0.016),
                ),
                f"{name}_hub",
            ),
            origin=Origin(rpy=(0.0, 0.0, yaw)),
            material=p["hub_gray"],
            name="hub", material_class_id="plastic.opaque_glossy_molded",
        )
        wheel.visual(
            mesh_from_geometry(
                TireGeometry(
                    wz - 0.005,
                    tw,
                    inner_radius=wr - 0.006,
                    tread=TireTread(style="block", depth=0.005, count=16 if wz < 0.11 else 18, land_ratio=0.55),
                    grooves=(TireGroove(center_offset=0.0, width=0.005, depth=0.0025),),
                    sidewall=TireSidewall(style="rounded", bulge=0.05),
                ),
                f"{name}_tire",
            ),
            origin=Origin(rpy=(0.0, 0.0, yaw)),
            material=p["tire_rubber"],
            name="tire", material_class_id="rubber.directional_grooved",
        )
        joint_y = _lateral_wheel_y(side, r.deck_scale, tw)
        model.articulation(
            f"{name}_spin",
            ArticulationType.CONTINUOUS,
            parent=deck,
            child=wheel,
            origin=Origin(xyz=(wx, joint_y, wz)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=20.0, velocity=35.0),
        )


# --------------------------------------------------------------------------- #
# Slot B: grass-collection factories
# --------------------------------------------------------------------------- #


def _build_collection_side_discharge(model: ArticulatedObject, r: ResolvedLawnMowerConfig, deck):
    """Right-side discharge port + curved deflector flap (REVOLUTE).

    The port + hinge track the scaled shell edge (-0.230*s on the -Y side) so
    the discharge mouth stays flush with the shell and the chute hinge_pin sits
    just outside the shell at every deck_scale (no shell/chute overlap).
    """
    p = _MAT
    edge = -0.230 * r.deck_scale  # right-side shell edge y
    hinge_y = edge - 0.004  # chute hinge just outboard of the shell edge
    deck.visual(
        Box((0.09, 0.010, 0.048)),
        origin=Origin(xyz=(CHUTE_HINGE[0], edge + 0.009, 0.073)),
        material=p["panel_dark"],
        name="discharge_port", material_class_id="metal.paint_coated",
    )
    deck.visual(
        Box((0.108, 0.006, 0.058)),
        origin=Origin(xyz=(CHUTE_HINGE[0], edge + 0.002, 0.073)),
        material=p["deck_body"],
        name="port_frame", material_class_id="metal.paint_coated",
    )
    deck.visual(
        Box((0.10, 0.016, 0.018)),
        origin=Origin(xyz=(CHUTE_HINGE[0], edge + 0.001, CHUTE_HINGE[2] - 0.002)),
        material=p["panel_dark"],
        name="chute_hinge_bracket", material_class_id="metal.paint_coated",
    )

    chute = model.part("discharge_chute")
    chute.visual(
        mesh_from_geometry(
            _build_curved_panel(0.10, 0.058, 0.018, 0.004, n=8),
            "chute_deflector_panel",
        ),
        material=p["deck_body"],
        name="deflector", material_class_id="metal.paint_coated",
    )
    chute.visual(
        Cylinder(radius=0.006, length=0.09),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)),
        material=p["steel_gray"],
        name="hinge_pin", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "chute_hinge",
        ArticulationType.REVOLUTE,
        parent=deck,
        child=chute,
        origin=Origin(xyz=(CHUTE_HINGE[0], hinge_y, CHUTE_HINGE[2])),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=CHUTE_OPEN_UPPER),
        mating=MatingContract(
            parent_face_geometry="chute_hinge_bracket",
            parent_face_side="negative_y",
            child_face_geometry="hinge_pin",
            child_face_side="positive_y",
            contact_tol=0.012,
        ),
    )
    return chute


def _build_collection_rear_bag(model: ArticulatedObject, r: ResolvedLawnMowerConfig, deck):
    """Rear discharge opening + spring door (REVOLUTE) + grass bag.

    The grass bag is a non-articulating accessory, so per Rule 1 its tubular
    frame + fabric body are fused into the deck visuals; only the spring door
    flap moves (REVOLUTE).
    """
    p = _MAT
    deck.visual(
        Box((0.004, 0.18, 0.065)),
        origin=Origin(xyz=(-0.302, 0.0, 0.0875)),
        material=p["panel_dark"],
        name="discharge_opening", material_class_id="metal.paint_coated",
    )

    # Spring-loaded discharge flap (REVOLUTE).
    door = model.part("discharge_door")
    door.visual(
        Box((0.004, 0.19, 0.075)),
        origin=Origin(xyz=(0.0, 0.0, -0.0375)),
        material=p["engine_black"],
        name="flap", material_class_id="plastic.opaque_glossy_molded",
    )
    door.visual(
        Cylinder(radius=0.007, length=0.20),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(pi / 2.0, 0.0, 0.0)),
        material=p["steel_gray"],
        name="hinge_barrel", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "discharge_door_hinge",
        ArticulationType.REVOLUTE,
        parent=deck,
        child=door,
        origin=Origin(xyz=(-0.300, 0.0, 0.125)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=1.2),
        mating=MatingContract(
            parent_face_geometry="discharge_opening",
            parent_face_side="negative_x",
            child_face_geometry="hinge_barrel",
            child_face_side="positive_x",
            contact_tol=0.012,
        ),
    )

    # Grass bag (frame + fabric) fused into the deck — non-articulating.
    for i, side in enumerate((1.0, -1.0)):
        deck.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    [
                        (-0.305, side * 0.12, 0.06),
                        (-0.38, side * 0.12, 0.22),
                        (-0.44, side * 0.12, 0.32),
                    ],
                    radius=0.008,
                    samples_per_segment=8,
                    radial_segments=10,
                ),
                f"bag_frame_tube_{i}",
            ),
            material=p["steel_gray"],
            name=f"bag_frame_tube_{i}", material_class_id="metal.steel_bare",
        )
    deck.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [(-0.44, -0.12, 0.32), (-0.44, 0.0, 0.32), (-0.44, 0.12, 0.32)],
                radius=0.008,
                samples_per_segment=4,
                radial_segments=10,
            ),
            "bag_frame_crossbar",
        ),
        material=p["steel_gray"],
        name="bag_frame_crossbar", material_class_id="metal.steel_bare",
    )
    # Fabric body draped over the frame cage. Its y-width is widened just enough
    # to embed the +-0.12 frame tubes (y to +-0.125), forming one connected
    # support island; x/z stay compact so it never reaches the handle path.
    deck.visual(
        Box((0.14, 0.25, 0.18)),
        origin=Origin(xyz=(-0.40, 0.0, 0.20)),
        material=p["bag_fabric"],
        name="bag_body", material_class_id="fabric.canvas",
    )
    return door


def _build_collection_mulch_plug(model: ArticulatedObject, r: ResolvedLawnMowerConfig, deck):
    """Rear mulching plug insert + cover panel fused into the deck (no joint)."""
    p = _MAT
    deck.visual(
        mesh_from_geometry(
            _curved_shell_arc(0.224, 0.230, 152.0, 208.0, 0.037),
            "mulching_plug",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.005)),
        material=p["panel_dark"],
        name="mulching_plug", material_class_id="plastic.opaque_glossy_molded",
    )
    deck.visual(
        mesh_from_geometry(
            _curved_shell_arc(0.230, 0.236, 148.0, 212.0, 0.052),
            "rear_cover_panel",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.008)),
        material=p["deck_body"],
        name="rear_cover_panel", material_class_id="metal.paint_coated",
    )
    return None


_COLLECTION_FACTORIES = {
    "side_discharge": _build_collection_side_discharge,
    "rear_bag": _build_collection_rear_bag,
    "mulch_plug": _build_collection_mulch_plug,
}


# --------------------------------------------------------------------------- #
# Slot C: handle factories  (REVOLUTE fold kept on EVERY variant)
# --------------------------------------------------------------------------- #


def _emit_fold_joint(model: ArticulatedObject, deck, child) -> None:
    """Emit the shared handlebar fold REVOLUTE about the lateral (Y) hinge axle.

    The fold pivot is the y-axis axle rod at the handlebar local origin. Both
    the deck (``handle_pivot_rod``, added in ``_build_deck``) and the handlebar
    (``fold_axle`` knuckle, added here) carry real hinge hardware that contains
    the joint origin, so ``fail_if_articulation_origin_far_from_geometry`` is
    satisfied on both sides.
    """
    p = _MAT
    # Hinge axle through the handlebar local origin (0,0,0) connecting the two
    # lower-tube roots; this is the physical fold axle, and it places child
    # geometry on the joint origin (child_distance -> ~0).
    child.visual(
        Cylinder(radius=0.013, length=0.34),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(pi / 2.0, 0.0, 0.0)),
        material=p["steel_gray"],
        name="fold_axle", material_class_id="metal.steel_bare",
    )
    for i, side in enumerate((1.0, -1.0)):
        child.visual(
            Box((0.026, 0.018, 0.05)),
            origin=Origin(xyz=(0.008, side * 0.122, -0.018)),
            material=p["panel_dark"],
            name=f"fold_knuckle_{i}", material_class_id="metal.paint_coated",
        )
    model.articulation(
        "handlebar_fold",
        ArticulationType.REVOLUTE,
        parent=deck,
        child=child,
        origin=Origin(xyz=HANDLE_PIVOT),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=40.0, velocity=1.5, lower=HANDLE_FOLD_LOWER, upper=0.0),
        mating=MatingContract(
            parent_face_geometry="handle_pivot_rod",
            parent_face_side="positive_z",
            child_face_geometry="fold_axle",
            child_face_side="negative_z",
            contact_tol=0.05,
        ),
    )


def _build_handle_u_fold(model: ArticulatedObject, r: ResolvedLawnMowerConfig, deck):
    """U-handle with single REVOLUTE fold (parent verbatim)."""
    p = _MAT
    handlebar = model.part("handlebar")
    lower_pts = [
        (0.03, 0.165, -0.075),
        # Pivot-root point sits on the fold axle axis so the tube stays
        # connected to fold_axle.
        (0.0, 0.165, 0.0),
        # P2 low (z=0.05): after the -2.27 rad fold the tube rides above the
        # rear wheel bracket tops (z=0.175) instead of through them.
        (-0.10, 0.175, 0.05),
        # P3 pushed rearward (x=-0.26, z=0.21): the fold rotation lifts this
        # section to z~0.23 over the deck dome (surface z<=0.224 at any
        # deck_scale); the previous (-0.16, 0.145) folded to z~0.198 and dug
        # into the shell dome.
        (-0.26, 0.185, 0.210),
        (-0.40, 0.190, 0.355),
    ]
    upper_pts = [
        (-0.37, 0.188, 0.329),
        (-0.60, 0.205, 0.530),
        (-0.78, 0.215, 0.690),
        (-0.93, 0.220, 0.830),
    ]
    for i, side in enumerate((1.0, -1.0)):
        handlebar.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    _mirror_y(lower_pts, side), radius=0.011, samples_per_segment=10, radial_segments=14
                ),
                f"handle_lower_tube_{i}",
            ),
            material=p["accent"],
            name=f"side_tube_lower_{i}", material_class_id="metal.paint_coated",
        )
        handlebar.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    _mirror_y(upper_pts, side), radius=0.011, samples_per_segment=10, radial_segments=14
                ),
                f"handle_upper_tube_{i}",
            ),
            material=p["handle_black"],
            name=f"side_tube_upper_{i}", material_class_id="metal.paint_coated",
        )
    handlebar.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [(-0.45, -0.196, 0.40), (-0.45, 0.0, 0.40), (-0.45, 0.196, 0.40)],
                radius=0.009,
                samples_per_segment=6,
                radial_segments=12,
            ),
            "handle_cross_brace",
        ),
        material=p["handle_black"],
        name="cross_brace", material_class_id="metal.paint_coated",
    )
    handlebar.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [(-0.93, -0.235, 0.83), (-0.93, 0.0, 0.83), (-0.93, 0.235, 0.83)],
                radius=0.012,
                samples_per_segment=6,
                radial_segments=14,
            ),
            "handle_grip_bar",
        ),
        material=p["handle_black"],
        name="grip_bar", material_class_id="metal.paint_coated",
    )
    handlebar.visual(
        Cylinder(radius=0.018, length=0.26),
        origin=Origin(xyz=(-0.93, 0.0, 0.83), rpy=(pi / 2.0, 0.0, 0.0)),
        material=p["grip_foam"],
        name="grip_foam", material_class_id="rubber.sponge_foam",
    )
    handlebar.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    (-0.87, -0.2177, 0.770),
                    (-0.95, -0.21, 0.860),
                    (-1.00, 0.0, 0.900),
                    (-0.95, 0.21, 0.860),
                    (-0.87, 0.2177, 0.770),
                ],
                radius=0.005,
                samples_per_segment=10,
                radial_segments=10,
            ),
            "handle_control_bail",
        ),
        material=p["accent"],
        name="control_bail", material_class_id="metal.paint_coated",
    )
    handlebar.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    # Cable start rides the lower tube root so the folded cable
                    # stays above the rear wheel brackets (bracket top z=0.175);
                    # mid points track the reshaped lower tube so the folded
                    # cable clears the deck dome as well.
                    (0.03, 0.152, -0.075),
                    (-0.10, 0.160, 0.050),
                    (-0.26, 0.170, 0.210),
                    (-0.40, 0.180, 0.355),
                    (-0.60, 0.195, 0.530),
                    (-0.78, 0.205, 0.690),
                    (-0.86, 0.208, 0.765),
                ],
                radius=0.0035,
                samples_per_segment=10,
                radial_segments=10,
            ),
            "handle_cable",
        ),
        material=p["cable_black"],
        name="cable", material_class_id="tech.cable_pipe_bundle",
    )
    _emit_fold_joint(model, deck, handlebar)
    return [handlebar]


def _build_handle_loop_bullhorn(model: ArticulatedObject, r: ResolvedLawnMowerConfig, deck):
    """Bullhorn / closed D-loop grip handle, single REVOLUTE fold (var_loophandle)."""
    p = _MAT
    handlebar = model.part("handlebar")
    lower_pts = [
        (0.03, 0.165, -0.075),
        # Pivot-root point sits on the fold axle axis so the tube stays
        # connected to fold_axle; the mid tube's outer bias (P2 y) keeps the
        # folded handle clear of the deck shell rim and rear wheel brackets.
        (0.0, 0.165, 0.0),
        # P2 z low (0.05): after the -2.27 rad fold the segment rides above the
        # bracket top edge; a larger z would land inside the bracket.
        (-0.10, 0.175, 0.05),
        # P3 y outer bias: without it the folded P3 segment (spline undershoot
        # drops tube y to ~0.118) cuts into the engine housing corner
        # (housing y<=0.12, z>=0.228); y=0.165 keeps the folded tube outside.
        (-0.25, 0.165, 0.200),
        # P4 lifted (z 0.36) and kept outboard (y 0.14): the folded P3->P4
        # spline mid-section otherwise clips the engine housing edge — both at
        # the -2.27 flat fold (world x~0.126, housing x<=0.13) and mid-fold
        # (~-1.89 rad, where the segment crosses the housing top-front corner
        # at z~0.40 with y<0.12).
        (-0.38, 0.140, 0.360),
    ]
    upper_pts = [
        (-0.36, 0.095, 0.350),
        (-0.56, 0.038, 0.510),
        (-0.72, 0.025, 0.665),
    ]
    for i, side in enumerate((1.0, -1.0)):
        handlebar.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    _mirror_y(lower_pts, side), radius=0.011, samples_per_segment=10, radial_segments=14
                ),
                f"handle_lower_tube_{i}",
            ),
            material=p["accent"],
            name=f"side_tube_lower_{i}", material_class_id="metal.paint_coated",
        )
        handlebar.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    _mirror_y(upper_pts, side), radius=0.011, samples_per_segment=10, radial_segments=14
                ),
                f"handle_upper_tube_{i}",
            ),
            material=p["handle_black"],
            name=f"side_tube_upper_{i}", material_class_id="metal.paint_coated",
        )
    grip_loop_pts = [
        (-0.71, 0.025, 0.655),
        (-0.83, 0.018, 0.760),
        (-0.91, 0.0, 0.835),
        (-0.83, -0.018, 0.760),
        (-0.71, -0.025, 0.655),
        (-0.66, -0.012, 0.615),
        (-0.64, 0.0, 0.598),
        (-0.66, 0.012, 0.615),
    ]
    handlebar.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                grip_loop_pts, radius=0.012, samples_per_segment=14, radial_segments=14, closed_spline=True
            ),
            "handle_grip_loop",
        ),
        material=p["handle_black"],
        name="grip_bar", material_class_id="metal.paint_coated",
    )
    handlebar.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    (-0.80, 0.022, 0.725),
                    (-0.86, 0.015, 0.790),
                    (-0.91, 0.0, 0.835),
                    (-0.86, -0.015, 0.790),
                    (-0.80, -0.022, 0.725),
                ],
                radius=0.018,
                samples_per_segment=12,
                radial_segments=16,
            ),
            "handle_grip_foam",
        ),
        material=p["grip_foam"],
        name="grip_foam", material_class_id="rubber.sponge_foam",
    )
    handlebar.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    (-0.84, -0.020, 0.790),
                    (-0.91, -0.015, 0.860),
                    (-0.95, 0.0, 0.890),
                    (-0.91, 0.015, 0.860),
                    (-0.84, 0.020, 0.790),
                ],
                radius=0.005,
                samples_per_segment=10,
                radial_segments=10,
            ),
            "handle_control_bail",
        ),
        material=p["accent"],
        name="control_bail", material_class_id="metal.paint_coated",
    )
    handlebar.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    # Cable start rides the lower tube root so the folded cable
                    # stays above the rear wheel brackets (z>0.18 folded).
                    (0.03, 0.152, -0.075),
                    (-0.10, 0.165, 0.080),
                    (-0.25, 0.155, 0.200),
                    # Matches the P4 outboard lift: keeps the cable clear of
                    # the engine housing corner through the whole fold sweep.
                    (-0.38, 0.140, 0.360),
                    (-0.56, 0.038, 0.510),
                    (-0.72, 0.025, 0.660),
                    (-0.80, 0.020, 0.730),
                ],
                radius=0.0035,
                samples_per_segment=10,
                radial_segments=10,
            ),
            "handle_cable",
        ),
        material=p["cable_black"],
        name="cable", material_class_id="tech.cable_pipe_bundle",
    )
    _emit_fold_joint(model, deck, handlebar)
    return [handlebar]


def _build_handle_telescoping(model: ArticulatedObject, r: ResolvedLawnMowerConfig, deck):
    """Two-segment telescoping handle: REVOLUTE fold + PRISMATIC slide (var_telehandle).

    The fold REVOLUTE is kept (deck -> lower_handle); a PRISMATIC slide
    (lower_handle -> upper_grip) adds height adjustment along the handle rake.
    """
    p = _MAT
    lower_handle = model.part("lower_handle")
    lower_tube_pts = [
        (0.03, 0.165, -0.075),
        (0.0, 0.165, 0.0),
        # Same folded-pose clearance shaping as the U-handle: z kept low so
        # the -2.27 rad fold rides the tube above the rear wheel bracket tops
        # (z=0.175) and the deck dome.
        (-0.10, 0.175, 0.05),
        (-0.28, 0.182, 0.233),
    ]
    sleeve_pts = [
        (-0.28, 0.182, 0.233),
        (-0.40, 0.190, 0.355),
        (-0.52, 0.198, 0.475),
    ]
    for i, side in enumerate((1.0, -1.0)):
        lower_handle.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    _mirror_y(lower_tube_pts, side), radius=0.011, samples_per_segment=10, radial_segments=14
                ),
                f"handle_lower_tube_{i}",
            ),
            material=p["accent"],
            name=f"side_tube_lower_{i}", material_class_id="metal.paint_coated",
        )
        lower_handle.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    _mirror_y(sleeve_pts, side), radius=0.014, samples_per_segment=10, radial_segments=14
                ),
                f"handle_sleeve_{i}",
            ),
            material=p["handle_black"],
            name=f"sleeve_{i}", material_class_id="metal.paint_coated",
        )
        lower_handle.visual(
            Box((0.038, 0.020, 0.014)),
            origin=Origin(xyz=(-0.52, side * 0.218, 0.475)),
            material=p["steel_gray"],
            name=f"clamp_lever_{i}", material_class_id="metal.steel_bare",
        )
    # No cross brace on the telescoping lower handle: any y-spanning brace on
    # this section folds to world x in [-0.18, 0.08], straight through the
    # power-unit housing (x<=0.13, z>=0.228) — the old (-0.22, 0.175) brace
    # landed on the spindle boss/crankshaft/housing. The sleeves are instead
    # cross-tied at the junction by the slide yoke below (which folds clear).
    # Center telescoping receiver sleeve straddling HANDLE_JUNCTION along the
    # slide rake. It places real lower-segment hardware on the handle_slide
    # joint origin (centerline, where the two side tubes leave a gap). The
    # sleeve spans rake [-0.02, +0.10] around the junction: the up-rake end
    # keeps >=10 mm of slide rod engaged at full 0.12 extension, while the
    # down-rake mouth stays short of the engine top-shroud corner that a
    # longer sleeve grazes mid-fold (fold ~-1.8 rad).
    slide_ry = atan2(HANDLE_SLIDE_AXIS[0], HANDLE_SLIDE_AXIS[2])
    jx, jy, jz = HANDLE_JUNCTION
    lower_handle.visual(
        Cylinder(radius=0.016, length=0.12),
        origin=Origin(xyz=(jx - 0.0298, 0.0, jz + 0.02668), rpy=(0.0, slide_ry, 0.0)),
        material=p["steel_gray"],
        name="slide_receiver", material_class_id="metal.steel_bare",
    )
    # Cross yoke tying the center receiver to the two side tubes (sleeves pass
    # through y~=+-0.19 at the junction), so the receiver is not a floating island.
    lower_handle.visual(
        Box((0.030, 0.40, 0.024)),
        origin=Origin(xyz=(jx, 0.0, jz), rpy=(0.0, slide_ry, 0.0)),
        material=p["handle_black"],
        name="slide_yoke", material_class_id="metal.paint_coated",
    )
    _emit_fold_joint(model, deck, lower_handle)

    upper_grip = model.part("upper_grip")
    upper_tube_pts = [
        (-0.30 - jx, 0.184 - jy, 0.255 - jz),
        (-0.50 - jx, 0.197 - jy, 0.455 - jz),
        (-0.70 - jx, 0.210 - jy, 0.630 - jz),
        (-0.93 - jx, 0.220 - jy, 0.830 - jz),
    ]
    for i, side in enumerate((1.0, -1.0)):
        upper_grip.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    _mirror_y(upper_tube_pts, side), radius=0.009, samples_per_segment=10, radial_segments=14
                ),
                f"handle_upper_tube_{i}",
            ),
            material=p["handle_black"],
            name=f"side_tube_upper_{i}", material_class_id="metal.paint_coated",
        )
    # Center telescoping inner rod through the upper-segment local origin
    # region, i.e. the handle_slide joint origin. It slides inside the lower
    # receiver sleeve and carries real child hardware near the joint origin.
    # The rod spans rake [-0.03, +0.15] (center offset +0.06 along the rake):
    # the old symmetric rod's down-rake end (rake -0.08) swept through the
    # power-unit housing/top-shroud corner (x~0.13, z~0.41) around fold
    # ~-1.8..-1.9 rad; at rake >= -0.03 every rod point sweeps clear, while
    # >=10 mm of rod still engages the receiver at full slide extension.
    upper_grip.visual(
        Cylinder(radius=0.0125, length=0.18),
        origin=Origin(xyz=(-0.0447, 0.0, 0.04002), rpy=(0.0, slide_ry, 0.0)),
        material=p["steel_gray"],
        name="slide_rod", material_class_id="metal.steel_bare",
    )
    # Cross yoke tying the center slide rod to the two upper side tubes (they
    # pass through child-local y~+-0.19 at the junction), so the rod is not a
    # floating island. Same thin rake-aligned slab as the lower-handle yoke:
    # the previous fat box (0.14 x 0.40 x 0.11) folded down onto the deck dome,
    # the spindle boss and the engine housing bottom; this slab folds to
    # x~0.25 / z~0.24, clear of the center stack at every deck_scale.
    upper_grip.visual(
        Box((0.030, 0.40, 0.024)),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, slide_ry, 0.0)),
        material=p["handle_black"],
        name="slide_yoke", material_class_id="metal.paint_coated",
    )
    upper_grip.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    (-0.93 - jx, -0.235 - jy, 0.83 - jz),
                    (-0.93 - jx, 0.0 - jy, 0.83 - jz),
                    (-0.93 - jx, 0.235 - jy, 0.83 - jz),
                ],
                radius=0.012,
                samples_per_segment=6,
                radial_segments=14,
            ),
            "handle_grip_bar",
        ),
        material=p["handle_black"],
        name="grip_bar", material_class_id="metal.paint_coated",
    )
    upper_grip.visual(
        Cylinder(radius=0.018, length=0.26),
        origin=Origin(xyz=(-0.93 - jx, 0.0 - jy, 0.83 - jz), rpy=(pi / 2.0, 0.0, 0.0)),
        material=p["grip_foam"],
        name="grip_foam", material_class_id="rubber.sponge_foam",
    )
    upper_grip.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    (-0.87 - jx, -0.2177 - jy, 0.770 - jz),
                    (-0.95 - jx, -0.21 - jy, 0.860 - jz),
                    (-1.00 - jx, 0.0 - jy, 0.900 - jz),
                    (-0.95 - jx, 0.21 - jy, 0.860 - jz),
                    (-0.87 - jx, 0.2177 - jy, 0.770 - jz),
                ],
                radius=0.005,
                samples_per_segment=10,
                radial_segments=10,
            ),
            "handle_control_bail",
        ),
        material=p["accent"],
        name="control_bail", material_class_id="metal.paint_coated",
    )
    upper_grip.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    (-0.44 - jx, 0.193 - jy, 0.395 - jz),
                    (-0.60 - jx, 0.195 - jy, 0.530 - jz),
                    (-0.78 - jx, 0.205 - jy, 0.690 - jz),
                    (-0.86 - jx, 0.208 - jy, 0.765 - jz),
                ],
                radius=0.0035,
                samples_per_segment=10,
                radial_segments=10,
            ),
            "handle_cable",
        ),
        material=p["cable_black"],
        name="cable", material_class_id="tech.cable_pipe_bundle",
    )
    model.articulation(
        "handle_slide",
        ArticulationType.PRISMATIC,
        parent=lower_handle,
        child=upper_grip,
        origin=Origin(xyz=HANDLE_JUNCTION),
        axis=HANDLE_SLIDE_AXIS,
        motion_limits=MotionLimits(effort=30.0, velocity=0.15, lower=0.0, upper=HANDLE_SLIDE_UPPER),
        mating=MatingContract(
            parent_face_geometry="slide_receiver",
            parent_face_side="positive_z",
            child_face_geometry="slide_rod",
            child_face_side="negative_z",
            contact_tol=0.15,
        ),
    )
    return [lower_handle, upper_grip]


_HANDLE_FACTORIES = {
    "u_handle_fold": _build_handle_u_fold,
    "telescoping_2seg": _build_handle_telescoping,
    "loop_bullhorn": _build_handle_loop_bullhorn,
}


# --------------------------------------------------------------------------- #
# Top-level builder
# --------------------------------------------------------------------------- #


def build_lawn_mower(
    config: LawnMowerConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    """Compose a walk-behind push lawn mower from the resolved slot choices."""
    r = resolve_config(config)
    model = ArticulatedObject(name="push_lawn_mower", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    deck = _build_deck(model, r)
    power_part = _POWER_FACTORIES[r.power_unit](model, r, deck)
    _build_blade(model, r, power_part=power_part)
    _build_wheels(model, r, deck)
    _COLLECTION_FACTORIES[r.grass_collection](model, r, deck)
    _HANDLE_FACTORIES[r.handle](model, r, deck)
    return model


def build_seeded_lawn_mower(seed: int) -> ArticulatedObject:
    return build_lawn_mower(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _handle_part_names(handle: HandleModule) -> list[str]:
    if handle == "telescoping_2seg":
        return ["lower_handle", "upper_grip"]
    return ["handlebar"]


def _grip_part_name(handle: HandleModule) -> str:
    return "upper_grip" if handle == "telescoping_2seg" else "handlebar"


def run_lawn_mower_tests(model: ArticulatedObject, config: LawnMowerConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    specs = _wheel_specs(r.wheel_count)

    deck = model.get_part("deck")
    blade = model.get_part("blade")
    power_part = model.get_part("engine" if r.power_unit == "gas_engine" else "motor")
    wheels = [model.get_part(spec[0]) for spec in specs]
    blade_joint = model.get_articulation("blade_spin")
    fold_joint = model.get_articulation("handlebar_fold")
    first_spin = model.get_articulation(f"{specs[0][0]}_spin")

    grip_part = model.get_part(_grip_part_name(r.handle))

    # --- intentional captured-fit overlaps ---
    ctx.allow_overlap(
        blade,
        power_part,
        elem_a="crankshaft",
        elem_b="power_housing",
        reason="Crankshaft/motor shaft is intentionally captured in the power-unit housing bore (proxy fit).",
    )
    # Power-unit drive spindle drops through the deck spindle bore and ends at
    # the blade-spin bearing; the blade crankshaft/hub nests on it. These are
    # captured rotary fits at the central spindle.
    ctx.allow_overlap(
        deck,
        power_part,
        elem_a="spindle_boss",
        elem_b="drive_spindle",
        reason="Power-unit drive spindle passes through the deck spindle-boss bore (clearance/captured fit).",
    )
    ctx.allow_overlap(
        deck,
        power_part,
        elem_a="spindle_bearing",
        elem_b="drive_spindle",
        reason="Power-unit drive spindle rotates inside the deck spindle bearing collar (captured bearing fit).",
    )
    ctx.allow_overlap(
        blade,
        power_part,
        elem_a="crankshaft",
        elem_b="drive_spindle",
        reason="Blade crankshaft is coaxially coupled to the power-unit drive spindle (captured rotary fit).",
    )
    ctx.allow_overlap(
        blade,
        power_part,
        elem_a="blade_hub",
        elem_b="drive_spindle",
        reason="Blade hub seats around the lower end of the power-unit drive spindle (captured rotary fit).",
    )
    ctx.allow_overlap(
        blade,
        power_part,
        elem_a="blade_hub",
        elem_b="blade_bearing",
        reason="Blade hub rotates on the power-unit blade-spin bearing (captured rotary fit).",
    )
    ctx.allow_overlap(
        blade,
        power_part,
        elem_a="blade_bar",
        elem_b="blade_bearing",
        reason="Cutting blade bar runs just under the power-unit blade-spin bearing (captured rotary fit).",
    )
    # Blade crankshaft rises through the deck spindle bore + bearing collar.
    ctx.allow_overlap(
        blade,
        deck,
        elem_a="crankshaft",
        elem_b="spindle_bearing",
        reason="Blade crankshaft rotates through the deck spindle bearing collar bore (captured bearing fit).",
    )
    ctx.allow_overlap(
        blade,
        deck,
        elem_a="crankshaft",
        elem_b="spindle_boss",
        reason="Blade crankshaft passes up through the deck spindle-boss bore (clearance/captured fit).",
    )
    # Electric/battery motors add a base shaft-bearing disk the shaft passes
    # through (and a motor cap on the brushless hub): captured-fit bearing bore.
    if r.power_unit in ("corded_electric", "battery_brushless"):
        ctx.allow_overlap(
            blade,
            power_part,
            elem_a="crankshaft",
            elem_b="shaft_bearing",
            reason="Motor shaft rotates inside the base shaft-bearing disk bore (captured bearing fit).",
        )
    if r.power_unit == "battery_brushless":
        ctx.allow_overlap(
            blade,
            power_part,
            elem_a="crankshaft",
            elem_b="motor_cap",
            reason="Motor shaft is captured through the brushless motor cap bore (proxy fit).",
        )
    # Rear-bag spring door: its hinge barrel is captured at the rear apron edge.
    if r.grass_collection == "rear_bag":
        ctx.allow_overlap(
            deck,
            model.get_part("discharge_door"),
            elem_a="rear_apron",
            elem_b="hinge_barrel",
            reason="Discharge-door hinge barrel is intentionally captured at the rear apron hinge line (pin-in-barrel proxy fit).",
        )
        # The spring door swings open across the rear apron mouth while
        # discharging; its lower edge stays close to the deck.
        ctx.allow_overlap(
            deck,
            model.get_part("discharge_door"),
            reason="rear discharge door swings close past the deck apron while opening",
        )
    # Side-discharge deflector: its hinge pin is captured in the deck hinge
    # bracket, and the deflector root closes flush against that bracket.
    if r.grass_collection == "side_discharge":
        ctx.allow_overlap(
            deck,
            model.get_part("discharge_chute"),
            elem_a="chute_hinge_bracket",
            elem_b="hinge_pin",
            reason="Side-discharge deflector hinge pin is intentionally captured in the deck chute hinge bracket (pin-in-bracket proxy fit).",
        )
        ctx.allow_overlap(
            deck,
            model.get_part("discharge_chute"),
            elem_a="chute_hinge_bracket",
            elem_b="deflector",
            reason="Side-discharge deflector root closes flush against the deck chute hinge bracket (closed-pose seating contact).",
        )
    for (name, _wx, _side, _wz, _tw, _wr, _ww), wheel in zip(specs, wheels):
        ctx.allow_overlap(
            deck,
            wheel,
            elem_a=f"{name}_axle",
            elem_b="hub",
            reason="Stub/through axle is intentionally captured in the wheel hub bore (interference proxy fit).",
        )
    # The part carrying the lower tubes (handlebar, or lower_handle for the
    # telescoping variant) is the one bolted over the deck pivot bolt bosses.
    lower_handle_part = model.get_part(
        "lower_handle" if r.handle == "telescoping_2seg" else "handlebar"
    )
    for i in (0, 1):
        ctx.allow_overlap(
            deck,
            lower_handle_part,
            elem_a=f"handle_bolt_boss_{i}",
            elem_b=f"side_tube_lower_{i}",
            reason="Handle lower tube end is intentionally bolted over the deck pivot bolt boss.",
        )
    # Handlebar fold axle is the lateral hinge pin captured by the deck pivot
    # rod + the two bolt bosses it threads through (pin-in-rod proxy fit).
    ctx.allow_overlap(
        deck,
        lower_handle_part,
        elem_a="handle_pivot_rod",
        elem_b="fold_axle",
        reason="Handlebar fold axle pivots inside the deck hinge pivot rod (captured hinge-pin fit).",
    )
    for i in (0, 1):
        ctx.allow_overlap(
            deck,
            lower_handle_part,
            elem_a=f"handle_bolt_boss_{i}",
            elem_b="fold_axle",
            reason="Handlebar fold axle is captured through the deck pivot bolt boss (captured hinge-pin fit).",
        )
        ctx.allow_overlap(
            deck,
            lower_handle_part,
            elem_a="handle_pivot_rod",
            elem_b=f"fold_knuckle_{i}",
            reason="Handlebar fold knuckle straddles the deck hinge pivot rod (captured hinge fit).",
        )
        ctx.allow_overlap(
            deck,
            lower_handle_part,
            elem_a=f"handle_bolt_boss_{i}",
            elem_b=f"fold_knuckle_{i}",
            reason="Handlebar fold knuckle straddles the deck pivot bolt boss (captured hinge fit).",
        )
        ctx.allow_overlap(
            deck,
            lower_handle_part,
            elem_a=f"handle_bracket_{i}",
            elem_b="fold_axle",
            reason="Handlebar fold axle threads through the deck handle pivot bracket (captured hinge-pin fit).",
        )
        ctx.allow_overlap(
            deck,
            lower_handle_part,
            elem_a=f"handle_bracket_{i}",
            elem_b=f"fold_knuckle_{i}",
            reason="Handlebar fold knuckle sits between the deck handle pivot brackets (captured hinge fit).",
        )
    if r.handle == "telescoping_2seg":
        lower = model.get_part("lower_handle")
        ctx.allow_overlap(
            lower,
            grip_part,
            elem_a="sleeve_0",
            elem_b="side_tube_upper_0",
            reason="Upper grip tube slides inside the lower handle sleeve (telescoping prismatic fit).",
        )
        ctx.allow_overlap(
            lower,
            grip_part,
            elem_a="sleeve_1",
            elem_b="side_tube_upper_1",
            reason="Upper grip tube slides inside the lower handle sleeve (telescoping prismatic fit).",
        )
        ctx.allow_overlap(
            lower,
            grip_part,
            elem_a="slide_receiver",
            elem_b="slide_rod",
            reason="Upper-grip center slide rod telescopes inside the lower-handle receiver sleeve (prismatic captured fit).",
        )
        for si in (0, 1):
            ctx.allow_overlap(
                lower,
                grip_part,
                elem_a=f"sleeve_{si}",
                elem_b="cable",
                reason="Control cable is clipped along the telescoping sleeve and routes past it (captured routing).",
            )
        # The two center yokes (carrying receiver + rod) telescope through each
        # other and the opposite segment's slide hardware along the slide rake.
        for la, lb in (
            ("slide_yoke", "slide_yoke"),
            ("slide_yoke", "slide_rod"),
            ("slide_receiver", "slide_yoke"),
            ("slide_yoke", "side_tube_upper_0"),
            ("slide_yoke", "side_tube_upper_1"),
            ("sleeve_0", "slide_yoke"),
            ("sleeve_1", "slide_yoke"),
            ("side_tube_lower_0", "slide_yoke"),
            ("side_tube_lower_1", "slide_yoke"),
        ):
            ctx.allow_overlap(
                lower,
                grip_part,
                elem_a=la,
                elem_b=lb,
                reason="Telescoping center yokes/rails interleave as the upper grip slides into the lower handle (prismatic captured fit).",
            )

    # --- wheels stand on the ground, each at its mount ---
    for (name, wx, side, wz, _tw, _wr, _ww), wheel in zip(specs, wheels):
        aabb = ctx.part_world_aabb(wheel)
        ctx.check(f"{name}_touches_ground", aabb is not None and abs(aabb[0][2]) <= 0.006, f"aabb={aabb!r}")
        pos = ctx.part_world_position(wheel)
        jy = _lateral_wheel_y(side, r.deck_scale, _tw)
        ok = (
            pos is not None
            and abs(pos[0] - wx) < 0.01
            and abs(pos[1] - jy) < 0.01
            and abs(pos[2] - wz) < 0.01
        )
        ctx.check(f"{name}_at_mount", ok, f"pos={pos!r}")

    ctx.check(
        "wheel_count_matches_multiplicity",
        len(wheels) == r.wheel_count and r.wheel_count in (3, 4),
        f"n={len(wheels)} wheel_count={r.wheel_count}",
    )

    # --- at least one wheel spins as a pure rotation about its axle ---
    pos0 = ctx.part_world_position(wheels[0])
    with ctx.pose({first_spin: pi / 3.0}):
        pos1 = ctx.part_world_position(wheels[0])
    ctx.check(
        "wheel_spin_pure_rotation",
        pos0 is not None and pos1 is not None and max(abs(a - b) for a, b in zip(pos0, pos1)) < 1e-6,
        f"pos0={pos0!r}, pos1={pos1!r}",
    )
    ctx.check(
        "wheel_spin_is_continuous_lateral",
        first_spin.articulation_type == ArticulationType.CONTINUOUS and tuple(first_spin.axis) == (0.0, 1.0, 0.0),
        f"type={first_spin.articulation_type}, axis={first_spin.axis}",
    )

    # --- blade hidden under the deck, CONTINUOUS about vertical axis ---
    bar = ctx.part_element_world_aabb(blade, elem="blade_bar")
    ctx.check(
        "blade_hidden_under_deck",
        bar is not None and bar[0][2] > 0.045 and bar[1][2] < 0.12,
        f"blade_bar_aabb={bar!r}",
    )
    ctx.check(
        "blade_spin_is_continuous_vertical",
        blade_joint.articulation_type == ArticulationType.CONTINUOUS and tuple(blade_joint.axis) == (0.0, 0.0, 1.0),
        f"type={blade_joint.articulation_type}, axis={blade_joint.axis}",
    )
    if bar is not None:
        rest_x = bar[1][0] - bar[0][0]
        rest_y = bar[1][1] - bar[0][1]
        with ctx.pose({blade_joint: pi / 2.0}):
            turned = ctx.part_element_world_aabb(blade, elem="blade_bar")
        ok = (
            turned is not None
            and rest_x > rest_y
            and (turned[1][1] - turned[0][1]) > (turned[1][0] - turned[0][0])
        )
        ctx.check("blade_spins_about_vertical_axis", ok, f"rest={bar!r}, turned={turned!r}")

    # --- power unit seated centered on the deck ---
    ppos = ctx.part_world_position(power_part)
    ctx.check(
        "power_unit_centered_on_deck",
        ppos is not None and abs(ppos[0]) < 0.05 and abs(ppos[1]) < 0.05,
        f"pos={ppos!r}",
    )
    ctx.expect_contact(
        power_part,
        deck,
        elem_a="power_housing",
        elem_b="spindle_boss",
        contact_tol=0.003,
        name="power_unit_seated_on_deck_boss",
    )

    # --- handle: fold REVOLUTE kept; grip ~1 m high; folds flat over deck ---
    ctx.check(
        "handle_fold_is_revolute",
        fold_joint.articulation_type == ArticulationType.REVOLUTE,
        f"type={fold_joint.articulation_type}",
    )
    grip = ctx.part_element_world_aabb(grip_part, elem="grip_foam")
    ctx.check(
        "grip_height_about_1m",
        grip is not None and 0.93 <= (grip[0][2] + grip[1][2]) * 0.5 <= 1.06,
        f"grip_aabb={grip!r}",
    )
    with ctx.pose({fold_joint: HANDLE_FOLD_LOWER}):
        folded_grip = ctx.part_element_world_aabb(grip_part, elem="grip_foam")
    ok = (
        folded_grip is not None
        and grip is not None
        and (folded_grip[0][0] + folded_grip[1][0]) * 0.5 > 0.6
        and (folded_grip[0][2] + folded_grip[1][2]) * 0.5 < 0.6
        and folded_grip[0][2] > 0.04
    )
    ctx.check("handle_folds_flat_over_deck", ok, f"folded_grip={folded_grip!r}")

    # --- telescoping slide extends the grip upward ---
    if r.handle == "telescoping_2seg":
        slide = model.get_articulation("handle_slide")
        ctx.check(
            "handle_slide_is_prismatic",
            slide.articulation_type == ArticulationType.PRISMATIC,
            f"type={slide.articulation_type}",
        )
        if grip is not None:
            with ctx.pose({slide: HANDLE_SLIDE_UPPER}):
                ext = ctx.part_element_world_aabb(grip_part, elem="grip_foam")
            ctx.check(
                "handle_slide_extends_grip_upward",
                ext is not None and (ext[0][2] + ext[1][2]) * 0.5 > (grip[0][2] + grip[1][2]) * 0.5 + 0.04,
                f"rest={grip!r}, ext={ext!r}",
            )

    # --- grass-collection mechanism articulates / is present ---
    if r.grass_collection == "side_discharge":
        chute_joint = model.get_articulation("chute_hinge")
        ctx.check(
            "chute_deflector_is_revolute",
            chute_joint.articulation_type == ArticulationType.REVOLUTE,
            f"type={chute_joint.articulation_type}",
        )
        chute = model.get_part("discharge_chute")
        closed = ctx.part_element_world_aabb(chute, elem="deflector")
        with ctx.pose({chute_joint: CHUTE_OPEN_UPPER}):
            opened = ctx.part_element_world_aabb(chute, elem="deflector")
        ctx.check(
            "chute_deflector_swings_open",
            closed is not None and opened is not None and abs(opened[1][2] - closed[1][2]) > 0.01,
            f"closed={closed!r}, opened={opened!r}",
        )
    elif r.grass_collection == "rear_bag":
        door_joint = model.get_articulation("discharge_door_hinge")
        ctx.check(
            "discharge_door_is_revolute",
            door_joint.articulation_type == ArticulationType.REVOLUTE,
            f"type={door_joint.articulation_type}",
        )
        door = model.get_part("discharge_door")
        closed = ctx.part_element_world_aabb(door, elem="flap")
        with ctx.pose({door_joint: 1.2}):
            opened = ctx.part_element_world_aabb(door, elem="flap")
        ctx.check(
            "discharge_door_swings_open",
            closed is not None and opened is not None and abs(opened[0][0] - closed[0][0]) > 0.01,
            f"closed={closed!r}, opened={opened!r}",
        )
        bag = ctx.part_element_world_aabb(deck, elem="bag_body")
        ctx.check("grass_bag_at_deck_rear", bag is not None and (bag[0][0] + bag[1][0]) * 0.5 < -0.2, f"bag={bag!r}")
    else:  # mulch_plug
        plug = ctx.part_element_world_aabb(deck, elem="mulching_plug")
        ctx.check(
            "mulching_plug_at_deck_rear",
            plug is not None and plug[0][0] < -0.15 and plug[1][0] > -0.30,
            f"plug={plug!r}",
        )

    # --- each axle stays engaged with its wheel hub along the lateral axis ---
    for (name, _wx, _side, _wz, _tw, _wr, _ww), wheel in zip(specs, wheels):
        ctx.expect_overlap(
            deck,
            wheel,
            axes="y",
            elem_a=f"{name}_axle",
            elem_b="hub",
            min_overlap=0.004,
            name=f"{name}_axle_engaged_in_hub",
        )

    return ctx.report()
