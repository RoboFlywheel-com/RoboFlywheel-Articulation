# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Modular procedural template for category ``skateboard``.

Root = ``deck`` (an X-elongated lofted maple/plastic board). Two metal trucks
(``front`` / ``rear``) hang off the deck bottom as parallel children. Each truck
is a short chain: ``{label}_baseplate`` (FIXED to the deck) -> ``{label}_hanger``
(REVOLUTE about a tilted kingpin axis, +/-15 deg lean) -> two
``{label}_wheel_{side}`` parts, each CONTINUOUS roll about the cross axle (Y).
Mounting bolt heads are inlined deck visuals (no joints) over a ``bolt_count``
multiplicity grid per truck.

Slots:
  A ``deck_outline`` {popsicle, oldschool, longboard, penny} -> _deck_mesh loft
  B ``truck_form``    {cast_kingpin, inverted_truck, wide_truck}
  C ``wheel_form``    {street_hard, cruiser_wheels, cored_wheels}
  mult ``bolt_count`` per-truck deck-top bolts (inlined deck visuals, no joint)

Geometry policy: faithfully adapts the 5-star sources' LoftGeometry deck,
WheelGeometry/TireGeometry wheels and LatheGeometry cored ring; nothing is
downgraded to plain Box/Cylinder where the source used a richer primitive.

5-star sources (``data/records/<rec>/revisions/rev_000001/model.py``):
  S0 parent rec_wooden-skateboard-...b6b31add  (all-slot baseline + joints)
  S1 rec_skateboard_var_oldschool / S2 longboard / S3 penny  (Slot A)
  S4 rec_skateboard_var_inverted_truck / S5 wide_truck       (Slot B)
  S6 rec_skateboard_var_cruiser_wheels / S7 cored_wheels     (Slot C)
  S8 rec_skateboard_var_bolts2 / S9 bolts6                   (multiplicity)

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Sports_Skateboard.md``
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
    BoxGeometry,
    CylinderGeometry,
    Inertial,
    LatheGeometry,
    LoftGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireShoulder,
    TireSidewall,
    TireTread,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    mesh_from_geometry,
    rounded_rect_profile,
)

__modular__ = True

DeckOutline = Literal["popsicle", "oldschool", "longboard", "penny"]
TruckForm = Literal["cast_kingpin", "inverted_truck", "wide_truck"]
WheelForm = Literal["street_hard", "cruiser_wheels", "cored_wheels"]
PaletteStyle = Literal[
    "maple_natural",
    "blue_plastic",
    "longboard_woody",
    "cruiser_pastel",
    "urethane_cored",
    "raw_metal_dark",
]

DECK_OUTLINES: tuple[DeckOutline, ...] = ("popsicle", "oldschool", "longboard", "penny")
TRUCK_FORMS: tuple[TruckForm, ...] = ("cast_kingpin", "inverted_truck", "wide_truck")
WHEEL_FORMS: tuple[WheelForm, ...] = ("street_hard", "cruiser_wheels", "cored_wheels")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "maple_natural",
    "blue_plastic",
    "longboard_woody",
    "cruiser_pastel",
    "urethane_cored",
    "raw_metal_dark",
)

BOLT_COUNTS: tuple[int, ...] = (2, 4, 6, 8)
BOLT_COUNT_WEIGHTS: tuple[float, ...] = (0.16, 0.46, 0.30, 0.08)

KINGPIN_TILT = math.radians(28.0)
DECK_BOTTOM = 0.0
BASEPLATE_THICK = 0.010
# Clearance kept between the wheel top and the deck bottom (z=0). The axle is
# dropped below the deck so the whole truck/wheel assembly hangs clear of the
# board: axle_z = -(wheel_radius + DECK_CLEAR).
DECK_CLEAR = 0.012
# The REVOLUTE kingpin pivot sits just below the deck/baseplate, inside the
# baseplate boss geometry (keeps the joint origin near both parent and child
# geometry). The hanger body+axle hang DOWN from this pivot to ``axle_z``.
PIVOT_Z = -0.018

# ---- palettes (rgba per material key, sampled from 5-star sources) ----
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "maple_natural": {
        "deck": (0.74, 0.58, 0.36, 1.0),
        "metal": (0.62, 0.64, 0.66, 1.0),
        "wheel": (0.86, 0.55, 0.27, 1.0),
        "bolt": (0.20, 0.20, 0.22, 1.0),
        "hub_core": (0.88, 0.88, 0.86, 1.0),
        "urethane": (0.82, 0.48, 0.22, 1.0),
    },
    "blue_plastic": {
        "deck": (0.15, 0.55, 0.78, 1.0),
        "metal": (0.62, 0.64, 0.66, 1.0),
        "wheel": (0.86, 0.55, 0.27, 1.0),
        "bolt": (0.18, 0.18, 0.20, 1.0),
        "hub_core": (0.90, 0.90, 0.88, 1.0),
        "urethane": (0.80, 0.46, 0.20, 1.0),
    },
    "longboard_woody": {
        "deck": (0.66, 0.50, 0.30, 1.0),
        "metal": (0.60, 0.62, 0.64, 1.0),
        "wheel": (0.83, 0.58, 0.32, 1.0),
        "bolt": (0.20, 0.20, 0.22, 1.0),
        "hub_core": (0.86, 0.86, 0.84, 1.0),
        "urethane": (0.80, 0.50, 0.24, 1.0),
    },
    "cruiser_pastel": {
        "deck": (0.78, 0.62, 0.40, 1.0),
        "metal": (0.66, 0.68, 0.70, 1.0),
        "wheel": (0.94, 0.66, 0.34, 1.0),
        "bolt": (0.22, 0.22, 0.24, 1.0),
        "hub_core": (0.92, 0.92, 0.90, 1.0),
        "urethane": (0.92, 0.60, 0.30, 1.0),
    },
    "urethane_cored": {
        "deck": (0.74, 0.58, 0.36, 1.0),
        "metal": (0.62, 0.64, 0.66, 1.0),
        "wheel": (0.84, 0.50, 0.24, 1.0),
        "bolt": (0.20, 0.20, 0.22, 1.0),
        "hub_core": (0.88, 0.88, 0.86, 1.0),
        "urethane": (0.82, 0.48, 0.22, 1.0),
    },
    "raw_metal_dark": {
        "deck": (0.70, 0.55, 0.34, 1.0),
        "metal": (0.34, 0.35, 0.37, 1.0),
        "wheel": (0.82, 0.54, 0.28, 1.0),
        "bolt": (0.14, 0.14, 0.16, 1.0),
        "hub_core": (0.80, 0.80, 0.78, 1.0),
        "urethane": (0.80, 0.46, 0.20, 1.0),
    },
}

# ---- per-outline deck constants (DECK_LEN, FRONT_X frac, DECK_WIDTH, DECK_THICK) ----
# (DECK_LEN, truck_x_frac, deck_width, deck_thick)
DECK_PARAMS: dict[DeckOutline, tuple[float, float, float, float]] = {
    # popsicle: FRONT_X 0.275 / half 0.40 -> frac 0.6875
    "popsicle": (0.80, 0.6875, 0.205, 0.012),
    # oldschool: same len / front_x 0.275
    "oldschool": (0.80, 0.6875, 0.230, 0.012),
    # longboard: len 1.10 / front_x 0.39 -> frac 0.709
    "longboard": (1.10, 0.7091, 0.240, 0.012),
    # penny: len 0.55 / front_x 0.19 -> frac 0.6909
    "penny": (0.55, 0.6909, 0.155, 0.015),
}

# Loft station tables (frac along half-length, half_width, centerline kick rise).
_DECK_RAW: dict[DeckOutline, list[tuple[float, float, float]]] = {
    "popsicle": [
        (-1.00, 0.030, 0.030),
        (-0.965, 0.060, 0.022),
        (-0.92, 0.085, 0.012),
        (-0.85, 0.097, 0.004),
        (-0.70, 0.1015, 0.0),
        (-0.40, 0.1025, 0.0),
        (0.0, 0.1025, 0.0),
        (0.40, 0.1025, 0.0),
        (0.70, 0.1015, 0.0),
        (0.85, 0.097, 0.004),
        (0.92, 0.085, 0.012),
        (0.965, 0.060, 0.022),
        (1.00, 0.030, 0.030),
    ],
    "oldschool": [
        (-1.00, 0.110, 0.048),
        (-0.96, 0.116, 0.038),
        (-0.90, 0.119, 0.022),
        (-0.82, 0.119, 0.008),
        (-0.72, 0.116, 0.0),
        (-0.58, 0.112, 0.0),
        (-0.42, 0.108, -0.001),
        (-0.25, 0.105, -0.001),
        (0.0, 0.103, -0.001),
        (0.20, 0.100, 0.0),
        (0.38, 0.094, 0.0),
        (0.52, 0.084, 0.0),
        (0.65, 0.070, 0.0),
        (0.78, 0.054, 0.0),
        (0.88, 0.038, 0.0),
        (0.95, 0.028, 0.0),
        (1.00, 0.022, 0.0),
    ],
    "longboard": [
        (-1.00, 0.012, 0.0),
        (-0.95, 0.025, 0.0),
        (-0.88, 0.042, 0.0),
        (-0.78, 0.062, 0.0),
        (-0.65, 0.082, 0.0),
        (-0.50, 0.098, 0.0),
        (-0.30, 0.110, 0.0),
        (-0.10, 0.117, 0.0),
        (0.10, 0.120, 0.0),
        (0.30, 0.120, 0.0),
        (0.50, 0.118, 0.0),
        (0.65, 0.112, 0.0),
        (0.80, 0.100, 0.0),
        (0.90, 0.082, 0.0),
        (0.96, 0.058, 0.0),
        (1.00, 0.035, 0.0),
    ],
    "penny": [
        (-1.00, 0.015, 0.028),
        (-0.94, 0.030, 0.022),
        (-0.88, 0.045, 0.014),
        (-0.82, 0.058, 0.006),
        (-0.76, 0.068, 0.001),
        (-0.68, 0.074, 0.0),
        (-0.50, 0.0775, 0.0),
        (-0.30, 0.0775, 0.0),
        (0.00, 0.0775, 0.0),
        (0.30, 0.0775, 0.0),
        (0.50, 0.0775, 0.0),
        (0.68, 0.074, 0.0),
        (0.76, 0.068, 0.0),
        (0.82, 0.058, 0.0),
        (0.88, 0.045, 0.0),
        (0.94, 0.030, 0.0),
        (1.00, 0.015, 0.0),
    ],
}

# Per-wheel-form nominal radius/width and the truck wheel-track each prefers.
# (wheel_radius, wheel_width)
_WHEEL_PARAMS: dict[WheelForm, tuple[float, float]] = {
    "street_hard": (0.0275, 0.034),
    "cruiser_wheels": (0.035, 0.050),
    "cored_wheels": (0.0275, 0.034),
}

# Per-truck nominal half-track (WHEEL_Y).
_TRUCK_TRACK: dict[TruckForm, float] = {
    "cast_kingpin": 0.092,
    "inverted_truck": 0.092,
    "wide_truck": 0.120,
}

NUM_SPOKES = 5


@dataclass(frozen=True)
class SkateboardConfig:
    deck_outline: DeckOutline | None = None
    truck_form: TruckForm | None = None
    wheel_form: WheelForm | None = None
    bolt_count: int = 4
    palette_style: PaletteStyle = "maple_natural"
    wheel_radius_scale: float = 1.0
    name: str = "skateboard"


@dataclass(frozen=True)
class ResolvedSkateboardConfig:
    deck_outline: DeckOutline
    truck_form: TruckForm
    wheel_form: WheelForm
    bolt_count: int
    palette_style: PaletteStyle
    name: str
    # derived geometry
    deck_len: float
    deck_width: float
    deck_thick: float
    front_x: float
    rear_x: float
    wheel_radius: float
    wheel_width: float
    wheel_y: float
    axle_z: float
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


# Extra ground/deck clearance (below z=0) the wheel top must keep even at the
# WORST kingpin lean, so a leaning truck never sweeps a wheel up into the deck.
DECK_LEAN_MARGIN = 0.007


def _required_axle_z(wheel_radius: float, wheel_y: float) -> float:
    """Lowest axle_z such that the wheel top clears the deck bottom (z=0) at any
    kingpin lean.

    A wheel centre sits at ``(0, +/-wheel_y, dz)`` relative to the kingpin pivot
    (``dz = axle_z - PIVOT_Z``) and swings about the tilted kingpin axis
    ``(+/-sin(theta), 0, cos(theta))`` over ``+/-15 deg``. Rotating the Y-offset
    centre about that axis lifts it; the highest wheel top over the lean range
    must stay ``DECK_LEAN_MARGIN`` below z=0. Solved in closed form (linear in
    ``axle_z``) and clamped so the truck never hangs higher than the nominal
    rest clearance.
    """
    theta = KINGPIN_TILT
    az = math.cos(theta)
    ax = math.sin(theta)
    nominal = -(wheel_radius + DECK_CLEAR)
    required = nominal
    for phi in (math.radians(15.0), -math.radians(15.0)):
        a_coef = math.cos(phi) + az * az * (1.0 - math.cos(phi))
        # worst-case upward contribution from the Y-offset centre swinging up
        rise = abs(ax * wheel_y * math.sin(phi))
        # PIVOT_Z + (axle_z - PIVOT_Z)*a_coef + rise + wheel_radius <= -margin
        rhs = -DECK_LEAN_MARGIN - PIVOT_Z - rise - wheel_radius
        axle_z_needed = PIVOT_Z + rhs / a_coef
        required = min(required, axle_z_needed)
    return required


def _clamp_int(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def _choice(value: str | None, allowed: tuple[str, ...], fallback: str, field: str) -> str:
    if value is None:
        return fallback
    if value not in allowed:
        raise ValueError(f"Unsupported {field}: {value}")
    return value


def config_from_seed(seed: int) -> SkateboardConfig:
    if seed == 0:
        return SkateboardConfig(
            deck_outline="popsicle",
            truck_form="cast_kingpin",
            wheel_form="street_hard",
            bolt_count=4,
            palette_style="maple_natural",
            wheel_radius_scale=1.0,
            name="skateboard",
        )
    rng = random.Random(seed)
    deck_outline = rng.choice(DECK_OUTLINES)
    truck_form = rng.choice(TRUCK_FORMS)
    # compatibility gate: penny x wide_truck -> wide track splays wheels past the
    # tiny deck rails, so fall back to a narrower truck.
    if deck_outline == "penny" and truck_form == "wide_truck":
        truck_form = rng.choice(("cast_kingpin", "inverted_truck"))
    wheel_form = rng.choice(WHEEL_FORMS)
    bolt_count = rng.choices(BOLT_COUNTS, weights=BOLT_COUNT_WEIGHTS, k=1)[0]
    palette_style = rng.choice(PALETTE_STYLES)
    wheel_radius_scale = rng.uniform(0.9, 1.3)
    return SkateboardConfig(
        deck_outline=deck_outline,
        truck_form=truck_form,
        wheel_form=wheel_form,
        bolt_count=bolt_count,
        palette_style=palette_style,
        wheel_radius_scale=round(wheel_radius_scale, 3),
        name=f"seeded_skateboard_{seed}",
    )


def resolve_config(config: SkateboardConfig) -> ResolvedSkateboardConfig:
    deck_outline = _choice(config.deck_outline, DECK_OUTLINES, "popsicle", "deck_outline")
    truck_form = _choice(config.truck_form, TRUCK_FORMS, "cast_kingpin", "truck_form")
    wheel_form = _choice(config.wheel_form, WHEEL_FORMS, "street_hard", "wheel_form")
    palette_style = _choice(config.palette_style, PALETTE_STYLES, "maple_natural", "palette_style")

    # compatibility gate (also enforced in config_from_seed): penny x wide_truck.
    if deck_outline == "penny" and truck_form == "wide_truck":
        truck_form = "cast_kingpin"

    bolt_count = _clamp_int(config.bolt_count, 2, 8)

    deck_len, truck_x_frac, deck_width, deck_thick = DECK_PARAMS[deck_outline]
    front_x = truck_x_frac * deck_len / 2.0
    rear_x = -front_x

    base_radius, wheel_width = _WHEEL_PARAMS[wheel_form]
    radius_scale = _clamp(config.wheel_radius_scale, 0.9, 1.3)
    wheel_radius = base_radius * radius_scale

    wheel_y = _TRUCK_TRACK[truck_form]

    # axle_z dropped below the deck so the wheel TOP clears the deck bottom even
    # at the worst kingpin lean (a leaning truck swings its Y-offset wheels up
    # toward the board). The four wheel bottoms share a common ground plane at
    # axle_z - wheel_radius.
    axle_z = _required_axle_z(wheel_radius, wheel_y)

    return ResolvedSkateboardConfig(
        deck_outline=deck_outline,
        truck_form=truck_form,
        wheel_form=wheel_form,
        bolt_count=bolt_count,
        palette_style=palette_style,
        name=config.name or "skateboard",
        deck_len=deck_len,
        deck_width=deck_width,
        deck_thick=deck_thick,
        front_x=front_x,
        rear_x=rear_x,
        wheel_radius=wheel_radius,
        wheel_width=wheel_width,
        wheel_y=wheel_y,
        axle_z=axle_z,
        palette=dict(PALETTES[palette_style]),
    )


def with_overrides(config: SkateboardConfig, **kwargs: object) -> SkateboardConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: SkateboardConfig | ResolvedSkateboardConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedSkateboardConfig) else resolve_config(config)
    return (
        ("deck_outline", r.deck_outline),
        ("truck_form", r.truck_form),
        ("wheel_form", r.wheel_form),
        ("bolt_count", f"{r.bolt_count}_per_truck"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ----------------------------------------------------------------------------
# deck loft (Slot A)
# ----------------------------------------------------------------------------
def _deck_mesh(r: ResolvedSkateboardConfig):
    half_len = r.deck_len / 2.0
    raw = _DECK_RAW[r.deck_outline]
    profiles = []
    for frac, half_w, kick in raw:
        z = frac * half_len
        w = max(half_w * 2.0, 0.006)
        prof2d = rounded_rect_profile(w, r.deck_thick, min(r.deck_thick * 0.45, half_w))
        loop = [(px, py + kick, z) for (px, py) in prof2d]
        profiles.append(loop)
    deck = LoftGeometry(profiles, cap=True, closed=True)
    deck.rotate_y(math.pi / 2.0)  # loft Z (length) -> +X
    deck.rotate_x(math.pi / 2.0)  # width -> Y, thickness -> Z (kick up +Z)
    deck.translate(0.0, 0.0, r.deck_thick / 2.0)  # flat bottom near z=0
    return mesh_from_geometry(deck, "deck_top")


def _bolt_mesh(name: str):
    head = CylinderGeometry(0.0045, 0.005)
    return mesh_from_geometry(head, name)


def _bolt_offsets(bolt_count: int) -> list[tuple[float, float]]:
    """Symmetric (dx, dy) grid of ``bolt_count`` heads centered on a truck.

    N=2 -> two along Y; otherwise a 2-column (X) x ceil(N/2)-row (Y) grid, which
    reproduces the parent 2x2 (N=4) and bolts6 2x3 (N=6) patterns.
    """
    bolt_dx = 0.030
    bolt_dy = 0.020
    if bolt_count <= 2:
        return [(0.0, -bolt_dy), (0.0, bolt_dy)][:bolt_count]
    rows = (bolt_count + 1) // 2
    offsets: list[tuple[float, float]] = []
    row_center = (rows - 1) / 2.0
    for i in range(bolt_count):
        col = i % 2
        row = i // 2
        sx = -1.0 if col == 0 else 1.0
        sy = row - row_center
        offsets.append((sx * bolt_dx, sy * bolt_dy))
    return offsets


def _build_deck(model: ArticulatedObject, r: ResolvedSkateboardConfig, mats: dict[str, object]):
    deck = model.part("deck")
    deck.visual(_deck_mesh(r), material=mats["deck"], name="deck_board", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style == "blue_plastic" else "wood.plywood"))

    offsets = _bolt_offsets(r.bolt_count)
    for label, tx in (("front", r.front_x), ("rear", r.rear_x)):
        for i, (dx, dy) in enumerate(offsets):
            deck.visual(
                _bolt_mesh(f"bolt_{label}_{i}"),
                origin=Origin(xyz=(tx + dx, dy, r.deck_thick + 0.001)),
                material=mats["bolt"],
                name=f"deck_bolt_{label}_{i}", material_class_id="metal.blackened_gunmetal",
            )

    deck.inertial = Inertial.from_geometry(
        Box((r.deck_len, r.deck_width, r.deck_thick)),
        mass=1.4,
        origin=Origin(xyz=(0.0, 0.0, r.deck_thick / 2.0)),
    )
    return deck


# ----------------------------------------------------------------------------
# trucks (Slot B): baseplate + hanger meshes per form
# ----------------------------------------------------------------------------
def _baseplate_mesh_cast(name: str):
    plate = BoxGeometry((0.075, 0.075, BASEPLATE_THICK))
    plate.translate(0.0, 0.0, -BASEPLATE_THICK / 2.0)
    boss = CylinderGeometry(0.011, 0.022)
    boss.translate(0.0, 0.0, -BASEPLATE_THICK - 0.006)
    plate.merge(boss)
    return mesh_from_geometry(plate, name)


def _baseplate_mesh_inverted(name: str, outboard_x: float):
    plate = BoxGeometry((0.080, 0.080, BASEPLATE_THICK))
    plate.translate(0.0, 0.0, -BASEPLATE_THICK / 2.0)
    boss = CylinderGeometry(0.012, 0.018)
    boss.translate(outboard_x, 0.0, -BASEPLATE_THICK - 0.009)
    plate.merge(boss)
    return mesh_from_geometry(plate, name)


def _baseplate_mesh_wide(name: str):
    plate = BoxGeometry((0.090, 0.088, BASEPLATE_THICK))
    plate.translate(0.0, 0.0, -BASEPLATE_THICK / 2.0)
    for angle in (0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0):
        rib = BoxGeometry((0.060, 0.006, 0.005))
        rib.translate(0.0, 0.0, -BASEPLATE_THICK - 0.0025)
        rib.rotate_z(angle)
        plate.merge(rib)
    boss = CylinderGeometry(0.014, 0.028)
    boss.translate(0.0, 0.0, -BASEPLATE_THICK - 0.008)
    plate.merge(boss)
    return mesh_from_geometry(plate, name)


# All hanger meshes are built in the HANGER frame whose origin is the kingpin
# PIVOT (near the deck/baseplate, local z=0). The cross-axle + wheel arms hang
# DOWN at local z = ``axle_local_z`` (negative); a neck reaches UP toward the
# baseplate boss so the REVOLUTE origin stays inside both bodies' geometry.
def _hanger_mesh_cast(name: str, r: ResolvedSkateboardConfig, axle_local_z: float):
    # pivot neck: short stub straddling local z=0 up toward the baseplate boss.
    neck = CylinderGeometry(0.010, 0.020)
    neck.translate(0.0, 0.0, 0.004)
    geo = neck
    # body slab sitting just above the axle.
    body = BoxGeometry((0.036, 0.052, 0.026))
    body.translate(0.0, 0.0, axle_local_z + 0.013)
    geo.merge(body)
    # downward spine connecting pivot neck to the axle body.
    spine = BoxGeometry((0.024, 0.030, abs(axle_local_z) + 0.014))
    spine.translate(0.0, 0.0, (axle_local_z + 0.006) / 2.0)
    geo.merge(spine)
    axle = CylinderGeometry(0.0065, r.wheel_y * 2.0 + r.wheel_width * 1.2)
    axle.rotate_x(math.pi / 2.0)
    axle.translate(0.0, 0.0, axle_local_z)
    geo.merge(axle)
    for s in (-1.0, 1.0):
        arm = BoxGeometry((0.024, r.wheel_y, 0.020))
        arm.translate(0.0, s * r.wheel_y / 2.0, axle_local_z)
        geo.merge(arm)
    return mesh_from_geometry(geo, name)


def _hanger_mesh_inverted(name: str, r: ResolvedSkateboardConfig, axle_local_z: float):
    # RKP: outboard pivot neck straddling local z=0.
    neck = CylinderGeometry(0.012, 0.024)
    neck.translate(0.0, 0.0, 0.004)
    geo = neck
    body_h = 0.028
    body = BoxGeometry((0.044, 0.058, body_h))
    body.translate(0.0, 0.0, axle_local_z + body_h / 2.0)
    geo.merge(body)
    spine = BoxGeometry((0.030, 0.034, abs(axle_local_z) + 0.014))
    spine.translate(0.0, 0.0, (axle_local_z + 0.006) / 2.0)
    geo.merge(spine)
    axle = CylinderGeometry(0.007, r.wheel_y * 2.0 + r.wheel_width * 1.2)
    axle.rotate_x(math.pi / 2.0)
    axle.translate(0.0, 0.0, axle_local_z)
    geo.merge(axle)
    arm_len = max(r.wheel_y - 0.025, 0.02)
    for s in (-1.0, 1.0):
        arm = BoxGeometry((0.028, arm_len, 0.024))
        arm.translate(0.0, s * arm_len / 2.0, axle_local_z)
        geo.merge(arm)
    return mesh_from_geometry(geo, name)


def _hanger_mesh_wide(name: str, r: ResolvedSkateboardConfig, axle_local_z: float):
    # gullwing: tall bushing crown reaching up to the pivot, wide wing axle below.
    neck = CylinderGeometry(0.009, 0.020)
    neck.translate(0.0, 0.0, 0.004)
    geo = neck
    crown = CylinderGeometry(0.019, 0.006)
    crown.translate(0.0, 0.0, -0.006)
    geo.merge(crown)
    bushing_seat = CylinderGeometry(0.016, 0.014)
    bushing_seat.translate(0.0, 0.0, -0.016)
    geo.merge(bushing_seat)
    spine = BoxGeometry((0.030, 0.040, abs(axle_local_z) + 0.014))
    spine.translate(0.0, 0.0, (axle_local_z + 0.006) / 2.0)
    geo.merge(spine)
    body = BoxGeometry((0.044, 0.072, 0.026))
    body.translate(0.0, 0.0, axle_local_z + 0.013)
    geo.merge(body)
    axle_len = r.wheel_y * 2.0 + r.wheel_width * 1.3
    axle = CylinderGeometry(0.007, axle_len)
    axle.rotate_x(math.pi / 2.0)
    axle.translate(0.0, 0.0, axle_local_z)
    geo.merge(axle)
    for s in (-1.0, 1.0):
        wing = BoxGeometry((0.034, r.wheel_y * 0.65, 0.024))
        wing.translate(0.0, s * r.wheel_y * 0.45, axle_local_z)
        geo.merge(wing)
        end_boss = CylinderGeometry(0.012, 0.028)
        end_boss.rotate_x(math.pi / 2.0)
        end_boss.translate(0.0, s * r.wheel_y, axle_local_z)
        geo.merge(end_boss)
    return mesh_from_geometry(geo, name)


# ----------------------------------------------------------------------------
# wheels (Slot C)
# ----------------------------------------------------------------------------
def _wheel_mesh_street(name: str, r: ResolvedSkateboardConfig):
    wheel = WheelGeometry(
        r.wheel_radius,
        r.wheel_width,
        rim=WheelRim(inner_radius=0.018, flange_height=0.003, flange_thickness=0.0025),
        hub=WheelHub(radius=0.009, width=0.030, cap_style="flat"),
        face=WheelFace(dish_depth=0.002, front_inset=0.001),
        bore=WheelBore(style="round", diameter=0.008),
    )
    wheel.rotate_z(math.pi / 2.0)
    return mesh_from_geometry(wheel, name)


def _tire_mesh_street(name: str, r: ResolvedSkateboardConfig):
    tire = TireGeometry(
        r.wheel_radius,
        r.wheel_width,
        inner_radius=0.020,
        tread=TireTread(style="circumferential", depth=0.0015, count=2),
        sidewall=TireSidewall(style="rounded", bulge=0.03),
    )
    tire.rotate_z(math.pi / 2.0)
    return mesh_from_geometry(tire, name)


def _wheel_mesh_cruiser(name: str, r: ResolvedSkateboardConfig):
    wheel = WheelGeometry(
        r.wheel_radius,
        r.wheel_width,
        rim=WheelRim(inner_radius=0.024, flange_height=0.004, flange_thickness=0.003),
        hub=WheelHub(radius=0.014, width=0.044, cap_style="flat"),
        face=WheelFace(dish_depth=0.003, front_inset=0.002),
        bore=WheelBore(style="round", diameter=0.010),
    )
    wheel.rotate_z(math.pi / 2.0)
    return mesh_from_geometry(wheel, name)


def _tire_mesh_cruiser(name: str, r: ResolvedSkateboardConfig):
    tire = TireGeometry(
        r.wheel_radius,
        r.wheel_width,
        inner_radius=0.024,
        carcass=TireCarcass(belt_width_ratio=0.70, sidewall_bulge=0.10),
        tread=TireTread(style="circumferential", depth=0.001, count=1),
        sidewall=TireSidewall(style="rounded", bulge=0.08),
        shoulder=TireShoulder(width=0.010, radius=0.008),
    )
    tire.rotate_z(math.pi / 2.0)
    return mesh_from_geometry(tire, name)


def _spoke_geo(inner_r: float, outer_r: float, axial_thick: float, tang_width: float):
    length = outer_r - inner_r
    geo = BoxGeometry((length, axial_thick, tang_width))
    geo.translate(inner_r + length / 2.0, 0.0, 0.0)
    return geo


def _hub_core_mesh(name: str, r: ResolvedSkateboardConfig):
    hub_radius = 0.009
    spoke_outer_r = max(0.019, r.wheel_radius * 0.69)
    spoke_axial = r.wheel_width * 0.72
    spoke_tang = 0.009
    hub = CylinderGeometry(hub_radius, spoke_axial, radial_segments=24)
    hub.rotate_x(math.pi / 2.0)
    for z_sign in (-1.0, 1.0):
        seat = CylinderGeometry(hub_radius + 0.003, 0.004, radial_segments=24)
        seat.rotate_x(math.pi / 2.0)
        seat.translate(0.0, z_sign * (spoke_axial / 2.0 - 0.002), 0.0)
        hub.merge(seat)
    for i in range(NUM_SPOKES):
        angle = 2.0 * math.pi * i / NUM_SPOKES
        spoke = _spoke_geo(hub_radius, spoke_outer_r, spoke_axial * 0.80, spoke_tang)
        spoke.rotate_y(angle)
        hub.merge(spoke)
    return mesh_from_geometry(hub, name)


def _urethane_ring_mesh(name: str, r: ResolvedSkateboardConfig):
    spoke_outer_r = max(0.019, r.wheel_radius * 0.69)
    r_in = spoke_outer_r - 0.0005
    r_out = r.wheel_radius
    hw = r.wheel_width / 2.0
    edge_r = 0.002
    profile = [
        (r_in, -hw),
        (r_out - edge_r, -hw),
        (r_out, -hw + edge_r),
        (r_out, hw - edge_r),
        (r_out - edge_r, hw),
        (r_in, hw),
    ]
    ring = LatheGeometry(profile, segments=48, closed=True)
    ring.rotate_x(math.pi / 2.0)
    return mesh_from_geometry(ring, name)


def _build_wheel(
    model: ArticulatedObject,
    name: str,
    r: ResolvedSkateboardConfig,
    mats: dict[str, object],
    side_sign: float,
):
    wheel = model.part(name)
    if r.wheel_form == "cored_wheels":
        wheel.visual(_hub_core_mesh(f"{name}_core", r), material=mats["hub_core"], name="hub_core", material_class_id="plastic.opaque_glossy_molded")
        wheel.visual(
            _urethane_ring_mesh(f"{name}_ring", r),
            material=mats["urethane"],
            name="urethane_ring", material_class_id="rubber.smooth_plain",
        )
    elif r.wheel_form == "cruiser_wheels":
        wheel.visual(
            _wheel_mesh_cruiser(f"{name}_rim", r), material=mats["metal"], name="wheel_rim", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "raw_metal_dark" else "metal.aluminum_bare")
        )
        wheel.visual(
            _tire_mesh_cruiser(f"{name}_tire", r), material=mats["wheel"], name="wheel_tire", material_class_id="rubber.directional_grooved"
        )
    else:  # street_hard
        wheel.visual(_wheel_mesh_street(f"{name}_rim", r), material=mats["metal"], name="wheel_rim", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "raw_metal_dark" else "metal.aluminum_bare"))
        wheel.visual(
            _tire_mesh_street(f"{name}_tire", r), material=mats["wheel"], name="wheel_tire", material_class_id="rubber.directional_grooved"
        )

    # roll marker: a short radial pip lying in the wheel's X/Z plane (the wheel
    # axis is Y), sitting in the OUTER third of the wheel (near the tread) so it
    # is always embedded in the solid rim/tire/urethane annulus and stays well
    # clear of ALL central hardware -- the cross-axle, the hanger arms and the
    # wide-truck end bosses (all within r<~0.014 of the spin axis). It is offset
    # outboard along the axle by ``side_sign`` so its whole body sits outboard of
    # the wheel centre plane and can never poke inboard into the hanger casting.
    mark_mid = r.wheel_radius * 0.84
    mark_len = r.wheel_radius * 0.24
    pip = BoxGeometry((0.0045, r.wheel_width * 0.55, mark_len))
    pip.translate(0.0, side_sign * r.wheel_width * 0.30, mark_mid)
    wheel.visual(mesh_from_geometry(pip, f"{name}_pip"), material=mats["bolt"], name="roll_marker", material_class_id="metal.blackened_gunmetal")

    wheel.inertial = Inertial.from_geometry(
        Box((r.wheel_width, r.wheel_radius * 2, r.wheel_radius * 2)), mass=0.06
    )
    return wheel


# ----------------------------------------------------------------------------
# truck assembly (baseplate FIXED -> hanger REVOLUTE -> 2 wheels CONTINUOUS)
# ----------------------------------------------------------------------------
def _build_truck(
    model: ArticulatedObject,
    deck,
    label: str,
    tx: float,
    tilt_sign: float,
    r: ResolvedSkateboardConfig,
    mats: dict[str, object],
) -> None:
    bp = model.part(f"{label}_baseplate")

    # The kingpin pivot sits at PIVOT_Z (inside the baseplate boss). The cross
    # axle hangs below at axle_z; in the hanger frame (origin = pivot) that is:
    axle_local_z = r.axle_z - PIVOT_Z

    if r.truck_form == "inverted_truck":
        boss_offset_x = 0.022
        outboard_x = tilt_sign * boss_offset_x
        bp.visual(
            _baseplate_mesh_inverted(f"{label}_plate", outboard_x),
            material=mats["metal"],
            name="baseplate", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "raw_metal_dark" else "metal.aluminum_bare"),
        )
        bp.inertial = Inertial.from_geometry(
            Box((0.080, 0.080, 0.030)), mass=0.11, origin=Origin(xyz=(0.0, 0.0, -0.012))
        )
        hanger = model.part(f"{label}_hanger")
        hanger.visual(
            _hanger_mesh_inverted(f"{label}_hanger_body", r, axle_local_z),
            material=mats["metal"],
            name="hanger", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "raw_metal_dark" else "metal.aluminum_bare"),
        )
        hanger.inertial = Inertial.from_geometry(
            Box((0.044, r.wheel_y * 2.0, abs(axle_local_z) + 0.03)),
            mass=0.22,
            origin=Origin(xyz=(0.0, 0.0, axle_local_z / 2.0)),
        )
        # RKP: axis tilts the opposite way (inward), pivot moves outboard.
        kp_axis = (-tilt_sign * math.sin(KINGPIN_TILT), 0.0, math.cos(KINGPIN_TILT))
        joint_origin = Origin(xyz=(outboard_x, 0.0, PIVOT_Z))
    else:
        if r.truck_form == "wide_truck":
            bp.visual(
                _baseplate_mesh_wide(f"{label}_plate"), material=mats["metal"], name="baseplate", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "raw_metal_dark" else "metal.aluminum_bare")
            )
            hanger_mesh = _hanger_mesh_wide(f"{label}_hanger_body", r, axle_local_z)
            bp_size = (0.090, 0.088, 0.030)
        else:  # cast_kingpin
            bp.visual(
                _baseplate_mesh_cast(f"{label}_plate"), material=mats["metal"], name="baseplate", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "raw_metal_dark" else "metal.aluminum_bare")
            )
            hanger_mesh = _hanger_mesh_cast(f"{label}_hanger_body", r, axle_local_z)
            bp_size = (0.075, 0.075, 0.030)
        bp.inertial = Inertial.from_geometry(
            Box(bp_size), mass=0.10, origin=Origin(xyz=(0.0, 0.0, -0.012))
        )
        hanger = model.part(f"{label}_hanger")
        hanger.visual(hanger_mesh, material=mats["metal"], name="hanger", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "raw_metal_dark" else "metal.aluminum_bare"))
        hanger.inertial = Inertial.from_geometry(
            Box((0.04, r.wheel_y * 2.0, abs(axle_local_z) + 0.03)),
            mass=0.18,
            origin=Origin(xyz=(0.0, 0.0, axle_local_z / 2.0)),
        )
        kp_axis = (tilt_sign * math.sin(KINGPIN_TILT), 0.0, math.cos(KINGPIN_TILT))
        joint_origin = Origin(xyz=(0.0, 0.0, PIVOT_Z))

    wheel_local_z = axle_local_z

    model.articulation(
        f"deck_to_{label}_baseplate",
        ArticulationType.FIXED,
        parent=deck,
        child=bp,
        origin=Origin(xyz=(tx, 0.0, DECK_BOTTOM)),
    )
    model.articulation(
        f"{label}_baseplate_to_hanger",
        ArticulationType.REVOLUTE,
        parent=bp,
        child=hanger,
        origin=joint_origin,
        axis=kp_axis,
        motion_limits=MotionLimits(
            effort=8.0,
            velocity=4.0,
            lower=-math.radians(15.0),
            upper=math.radians(15.0),
        ),
    )

    for s, side in ((-1.0, "0"), (1.0, "1")):
        wheel = _build_wheel(model, f"{label}_wheel_{side}", r, mats, s)
        model.articulation(
            f"{label}_hanger_to_wheel_{side}",
            ArticulationType.CONTINUOUS,
            parent=hanger,
            child=wheel,
            origin=Origin(xyz=(0.0, s * r.wheel_y, wheel_local_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=30.0),
        )


def build_skateboard(
    config: SkateboardConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or SkateboardConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"skate_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in r.palette.items()
    }

    deck = _build_deck(model, r, mats)
    _build_truck(model, deck, "front", r.front_x, 1.0, r, mats)
    _build_truck(model, deck, "rear", r.rear_x, -1.0, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_skateboard(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_skateboard(config_from_seed(seed), assets=assets)


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _allow_seated_overlaps(ctx: TestContext, r: ResolvedSkateboardConfig) -> None:
    for label in ("front", "rear"):
        ctx.allow_overlap(
            f"{label}_baseplate",
            "deck",
            elem_a="baseplate",
            elem_b="deck_board",
            reason="Baseplate is bolted flush against the deck bottom.",
        )
        ctx.expect_contact(f"{label}_baseplate", "deck", name=f"{label} baseplate seated on deck")
        ctx.allow_overlap(
            f"{label}_hanger",
            f"{label}_baseplate",
            elem_a="hanger",
            elem_b="baseplate",
            reason="Hanger pivot neck is captured by the baseplate kingpin boss.",
        )
        for side in ("0", "1"):
            wheel = f"{label}_wheel_{side}"
            if r.wheel_form == "cored_wheels":
                ctx.allow_overlap(
                    wheel,
                    f"{label}_hanger",
                    elem_a="hub_core",
                    elem_b="hanger",
                    reason="Cored wheel hub seats on the hanger cross-axle.",
                )
                ctx.allow_overlap(
                    wheel,
                    wheel,
                    elem_a="urethane_ring",
                    elem_b="hub_core",
                    reason="Urethane ring is bonded onto the hub core.",
                )
            else:
                ctx.allow_overlap(
                    wheel,
                    f"{label}_hanger",
                    elem_a="wheel_rim",
                    elem_b="hanger",
                    reason="Wheel is seated on the hanger cross-axle (axle runs through the bore).",
                )


def run_skateboard_tests(object_model: ArticulatedObject, config: SkateboardConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_seated_overlaps(ctx, r)

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.02)

    deck = object_model.get_part("deck")

    # ---- deck longer than wide ----
    dext = _ext(ctx.part_world_aabb(deck))
    ctx.check("deck longer than wide", dext[0] > dext[1] + 0.25, details=f"deck extents={dext}")

    # ---- four wheels rest on a common ground plane ----
    wheel_bottoms = []
    for label in ("front", "rear"):
        for side in ("0", "1"):
            w = object_model.get_part(f"{label}_wheel_{side}")
            wheel_bottoms.append(ctx.part_world_aabb(w)[0][2])
    zmin = min(wheel_bottoms)
    zmax = max(wheel_bottoms)
    ctx.check(
        "board rests on four wheels (coplanar wheel bottoms)",
        (zmax - zmin) < 0.006,
        details=f"wheel bottoms={[round(z, 4) for z in wheel_bottoms]}",
    )
    deck_zmin = ctx.part_world_aabb(deck)[0][2]
    ctx.check(
        "wheels are the lowest part of the assembly",
        zmin < deck_zmin - 0.04,
        details=f"wheel zmin={zmin:.4f}, deck zmin={deck_zmin:.4f}",
    )

    # ---- trucks symmetric front/back ----
    fbp = ctx.part_world_position(object_model.get_part("front_baseplate"))
    rbp = ctx.part_world_position(object_model.get_part("rear_baseplate"))
    ctx.check(
        "two trucks symmetric front/back",
        abs(fbp[0] + rbp[0]) < 0.01 and abs(fbp[0]) > 0.15,
        details=f"front_x={fbp[0]:.3f}, rear_x={rbp[0]:.3f}",
    )

    # ---- kingpin REVOLUTE lean (axle tips) ----
    for label in ("front", "rear"):
        hanger = object_model.get_part(f"{label}_hanger")
        kp = object_model.get_articulation(f"{label}_baseplate_to_hanger")
        ctx.check(
            f"{label} kingpin is revolute",
            kp.articulation_type == ArticulationType.REVOLUTE,
        )
        rest_ext = _ext(ctx.part_world_aabb(hanger))
        with ctx.pose({kp: math.radians(15.0)}):
            leaned_ext = _ext(ctx.part_world_aabb(hanger))
        ctx.check(
            f"{label} hanger leans about kingpin (axle tips)",
            leaned_ext[2] > rest_ext[2] + 0.003,
            details=f"{label} rest_z={rest_ext[2]:.4f} leaned_z={leaned_ext[2]:.4f}",
        )

    # ---- four wheels roll (marker moves) ----
    wheel_parts = []
    for label in ("front", "rear"):
        for side in ("0", "1"):
            wheel = object_model.get_part(f"{label}_wheel_{side}")
            wheel_parts.append(wheel)
            roll = object_model.get_articulation(f"{label}_hanger_to_wheel_{side}")
            ctx.check(
                f"{label} wheel {side} continuous",
                roll.articulation_type == ArticulationType.CONTINUOUS,
            )
            ctx.check(
                f"{label} wheel {side} axis Y",
                tuple(roll.axis) == (0.0, 1.0, 0.0),
                details=str(roll.axis),
            )
            pip0 = ctx.part_element_world_aabb(wheel, elem="roll_marker")
            c0 = ((pip0[0][0] + pip0[1][0]) / 2.0, (pip0[0][2] + pip0[1][2]) / 2.0)
            with ctx.pose({roll: math.pi / 2.0}):
                pip1 = ctx.part_element_world_aabb(wheel, elem="roll_marker")
                c1 = ((pip1[0][0] + pip1[1][0]) / 2.0, (pip1[0][2] + pip1[1][2]) / 2.0)
            moved = math.hypot(c1[0] - c0[0], c1[1] - c0[1])
            ctx.check(
                f"{label} wheel {side} rolls about axle (marker moves)",
                moved > 0.01,
                details=f"marker moved {moved:.4f} m",
            )
    ctx.check("exactly four wheels", len(wheel_parts) == 4, details=f"{len(wheel_parts)}")

    # ---- bolt multiplicity ----
    bolt_names = [v.name for v in deck.visuals if v.name.startswith("deck_bolt_")]
    ctx.check(
        "bolt multiplicity",
        len(bolt_names) == r.bolt_count * 2,
        details=f"expected {r.bolt_count * 2}, got {len(bolt_names)}",
    )

    # ---- cored wheel has both visuals ----
    if r.wheel_form == "cored_wheels":
        cw = object_model.get_part("front_wheel_0")
        names = {v.name for v in cw.visuals}
        ctx.check(
            "cored wheel has hub_core + urethane_ring",
            "hub_core" in names and "urethane_ring" in names,
            details=str(sorted(names)),
        )

    # ---- slot choices recorded ----
    expected_slots = dict(slot_choices_for_config(r))
    recorded = dict(object_model.meta.get("slot_choices", ()))
    ctx.check(
        "slot_choices_recorded",
        recorded == expected_slots,
        details=f"{recorded} vs {expected_slots}",
    )

    return ctx.report()


__all__ = [
    "SkateboardConfig",
    "ResolvedSkateboardConfig",
    "build_seeded_skateboard",
    "build_skateboard",
    "config_from_seed",
    "resolve_config",
    "run_skateboard_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
