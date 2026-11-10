# SPDX-License-Identifier: Apache-2.0

"""Bird cage — modular procedural template.

Mixed topology: a single grounded ``cage`` root (barred/wire enclosure + roof +
base/support + interior perches, all non-articulating and fused as visuals per
Rule 1) carries an independently articulated access opening (``door`` / a
``roof_hatch``) and, for hinge doors, a small rotating ``latch``.

Slots (exported via ``slot_choices_for_seed``):

* Slot A ``body_form``      — ③ primary form family (box barrel-vault / flat-top
  / gable, or round dome / hexagonal prism).
* Slot B ``door_mechanism`` — ② joint/mechanism (side hinge, bottom drop-front,
  vertical guillotine slide, top-lift roof hatch).
* Slot C ``support_base``   — ① support skeleton (rolling caster tray, four-leg
  floor stand, footed tabletop tray + hook, hanging bail).
* Slot D ``interior``       — N multiplicity (1/2/3 perches, optional 2 feeders).

Sources (5-star): box family adapts
``rec_use-the-attached-reference-image-picture-pet-ani_...291ba037`` (barrel
box) + forks flat_top / roof_gable / mechanism_dropfront / mechanism_slidedoor /
mechanism_topopen / support_legstand / n3_perch / accessory_feedcups /
n_bars_coarse; round family adapts
``rec_pet_animal_related__bird_cage__001_...`` (domed round) + forks
skeleton_hexagon / support_hanging.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    CylinderGeometry,
    Inertial,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True


# --------------------------------------------------------------------------- #
# Slot module vocabularies
# --------------------------------------------------------------------------- #
BodyForm = Literal[
    "barrel_vault_box",
    "flat_top_box",
    "gable_box",
    "dome_round",
    "hex_prism",
]
DoorMechanism = Literal["side_hinge", "drop_front", "slide_door", "top_hatch"]
SupportBase = Literal["caster_tray", "leg_stand", "footed_tray", "hanging_bail"]
Interior = Literal["perch1", "perch2", "perch3", "perch2_feed2", "perch3_feed2"]
BarDensity = Literal["dense", "coarse"]
PaletteTheme = Literal["black_powder", "aged_brass", "white_coat"]

BODY_FORMS: tuple[BodyForm, ...] = (
    "barrel_vault_box",
    "flat_top_box",
    "gable_box",
    "dome_round",
    "hex_prism",
)
BOX_FORMS = ("barrel_vault_box", "flat_top_box", "gable_box")
ROUND_FORMS = ("dome_round", "hex_prism")

DOOR_MECHANISMS: tuple[DoorMechanism, ...] = (
    "side_hinge",
    "drop_front",
    "slide_door",
    "top_hatch",
)
SUPPORT_BASES: tuple[SupportBase, ...] = (
    "caster_tray",
    "leg_stand",
    "footed_tray",
    "hanging_bail",
)
INTERIORS: tuple[Interior, ...] = (
    "perch1",
    "perch2",
    "perch3",
    "perch2_feed2",
    "perch3_feed2",
)

# Compatibility gating (source-faithful): box forks own the box doors/supports;
# the domed/hex mesh forms own the round doors/supports. Enforced in
# ``config_from_seed`` so every reachable seed (and corner seed) is legal.
BOX_DOORS = ("side_hinge", "drop_front", "slide_door")
ROUND_DOORS = ("side_hinge",)
BOX_SUPPORTS = ("caster_tray", "leg_stand")
ROUND_SUPPORTS = ("footed_tray", "hanging_bail")
BOX_INTERIORS = INTERIORS
ROUND_INTERIORS = ("perch1", "perch2", "perch3")


def _compatible_doors(body: str) -> tuple[str, ...]:
    if body == "flat_top_box":
        return BOX_DOORS + ("top_hatch",)  # only the flat rim can host a hatch
    if body in BOX_FORMS:
        return BOX_DOORS
    return ROUND_DOORS


def _compatible_supports(body: str) -> tuple[str, ...]:
    return BOX_SUPPORTS if body in BOX_FORMS else ROUND_SUPPORTS


def _compatible_interiors(body: str) -> tuple[str, ...]:
    return BOX_INTERIORS if body in BOX_FORMS else ROUND_INTERIORS


PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "black_powder": {
        "bar": (0.02, 0.02, 0.022, 1.0),
        "tray": (0.03, 0.028, 0.025, 1.0),
        "wood": (0.72, 0.54, 0.34, 1.0),
        "accent": (0.45, 0.45, 0.42, 1.0),
        "wheel": (0.02, 0.02, 0.02, 1.0),
        "cup": (0.60, 0.60, 0.62, 1.0),
    },
    "aged_brass": {
        "bar": (0.73, 0.48, 0.22, 1.0),
        "tray": (0.38, 0.24, 0.12, 1.0),
        "wood": (0.48, 0.29, 0.13, 1.0),
        "accent": (0.55, 0.40, 0.20, 1.0),
        "wheel": (0.06, 0.05, 0.05, 1.0),
        "cup": (0.70, 0.55, 0.30, 1.0),
    },
    "white_coat": {
        "bar": (0.90, 0.90, 0.92, 1.0),
        "tray": (0.83, 0.83, 0.85, 1.0),
        "wood": (0.72, 0.54, 0.34, 1.0),
        "accent": (0.58, 0.58, 0.60, 1.0),
        "wheel": (0.10, 0.10, 0.10, 1.0),
        "cup": (0.80, 0.80, 0.82, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class BirdCageConfig:
    body_form: BodyForm | None = None
    door_mechanism: DoorMechanism | None = None
    support_base: SupportBase | None = None
    interior: Interior | None = None
    bar_density: BarDensity = "dense"
    palette_theme: PaletteTheme = "black_powder"
    width_scale: float = 1.0
    height_scale: float = 1.0
    door_frac: float = 0.48


@dataclass(frozen=True)
class ResolvedBirdCageConfig:
    body_form: BodyForm
    door_mechanism: DoorMechanism
    support_base: SupportBase
    interior: Interior
    bar_density: BarDensity
    palette_theme: PaletteTheme
    width_scale: float
    height_scale: float
    door_frac: float
    # derived
    family: str  # "box" | "round"
    faceted: bool
    palette: dict[str, tuple[float, float, float, float]]
    # box body dims (also filled with sensible values for round for tests)
    half_w: float
    half_d: float
    front_y: float
    back_y: float
    bottom_z: float
    spring_z: float
    top_z: float
    # round body dims
    cage_r: float
    straight_z0: float
    straight_z1: float
    dome_z: float
    # aperture (front-face rectangular opening)
    door_w: float
    door_bottom_z: float
    door_h: float
    door_top_z: float
    door_x_min: float
    door_x_max: float
    # interior perch span/heights
    perch_x0: float
    perch_x1: float
    n_perches: int
    n_feed_cups: int


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


_PERCH_N = {"perch1": 1, "perch2": 2, "perch3": 3, "perch2_feed2": 2, "perch3_feed2": 3}
_FEED_N = {"perch1": 0, "perch2": 0, "perch3": 0, "perch2_feed2": 2, "perch3_feed2": 2}


def config_from_seed(seed: int) -> BirdCageConfig:
    """Deterministic procedural sampling. seed 0 is NOT special-cased."""
    rng = random.Random(seed)
    body = rng.choice(BODY_FORMS)
    door = rng.choice(_compatible_doors(body))
    support = rng.choice(_compatible_supports(body))
    interior = rng.choice(_compatible_interiors(body))
    return BirdCageConfig(
        body_form=body,  # type: ignore[arg-type]
        door_mechanism=door,  # type: ignore[arg-type]
        support_base=support,  # type: ignore[arg-type]
        interior=interior,  # type: ignore[arg-type]
        bar_density=rng.choice(("dense", "coarse")),  # type: ignore[arg-type]
        palette_theme=rng.choice(tuple(PALETTES.keys())),  # type: ignore[arg-type]
        width_scale=round(rng.uniform(0.86, 1.16), 4),
        height_scale=round(rng.uniform(0.86, 1.18), 4),
        door_frac=round(rng.uniform(0.44, 0.58), 4),
    )


def resolve_config(config: BirdCageConfig) -> ResolvedBirdCageConfig:
    body = config.body_form or "barrel_vault_box"
    if body not in BODY_FORMS:
        raise ValueError(f"Unsupported body_form: {body!r}")
    family = "box" if body in BOX_FORMS else "round"
    faceted = body == "hex_prism"

    door = config.door_mechanism or _compatible_doors(body)[0]
    support = config.support_base or _compatible_supports(body)[0]
    interior = config.interior or _compatible_interiors(body)[0]
    if door not in _compatible_doors(body):
        raise ValueError(f"door {door!r} incompatible with body {body!r}")
    if support not in _compatible_supports(body):
        raise ValueError(f"support {support!r} incompatible with body {body!r}")
    if interior not in _compatible_interiors(body):
        raise ValueError(f"interior {interior!r} incompatible with body {body!r}")
    if config.palette_theme not in PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme!r}")
    if config.bar_density not in ("dense", "coarse"):
        raise ValueError(f"Unsupported bar_density: {config.bar_density!r}")

    ws = _clamp(config.width_scale, 0.80, 1.22)
    hs = _clamp(config.height_scale, 0.80, 1.24)
    df = _clamp(config.door_frac, 0.40, 0.62)

    # Box dims
    W = 0.76 * ws
    D = 0.52 * ws
    half_w = W / 2.0
    half_d = D / 2.0
    front_y_box = -half_d
    back_y = half_d
    bottom_z = 0.23
    spring_z = bottom_z + 1.20 * hs

    # Round dims
    cage_r = 0.215 * ws
    straight_z0 = 0.075
    straight_z1 = straight_z0 + 0.393 * hs
    dome_z = straight_z1 + 0.252 * (0.6 + 0.4 * ws)

    if family == "box":
        front_y = front_y_box
        door_w = _clamp(df * W, 0.26, W - 0.16)
        door_x_min = -door_w / 2.0
        door_x_max = door_w / 2.0
        door_bottom_z = bottom_z + 0.16
        door_h = _clamp(0.58 * hs, 0.30, spring_z - door_bottom_z - 0.10)
        door_top_z = door_bottom_z + door_h
        perch_x0 = -half_w - 0.006
        perch_x1 = half_w + 0.006
        top_z = spring_z + (half_w if body == "barrel_vault_box" else 0.0)
        if body == "gable_box":
            top_z = spring_z + 0.35 * hs
        elif body == "flat_top_box":
            top_z = spring_z
    else:
        front_dist = cage_r * math.cos(math.pi / 6.0) if faceted else cage_r
        front_y = -front_dist
        door_w = _clamp(0.130 * ws, 0.10, 2.0 * front_dist - 0.06)
        door_x_min = -door_w / 2.0
        door_x_max = door_w / 2.0
        door_h = _clamp(0.205 * hs, 0.12, straight_z1 - straight_z0 - 0.03)
        door_bottom_z = (straight_z0 + straight_z1) / 2.0 - door_h / 2.0
        door_top_z = door_bottom_z + door_h
        perch_x0 = -cage_r - 0.006
        perch_x1 = cage_r + 0.006
        top_z = dome_z + 0.13
        # keep box fields consistent for generic tests
        half_w = cage_r
        half_d = cage_r
        back_y = cage_r
        bottom_z = straight_z0
        spring_z = straight_z1

    return ResolvedBirdCageConfig(
        body_form=body,  # type: ignore[arg-type]
        door_mechanism=door,  # type: ignore[arg-type]
        support_base=support,  # type: ignore[arg-type]
        interior=interior,  # type: ignore[arg-type]
        bar_density=config.bar_density,
        palette_theme=config.palette_theme,
        width_scale=ws,
        height_scale=hs,
        door_frac=df,
        family=family,
        faceted=faceted,
        palette=dict(PALETTES[config.palette_theme]),
        half_w=half_w,
        half_d=half_d,
        front_y=front_y,
        back_y=back_y,
        bottom_z=bottom_z,
        spring_z=spring_z,
        top_z=top_z,
        cage_r=cage_r,
        straight_z0=straight_z0,
        straight_z1=straight_z1,
        dome_z=dome_z,
        door_w=door_w,
        door_bottom_z=door_bottom_z,
        door_h=door_h,
        door_top_z=door_top_z,
        door_x_min=door_x_min,
        door_x_max=door_x_max,
        perch_x0=perch_x0,
        perch_x1=perch_x1,
        n_perches=_PERCH_N[interior],
        n_feed_cups=_FEED_N[interior],
    )


# --------------------------------------------------------------------------- #
# Rod helpers (Box/Cylinder visual vocabulary — origin A family)
# --------------------------------------------------------------------------- #
def _rod_rpy(dx: float, dy: float, dz: float) -> tuple[float, float, float]:
    if abs(dy) < 1e-9:
        return (0.0, math.atan2(dx, dz), 0.0)
    if abs(dx) < 1e-9 and abs(dz) < 1e-9:
        return (math.pi / 2.0, 0.0, 0.0)
    yaw = math.atan2(dy, dx)
    horiz = math.hypot(dx, dy)
    pitch = math.atan2(horiz, dz)
    return (0.0, pitch, yaw)


def _add_rod(
    part: Part,
    name: str,
    p0: tuple[float, float, float],
    p1: tuple[float, float, float],
    *,
    radius: float = 0.0045,
    material: str = "bar",
    end_pad: float = 0.0015,
) -> None:
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 1e-6:
        return
    part.visual(
        Cylinder(radius=radius, length=length + 2.0 * end_pad),
        origin=Origin(
            xyz=((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0, (p0[2] + p1[2]) / 2.0),
            rpy=_rod_rpy(dx, dy, dz),
        ),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _add_arch(
    part: Part,
    prefix: str,
    *,
    center_x: float,
    y: float,
    spring_z: float,
    radius: float,
    segments: int = 16,
    rod_radius: float = 0.0055,
    material: str = "bar",
) -> None:
    last = None
    for i in range(segments + 1):
        theta = math.pi - (math.pi * i / segments)
        p = (center_x + radius * math.cos(theta), y, spring_z + radius * math.sin(theta))
        if last is not None:
            _add_rod(part, f"{prefix}_{i:02d}", last, p, radius=rod_radius, material=material)
        last = p


# --------------------------------------------------------------------------- #
# Mesh helpers (round/hex family — origin B vocabulary)
# --------------------------------------------------------------------------- #
def _mrod_z(radius: float, length: float, center: tuple[float, float, float], seg: int = 12) -> MeshGeometry:
    return CylinderGeometry(radius=radius, height=length, radial_segments=seg).translate(*center)


def _mrod_x(radius: float, length: float, center: tuple[float, float, float], seg: int = 12) -> MeshGeometry:
    return CylinderGeometry(radius=radius, height=length, radial_segments=seg).rotate_y(math.pi / 2.0).translate(*center)


def _mtube(p0: tuple[float, float, float], p1: tuple[float, float, float], tube_r: float) -> MeshGeometry:
    return tube_from_spline_points([p0, p1], radius=tube_r, samples_per_segment=2, radial_segments=10, cap_ends=True)


def _merge(parts: list[MeshGeometry]) -> MeshGeometry:
    merged = MeshGeometry()
    for p in parts:
        merged.merge(p)
    return merged


# --------------------------------------------------------------------------- #
# Slot A: body_form — builds the ``cage`` root enclosure + roof, cuts aperture
# --------------------------------------------------------------------------- #
def _box_counts(r: ResolvedBirdCageConfig) -> tuple[int, int]:
    """(front/back verticals per face, side verticals) for dense/coarse."""
    return (13, 9) if r.bar_density == "dense" else (7, 5)


def _build_box_body(model: ArticulatedObject, r: ResolvedBirdCageConfig) -> Part:
    cage = model.part("cage")
    half_w, half_d = r.half_w, r.half_d
    front_y, back_y = r.front_y, r.back_y
    bottom_z, spring_z = r.bottom_z, r.spring_z
    rod_r, rail_r = 0.0045, 0.006
    n_face, n_side = _box_counts(r)

    # Bottom + top rectangular rails.
    for z, label in ((bottom_z, "bottom"), (spring_z, "spring")):
        _add_rod(cage, f"{label}_front_rail", (-half_w, front_y, z), (half_w, front_y, z), radius=rail_r)
        _add_rod(cage, f"{label}_rear_rail", (-half_w, back_y, z), (half_w, back_y, z), radius=rail_r)
        _add_rod(cage, f"{label}_side_rail_0", (-half_w, front_y, z), (-half_w, back_y, z), radius=rail_r)
        _add_rod(cage, f"{label}_side_rail_1", (half_w, front_y, z), (half_w, back_y, z), radius=rail_r)

    # Corner posts.
    for ix, x in enumerate((-half_w, half_w)):
        for iy, y in enumerate((front_y, back_y)):
            _add_rod(cage, f"corner_post_{ix}_{iy}", (x, y, bottom_z), (x, y, spring_z), radius=rail_r)

    # Side walls.
    side_y_values = [front_y + i * ((back_y - front_y) / (n_side - 1)) for i in range(n_side)]
    side_z_values = [bottom_z + (spring_z - bottom_z) * f for f in (0.14, 0.38, 0.62, 0.86)] + [spring_z]
    for side_i, x in enumerate((-half_w, half_w)):
        for i, y in enumerate(side_y_values):
            _add_rod(cage, f"side_vertical_{side_i}_{i}", (x, y, bottom_z), (x, y, spring_z), radius=rod_r)
        for i, z in enumerate(side_z_values):
            _add_rod(cage, f"side_horizontal_{side_i}_{i}", (x, front_y, z), (x, back_y, z), radius=rod_r)

    # Back wall grid.
    back_x_values = [-half_w + 0.03 + i * ((2 * half_w - 0.06) / (n_face - 1)) for i in range(n_face)]
    for i, x in enumerate(back_x_values):
        _add_rod(cage, f"rear_vertical_{i}", (x, back_y, bottom_z), (x, back_y, spring_z), radius=rod_r)
    for i, z in enumerate(side_z_values):
        _add_rod(cage, f"rear_horizontal_{i}", (-half_w, back_y, z), (half_w, back_y, z), radius=rod_r)

    # Front face. When the access opening is a roof hatch the front stays a full
    # grid; otherwise cut the door aperture (slide clears to the spring rail).
    if r.door_mechanism == "top_hatch":
        for i, x in enumerate(back_x_values):
            _add_rod(cage, f"front_vertical_{i}", (x, front_y, bottom_z), (x, front_y, spring_z), radius=rod_r)
        for i, z in enumerate(side_z_values):
            _add_rod(cage, f"front_full_rail_{i}", (-half_w, front_y, z), (half_w, front_y, z), radius=rod_r)
        _build_box_roof(cage, r, rod_r, rail_r)
        return cage

    dxmin, dxmax = r.door_x_min, r.door_x_max
    cut_top = spring_z if r.door_mechanism == "slide_door" else r.door_top_z
    for i, x in enumerate(back_x_values):
        if dxmin - 0.006 < x < dxmax + 0.006:
            _add_rod(cage, f"front_lower_short_{i}", (x, front_y, bottom_z), (x, front_y, r.door_bottom_z - 0.018), radius=rod_r)
            if cut_top < spring_z - 0.01:
                _add_rod(cage, f"front_upper_short_{i}", (x, front_y, cut_top + 0.05), (x, front_y, spring_z), radius=rod_r)
        else:
            _add_rod(cage, f"front_vertical_{i}", (x, front_y, bottom_z), (x, front_y, spring_z), radius=rod_r)
    # Split front horizontal rails around the aperture.
    for i, z in enumerate(side_z_values):
        if r.door_bottom_z - 0.02 < z < cut_top + 0.02:
            _add_rod(cage, f"front_left_split_{i}", (-half_w, front_y, z), (dxmin - 0.02, front_y, z), radius=rod_r)
            _add_rod(cage, f"front_right_split_{i}", (dxmax + 0.02, front_y, z), (half_w, front_y, z), radius=rod_r)
        else:
            _add_rod(cage, f"front_full_rail_{i}", (-half_w, front_y, z), (half_w, front_y, z), radius=rod_r)
    _add_rod(cage, "front_sill_left", (-half_w, front_y, r.door_bottom_z), (dxmin - 0.02, front_y, r.door_bottom_z), radius=rail_r)
    _add_rod(cage, "front_sill_right", (dxmax + 0.02, front_y, r.door_bottom_z), (half_w, front_y, r.door_bottom_z), radius=rail_r)

    # Fixed door surround (slightly larger than the hinged door).
    clr = 0.024
    sxmin, sxmax = dxmin - clr, dxmax + clr
    sy = front_y + 0.004
    stop = r.door_top_z + clr
    for nm, a, b in (
        ("fixed_door_frame_left", (sxmin, sy, r.door_bottom_z), (sxmin, sy, stop)),
        ("fixed_door_frame_right", (sxmax, sy, r.door_bottom_z), (sxmax, sy, stop)),
        ("fixed_door_frame_bottom", (sxmin, sy, r.door_bottom_z), (sxmax, sy, r.door_bottom_z)),
        ("fixed_door_frame_top", (sxmin, sy, stop), (sxmax, sy, stop)),
    ):
        _add_rod(cage, nm, a, b, radius=rail_r * 1.2)

    _build_box_roof(cage, r, rod_r, rail_r)
    return cage


def _build_box_roof(cage: Part, r: ResolvedBirdCageConfig, rod_r: float, rail_r: float) -> None:
    half_w, half_d = r.half_w, r.half_d
    front_y, back_y = r.front_y, r.back_y
    spring_z = r.spring_z
    roof_y_values = [front_y, front_y + (back_y - front_y) * 0.25, 0.0,
                     front_y + (back_y - front_y) * 0.75, back_y]

    if r.body_form == "barrel_vault_box":
        roof_r = half_w
        for i, y in enumerate(roof_y_values):
            _add_arch(cage, f"roof_arch_rib_{i}", center_x=0.0, y=y, spring_z=spring_z, radius=roof_r, rod_radius=rail_r)
        for i, deg in enumerate((20, 45, 70, 90, 110, 135, 160)):
            th = math.radians(deg)
            x = roof_r * math.cos(th)
            z = spring_z + roof_r * math.sin(th)
            _add_rod(cage, f"roof_longitudinal_{i}", (x, front_y, z), (x, back_y, z), radius=rod_r)
        for face_i, y in enumerate((front_y, back_y)):
            for i, x in enumerate((-0.36 * half_w, 0.0, 0.36 * half_w)):
                z_to = spring_z + math.sqrt(max(0.0, roof_r * roof_r - x * x))
                _add_rod(cage, f"gable_vertical_{face_i}_{i}", (x, y, spring_z), (x, y, z_to), radius=rod_r)
    elif r.body_form == "flat_top_box":
        n = 11 if r.bar_density == "dense" else 7
        for i in range(n):
            x = -half_w + 0.04 + i * ((2 * half_w - 0.08) / (n - 1))
            _add_rod(cage, f"roof_longitudinal_{i}", (x, front_y, spring_z), (x, back_y, spring_z), radius=rod_r)
        m = 8 if r.bar_density == "dense" else 5
        for i in range(m):
            y = front_y + 0.04 + i * ((back_y - front_y - 0.08) / (m - 1))
            _add_rod(cage, f"roof_cross_wire_{i}", (-half_w, y, spring_z), (half_w, y, spring_z), radius=rod_r)
    else:  # gable_box
        ridge_z = r.top_z
        for i, y in enumerate(roof_y_values):
            _add_rod(cage, f"roof_rib_{i}_l", (-half_w, y, spring_z), (0.0, y, ridge_z), radius=rail_r)
            _add_rod(cage, f"roof_rib_{i}_r", (half_w, y, spring_z), (0.0, y, ridge_z), radius=rail_r)
        _add_rod(cage, "roof_ridge_purlin", (0.0, front_y, ridge_z), (0.0, back_y, ridge_z), radius=rail_r)
        for i, xf in enumerate((0.25, 0.55, 0.85)):
            xp = half_w * xf
            zp = spring_z + (ridge_z - spring_z) * (1.0 - xf)
            _add_rod(cage, f"roof_longitudinal_{i}", (xp, front_y, zp), (xp, back_y, zp), radius=rod_r)
            _add_rod(cage, f"roof_longitudinal_{i + 3}", (-xp, front_y, zp), (-xp, back_y, zp), radius=rod_r)
        for face_i, y in enumerate((front_y, back_y)):
            for i, x in enumerate((-0.55 * half_w, 0.0, 0.55 * half_w)):
                z_at = spring_z + (ridge_z - spring_z) * (1.0 - abs(x) / half_w)
                _add_rod(cage, f"gable_vertical_{face_i}_{i}", (x, y, spring_z), (x, y, z_at), radius=rod_r)


def _build_round_body(model: ArticulatedObject, r: ResolvedBirdCageConfig) -> Part:
    cage = model.part("cage")
    R = r.cage_r
    z0, z1, dome_z = r.straight_z0, r.straight_z1, r.dome_z
    faceted = r.faceted
    n_sides = 6 if faceted else (20 if r.bar_density == "dense" else 12)
    front_dist = -r.front_y
    dxmin, dxmax = r.door_x_min, r.door_x_max
    door_bz, door_tz = r.door_bottom_z, r.door_top_z

    def ang(i: int) -> float:
        return math.tau * i / n_sides

    def pos(i: int) -> tuple[float, float]:
        return (R * math.cos(ang(i)), R * math.sin(ang(i)))

    bars: list[MeshGeometry] = []

    # Hoops.
    for z, tube in ((z0, 0.0048), ((z0 + z1) / 2.0, 0.0034), (z1, 0.0044)):
        if faceted:
            for i in range(n_sides):
                x0, y0 = pos(i)
                x1, y1 = pos((i + 1) % n_sides)
                bars.append(_mtube((x0, y0, z), (x1, y1, z), tube))
        else:
            bars.append(TorusGeometry(radius=R, tube=tube, radial_segments=10, tubular_segments=48).translate(0, 0, z))

    # Vertical bars around the circumference (front door gap skipped).
    for i in range(n_sides):
        x, y = pos(i)
        in_door = (y < 0.0) and (dxmin - 0.005 <= x <= dxmax + 0.005) and (abs(y + front_dist) < 0.06 or faceted and abs(y + r.front_y) < 0.001)
        # Simpler door test: near front and within door x-span.
        in_door = (y < -R * 0.55) and (dxmin - 0.005 <= x <= dxmax + 0.005)
        if in_door:
            if door_bz - z0 > 0.01:
                bars.append(_mrod_z(0.0032, door_bz - z0, (x, y, (z0 + door_bz) / 2.0)))
            if z1 - door_tz > 0.01:
                bars.append(_mrod_z(0.0032, z1 - door_tz, (x, y, (door_tz + z1) / 2.0)))
        else:
            bars.append(_mrod_z(0.0032, z1 - z0, (x, y, (z0 + z1) / 2.0)))
        # Roof meridian to crown (curved dome silhouette).
        bars.append(
            tube_from_spline_points(
                [(x, y, z1), (x * 0.72, y * 0.72, z1 + (dome_z - z1) * 0.42),
                 (x * 0.36, y * 0.36, z1 + (dome_z - z1) * 0.78), (x * 0.10, y * 0.10, dome_z)],
                radius=0.0030, samples_per_segment=4, radial_segments=8, cap_ends=True,
            )
        )

    # Crown ring + spokes.
    bars.append(TorusGeometry(radius=0.036, tube=0.0048, radial_segments=10, tubular_segments=32).translate(0, 0, dome_z))
    bars.append(_mrod_x(0.0032, 0.078, (0, 0, dome_z)))
    bars.append(tube_from_spline_points([(0, -0.039, dome_z), (0, 0.039, dome_z)], radius=0.0032, samples_per_segment=2, radial_segments=8, cap_ends=True))
    bars.append(_mrod_z(0.0050, 0.035, (0, 0, dome_z + 0.012)))

    # Door opening frame on the front face (heavier wire).
    fy = r.front_y
    frame_h = door_tz - door_bz + 0.022
    bars.extend([
        _mrod_z(0.0052, frame_h, (dxmin, fy, (door_bz + door_tz) / 2.0), 14),
        _mrod_z(0.0052, frame_h, (dxmax, fy, (door_bz + door_tz) / 2.0), 14),
        _mrod_x(0.0052, r.door_w + 0.022, (0, fy, door_bz), 14),
        _mrod_x(0.0052, r.door_w + 0.022, (0, fy, door_tz), 14),
    ])

    cage.visual(mesh_from_geometry(_merge(bars), "cage_bars"), material="bar", name="cage_bars", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
    return cage


# --------------------------------------------------------------------------- #
# Slot C: support_base — fused visuals on ``cage``
# --------------------------------------------------------------------------- #
def _build_support(cage: Part, r: ResolvedBirdCageConfig) -> None:
    if r.support_base == "caster_tray":
        _build_caster_tray(cage, r)
    elif r.support_base == "leg_stand":
        _build_leg_stand(cage, r)
    elif r.support_base == "footed_tray":
        _build_footed_tray(cage, r)
    else:
        _build_hanging_bail(cage, r)


def _build_caster_tray(cage: Part, r: ResolvedBirdCageConfig) -> None:
    half_w, half_d = r.half_w, r.half_d
    front_y, back_y, bottom_z = r.front_y, r.back_y, r.bottom_z
    tw, td = 2 * half_w + 0.12, 2 * half_d + 0.12
    cage.visual(Box((tw, td, 0.075)), origin=Origin(xyz=(0, 0, 0.105)), material="tray", name="base_tray", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
    cage.visual(Box((tw + 0.04, 0.045, 0.075)), origin=Origin(xyz=(0, -td / 2.0 - 0.02, 0.165)), material="tray", name="front_tray_lip", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
    cage.visual(Box((tw + 0.04, 0.045, 0.075)), origin=Origin(xyz=(0, td / 2.0 + 0.02, 0.165)), material="tray", name="rear_tray_lip", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
    cage.visual(Box((0.045, td, 0.075)), origin=Origin(xyz=(-tw / 2.0 - 0.02, 0, 0.165)), material="tray", name="side_tray_lip_0", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
    cage.visual(Box((0.045, td, 0.075)), origin=Origin(xyz=(tw / 2.0 + 0.02, 0, 0.165)), material="tray", name="side_tray_lip_1", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
    for ix, x in enumerate((-half_w, half_w)):
        for iy, y in enumerate((-half_d + 0.03, half_d - 0.03)):
            s = f"{ix}_{iy}"
            _add_rod(cage, f"caster_stem_{s}", (x, y, 0.034), (x, y, 0.074), radius=0.006, material="accent")
            cage.visual(Box((0.040, 0.014, 0.050)), origin=Origin(xyz=(x - 0.020, y, 0.043)), material="accent", name=f"caster_fork_a_{s}", material_class_id=("metal.aluminum_bare" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
            cage.visual(Box((0.040, 0.014, 0.050)), origin=Origin(xyz=(x + 0.020, y, 0.043)), material="accent", name=f"caster_fork_b_{s}", material_class_id=("metal.aluminum_bare" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
            cage.visual(Cylinder(radius=0.030, length=0.020), origin=Origin(xyz=(x, y, 0.030), rpy=(math.pi / 2.0, 0, 0)), material="wheel", name=f"caster_wheel_{s}", material_class_id="rubber.smooth_plain")
    for ix, x in enumerate((-half_w, half_w)):
        for iy, y in enumerate((front_y, back_y)):
            _add_rod(cage, f"tray_riser_{ix}_{iy}", (x, y, 0.135), (x, y, bottom_z + 0.008), radius=0.006)


def _build_leg_stand(cage: Part, r: ResolvedBirdCageConfig) -> None:
    half_w, half_d = r.half_w, r.half_d
    front_y, back_y, bottom_z = r.front_y, r.back_y, r.bottom_z
    sw, sd = half_w + 0.03, half_d + 0.03
    top_z = bottom_z - 0.006
    shelf_z = top_z * 0.24
    foot_h = 0.008
    corners = [(-sw, -sd), (-sw, sd), (sw, -sd), (sw, sd)]
    for i, (lx, ly) in enumerate(corners):
        _add_rod(cage, f"stand_leg_{i}", (lx, ly, foot_h), (lx, ly, top_z), radius=0.014, material="accent")
        cage.visual(Cylinder(radius=0.018, length=foot_h), origin=Origin(xyz=(lx, ly, foot_h / 2.0)), material="accent", name=f"foot_pad_{i}", material_class_id=("metal.aluminum_bare" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
    # Top apron (cage seats here) and lower shelf.
    for lbl, z in (("apron", top_z), ("shelf", shelf_z)):
        _add_rod(cage, f"{lbl}_front", (-sw, -sd, z), (sw, -sd, z), radius=0.008, material="accent")
        _add_rod(cage, f"{lbl}_rear", (-sw, sd, z), (sw, sd, z), radius=0.008, material="accent")
        _add_rod(cage, f"{lbl}_left", (-sw, -sd, z), (-sw, sd, z), radius=0.008, material="accent")
        _add_rod(cage, f"{lbl}_right", (sw, -sd, z), (sw, sd, z), radius=0.008, material="accent")
    for i in range(7):
        sx = -sw + 0.04 + i * ((2 * sw - 0.08) / 6.0)
        _add_rod(cage, f"shelf_cross_{i}", (sx, -sd, shelf_z), (sx, sd, shelf_z), radius=0.0045, material="accent")
    # Thin tray seated on the apron, tying legs to the cage bottom rails.
    cage.visual(Box((2 * half_w + 0.06, 2 * half_d + 0.06, 0.022)), origin=Origin(xyz=(0, 0, top_z + 0.011)), material="tray", name="cage_tray", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
    for ix, x in enumerate((-half_w, half_w)):
        for iy, y in enumerate((front_y, back_y)):
            _add_rod(cage, f"tray_riser_{ix}_{iy}", (x, y, top_z + 0.020), (x, y, bottom_z + 0.006), radius=0.006)


def _lathe_tray_mesh(base_r: float, rim_z: float, depth: float) -> MeshGeometry:
    return LatheGeometry.from_shell_profiles(
        [(0.030, rim_z - depth - 0.020), (0.72 * base_r, rim_z - depth - 0.018),
         (0.92 * base_r, rim_z - 0.004), (base_r, rim_z + 0.020),
         (base_r, rim_z + 0.055), (0.94 * base_r, rim_z + 0.074)],
        [(0.015, rim_z - depth - 0.006), (0.66 * base_r, rim_z - depth - 0.004),
         (0.87 * base_r, rim_z + 0.012), (0.90 * base_r, rim_z + 0.048),
         (0.84 * base_r, rim_z + 0.060)],
        segments=64, start_cap="flat", end_cap="round", lip_samples=6,
    )


def _build_footed_tray(cage: Part, r: ResolvedBirdCageConfig) -> None:
    base_r = r.cage_r * 1.15
    rim_z = r.straight_z0
    tray = _lathe_tray_mesh(base_r, rim_z, 0.09)
    cage.visual(mesh_from_geometry(tray, "base_tray"), material="tray", name="base_tray", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
    # Small scrollwork feet under the tray.
    for i in range(4):
        a = math.tau * i / 4.0 + math.pi / 4.0
        fx, fy = base_r * 0.7 * math.cos(a), base_r * 0.7 * math.sin(a)
        cage.visual(Cylinder(radius=0.010, length=rim_z - 0.03), origin=Origin(xyz=(fx, fy, (rim_z - 0.03) / 2.0)), material="accent", name=f"tray_foot_{i}", material_class_id=("metal.aluminum_bare" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
    # Top hanging hook rising from the dome crown.
    hook = tube_from_spline_points(
        [(0, 0, r.dome_z - 0.006), (0, 0, r.dome_z + 0.05), (0.012, 0, r.dome_z + 0.095),
         (0.036, 0, r.dome_z + 0.09), (0.02, 0, r.dome_z + 0.075)],
        radius=0.0042, samples_per_segment=8, radial_segments=10, cap_ends=True,
    )
    cage.visual(mesh_from_geometry(hook, "top_hook"), material="bar", name="top_hook", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))


def _build_hanging_bail(cage: Part, r: ResolvedBirdCageConfig) -> None:
    base_r = r.cage_r * 1.06
    rim_z = r.straight_z0
    pan = _lathe_tray_mesh(base_r, rim_z, 0.045)
    cage.visual(mesh_from_geometry(pan, "base_tray"), material="tray", name="base_tray", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
    # Arched carrying bail from the crown — sole support.
    bail = tube_from_spline_points(
        [(-0.02, 0, r.dome_z - 0.01), (-0.05, 0, r.dome_z + 0.10), (0.0, 0, r.dome_z + 0.17),
         (0.05, 0, r.dome_z + 0.10), (0.02, 0, r.dome_z - 0.01)],
        radius=0.0045, samples_per_segment=8, radial_segments=10, cap_ends=True,
    )
    cage.visual(mesh_from_geometry(bail, "carry_bail"), material="bar", name="carry_bail", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))


# --------------------------------------------------------------------------- #
# Slot D: interior — perches (+ optional feeder cups), fused visuals on ``cage``
# --------------------------------------------------------------------------- #
def _build_interior(cage: Part, r: ResolvedBirdCageConfig) -> None:
    n = r.n_perches
    z_lo = r.bottom_z + (r.spring_z - r.bottom_z) * 0.34
    z_hi = r.bottom_z + (r.spring_z - r.bottom_z) * 0.70
    if r.family == "box":
        _, n_side = _box_counts(r)
        ys = [r.front_y + i * ((r.back_y - r.front_y) / (n_side - 1)) for i in range(n_side)]
        interior_idx = list(range(1, n_side - 1)) or [n_side // 2]
        ex0, ex1 = -r.half_w - 0.004, r.half_w + 0.004
    else:
        interior_idx = None
        ex0, ex1 = -r.cage_r - 0.004, r.cage_r + 0.004
    for i in range(n):
        frac = 0.5 if n == 1 else i / (n - 1)
        z = z_lo + (z_hi - z_lo) * frac
        # Perch ends seat onto real wall bars: box → an interior side-wall
        # vertical (shared y); round/hex → the angle-0/π bars at y≈0.
        y = ys[interior_idx[i % len(interior_idx)]] if r.family == "box" else 0.0
        _add_rod(cage, f"perch_{i}", (ex0, y, z), (ex1, y, z), radius=0.013, material="wood")
    for i in range(r.n_feed_cups):
        z = r.door_bottom_z + (0.12 if i == 0 else 0.34)
        anchor_x = r.door_x_max + 0.024  # fixed door surround (right jamb)
        cup_x = r.door_x_max + 0.055
        cup_y = r.front_y + 0.030
        cage.visual(Cylinder(radius=0.026, length=0.034), origin=Origin(xyz=(cup_x, cup_y, z)), material="cup", name=f"feed_cup_{i}", material_class_id=("ceramic.porcelain_glazed_plain" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
        _add_rod(cage, f"feed_bracket_{i}", (anchor_x, r.front_y + 0.004, z), (cup_x, cup_y, z), radius=0.004, material="accent")


# --------------------------------------------------------------------------- #
# Slot B: door_mechanism — the articulated opening (+ latch)
# --------------------------------------------------------------------------- #
def _door_panel_offset(part: Part, r: ResolvedBirdCageConfig, *, x0: float, symmetric: bool) -> None:
    """Rectangular wire door panel. Local frame: bottom at z=0, spans door_h in z.

    ``x0`` is the local x of the left edge (0 for hinge-at-left, -w/2 for symmetric).
    """
    w, h = r.door_w, r.door_h
    rail_r, rod_r = 0.006, 0.0045
    x1 = x0 + w
    _add_rod(part, "door_left_frame", (x0, 0, 0), (x0, 0, h), radius=rail_r)
    _add_rod(part, "door_right_frame", (x1, 0, 0), (x1, 0, h), radius=rail_r)
    _add_rod(part, "door_bottom_frame", (x0, 0, 0), (x1, 0, 0), radius=rail_r)
    _add_rod(part, "door_top_frame", (x0, 0, h), (x1, 0, h), radius=rail_r)
    nbar = 5 if r.bar_density == "dense" else 3
    for i in range(nbar):
        lx = x0 + w * (i + 1) / (nbar + 1)
        _add_rod(part, f"door_vertical_bar_{i}", (lx, 0, 0.012), (lx, 0, h - 0.006), radius=rod_r)
    for i, lz in enumerate((h * 0.34, h * 0.68)):
        _add_rod(part, f"door_horizontal_bar_{i}", (x0 + 0.02, 0, lz), (x1 - 0.02, 0, lz), radius=rod_r)


def _add_latch(model: ArticulatedObject, door: Part, *, origin: tuple[float, float, float], boss_xyz: tuple[float, float, float]) -> None:
    door.visual(Cylinder(radius=0.014, length=0.008), origin=Origin(xyz=boss_xyz, rpy=(math.pi / 2.0, 0, 0)), material="bar", name="door_latch_boss", material_class_id="metal.paint_coated")
    latch = model.part("latch")
    latch.visual(Cylinder(radius=0.017, length=0.007), origin=Origin(xyz=(0, 0, 0), rpy=(math.pi / 2.0, 0, 0)), material="bar", name="latch_pivot_disc", material_class_id="metal.paint_coated")
    latch.visual(Box((0.082, 0.008, 0.017)), origin=Origin(xyz=(0.046, 0, 0)), material="bar", name="latch_tab", material_class_id="metal.paint_coated")
    latch.visual(Cylinder(radius=0.004, length=0.032), origin=Origin(xyz=(0, 0.016, 0), rpy=(math.pi / 2.0, 0, 0)), material="bar", name="latch_spindle", material_class_id="metal.paint_coated")
    model.articulation(
        "latch_pivot", ArticulationType.REVOLUTE, parent=door, child=latch,
        origin=Origin(xyz=origin), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.4, velocity=3.0, lower=0.0, upper=1.57),
    )


_PROUD = 0.016  # door panel sits this far proud of the front face (avoids
# coplanar closed-pose overlap with the cage bars). Connectivity is carried by a
# cage-side hinge PIN coaxial with the rotation axis: the door's hinge-edge frame
# rail (which lies on the axis) wraps it and never sweeps through it, so the pin
# stays put under rotation. Standoffs at the pin ends tie it to the surround.


def _emit_hinge_pin(cage: Part, r: ResolvedBirdCageConfig, *, axis: str, dxmin: float, dxmax: float, door_y: float, db: float, dh: float) -> None:
    """Cage hinge pin on the door's rotation axis + two standoffs to the cage."""
    ay = r.front_y + 0.004 if r.family == "box" else r.front_y  # surround / opening frame plane
    # standoff root x: box → the fixed surround-left jamb (dxmin-0.024); round →
    # the front opening frame vertical (dxmin).
    sx = (dxmin - 0.024) if r.family == "box" else dxmin
    if axis == "z":  # side hinge — vertical axis at (dxmin, door_y)
        _add_rod(cage, "cage_hinge_pin", (dxmin, door_y, db - 0.02), (dxmin, door_y, db + dh + 0.02), radius=0.005)
        for k, z in ((0, db + 0.03), (1, db + dh - 0.03)):
            _add_rod(cage, f"hinge_standoff_{k}", (sx, ay, z), (dxmin, door_y, z), radius=0.0045)
    else:  # drop front — horizontal x axis at (·, door_y, db)
        px0, px1 = dxmin - 0.02, dxmax + 0.02
        _add_rod(cage, "cage_hinge_pin", (px0, door_y, db), (px1, door_y, db), radius=0.005)
        for k, x in ((0, px0), (1, px1)):
            _add_rod(cage, f"hinge_standoff_{k}", (x, ay, db), (x, door_y, db), radius=0.0045)


def _build_door(model: ArticulatedObject, cage: Part, r: ResolvedBirdCageConfig) -> None:
    mech = r.door_mechanism
    fy = r.front_y
    door_y = fy - _PROUD
    dxmin, dxmax = r.door_x_min, r.door_x_max
    db, dh = r.door_bottom_z, r.door_h

    if mech == "side_hinge":
        door = model.part("door")
        _door_panel_offset(door, r, x0=0.0, symmetric=False)
        for i, zc in enumerate((dh * 0.28, dh * 0.76)):
            _add_rod(door, f"door_hinge_barrel_{i}", (0.0, -0.018, zc - 0.06), (0.0, -0.018, zc + 0.06), radius=0.011)
            door.visual(Box((0.02, 0.02, 0.018)), origin=Origin(xyz=(0.004, -0.009, zc)), material="bar", name=f"door_hinge_leaf_{i}", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
        _emit_hinge_pin(cage, r, axis="z", dxmin=dxmin, dxmax=dxmax, door_y=door_y, db=db, dh=dh)
        model.articulation(
            "door_hinge", ArticulationType.REVOLUTE, parent=cage, child=door,
            origin=Origin(xyz=(dxmin, door_y, db)), axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=1.35),
        )
        _add_latch(model, door, origin=(r.door_w + 0.014, -0.030, dh * 0.55), boss_xyz=(r.door_w + 0.014, -0.004, dh * 0.55))
        if r.family == "box":
            strike_x = dxmax + 0.062
            strike_z = db + dh * 0.55
            cage.visual(Box((0.030, 0.006, 0.030)), origin=Origin(xyz=(strike_x, door_y - 0.006, strike_z)), material="bar", name="latch_strike", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
            # Bridge the keeper to the fixed door-surround right jamb (x = dxmax + clr)
            # so it seats on a real cage bar instead of floating as its own island.
            _add_rod(cage, "strike_standoff", (dxmax + 0.024, fy + 0.004, strike_z), (strike_x, door_y - 0.006, strike_z), radius=0.0035)

    elif mech == "drop_front":
        door = model.part("door")
        _door_panel_offset(door, r, x0=-r.door_w / 2.0, symmetric=True)
        for i, xc in enumerate((-r.door_w * 0.25, r.door_w * 0.25)):
            _add_rod(door, f"door_hinge_barrel_{i}", (xc - 0.06, -0.018, 0.0), (xc + 0.06, -0.018, 0.0), radius=0.011)
            door.visual(Box((0.018, 0.02, 0.02)), origin=Origin(xyz=(xc, -0.009, 0.004)), material="bar", name=f"door_hinge_leaf_{i}", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
        _emit_hinge_pin(cage, r, axis="x", dxmin=dxmin, dxmax=dxmax, door_y=door_y, db=db, dh=dh)
        model.articulation(
            "door_hinge", ArticulationType.REVOLUTE, parent=cage, child=door,
            origin=Origin(xyz=(0.0, door_y, db)), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=1.55),
        )
        # Bottom-hinged drop-front doors use fixed side catches, not a swing
        # latch (a swinging tab would sweep the door's own bars). Add a small
        # non-moving keeper on the cage above the top free edge.
        catch_z = db + dh + 0.024  # on the fixed surround top rail
        cage.visual(Box((0.030, 0.006, 0.024)), origin=Origin(xyz=(0.0, door_y - 0.006, catch_z)), material="bar", name="drop_front_catch", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
        _add_rod(cage, "catch_standoff", (0.0, fy + 0.004, catch_z), (0.0, door_y - 0.006, catch_z), radius=0.0035)

    elif mech == "slide_door":
        door = model.part("door")
        _door_panel_offset(door, r, x0=0.0, symmetric=False)
        for i, (lx, lz) in enumerate(((-0.005, 0.06), (r.door_w + 0.005, 0.06), (-0.005, dh - 0.06), (r.door_w + 0.005, dh - 0.06))):
            door.visual(Box((0.010, 0.018, 0.030)), origin=Origin(xyz=(lx, -0.003, lz)), material="bar", name=f"door_lug_{i}", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
        # Guide rails on the cage, between the front face and the proud door.
        for side, sx in (("left", dxmin - 0.012), ("right", dxmax + 0.012)):
            cage.visual(Box((0.016, 0.028, r.spring_z - db)), origin=Origin(xyz=(sx, door_y + 0.008, db + (r.spring_z - db) / 2.0)), material="bar", name=f"{side}_guide_rail", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))
        travel = _clamp(dh * 0.86, 0.06, r.spring_z - db - dh - 0.02)
        model.articulation(
            "door_slide", ArticulationType.PRISMATIC, parent=cage, child=door,
            origin=Origin(xyz=(dxmin, door_y, db)), axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=5.0, velocity=0.5, lower=0.0, upper=travel),
        )
        cage.visual(Cylinder(radius=0.006, length=0.024), origin=Origin(xyz=(dxmax + 0.012, door_y + 0.004, db - 0.004), rpy=(0, math.pi / 2.0, 0)), material="bar", name="door_stop_pin", material_class_id=("metal.paint_coated" if r.palette_theme in {"black_powder", "white_coat"} else "metal.brass_aged"))

    else:  # top_hatch (flat_top_box only)
        hatch = model.part("roof_hatch")
        hw = r.half_w * 0.92
        hd = (r.back_y - r.front_y) * 0.92
        hz = 0.006  # panel elevation above hinge axis (local frame)
        hinge_z = r.spring_z + 0.016  # lift clear of the fixed roof grid
        # Cage-side hinge rail (rear top edge), tied down to the rear spring rail.
        _add_rod(cage, "hatch_hinge_rail", (-hw, r.back_y, hinge_z), (hw, r.back_y, hinge_z), radius=0.007)
        for i, xc in enumerate((-hw * 0.55, hw * 0.55)):
            _add_rod(cage, f"hatch_hinge_post_{i}", (xc, r.back_y, r.spring_z), (xc, r.back_y, hinge_z), radius=0.006)
        _add_rod(hatch, "hatch_frame_rear", (-hw, 0.0, hz), (hw, 0.0, hz), radius=0.006)
        _add_rod(hatch, "hatch_frame_front", (-hw, -hd, hz), (hw, -hd, hz), radius=0.006)
        _add_rod(hatch, "hatch_frame_left", (-hw, 0.0, hz), (-hw, -hd, hz), radius=0.006)
        _add_rod(hatch, "hatch_frame_right", (hw, 0.0, hz), (hw, -hd, hz), radius=0.006)
        for i in range(1, 8 if r.bar_density == "dense" else 5):
            yp = -hd * i / (8 if r.bar_density == "dense" else 5)
            _add_rod(hatch, f"hatch_bar_{i}", (-hw, yp, hz), (hw, yp, hz), radius=0.0045)
        for i, xc in enumerate((-hw * 0.55, hw * 0.55)):
            _add_rod(hatch, f"hatch_hinge_barrel_{i}", (xc - 0.04, 0.0, 0.0), (xc + 0.04, 0.0, 0.0), radius=0.009)
        for nm, x in (("hatch_handle_left", -0.06), ("hatch_handle_right", 0.06)):
            _add_rod(hatch, nm, (x, -hd, hz), (x, -hd, hz + 0.032), radius=0.005)
        _add_rod(hatch, "hatch_handle_top", (-0.06, -hd, hz + 0.032), (0.06, -hd, hz + 0.032), radius=0.005)
        model.articulation(
            "door_hinge", ArticulationType.REVOLUTE, parent=cage, child=hatch,
            origin=Origin(xyz=(0.0, r.back_y, hinge_z)), axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=1.20),
        )


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_bird_cage(config: BirdCageConfig, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="bird_cage", assets=assets)
    for role, rgba in r.palette.items():
        model.material(role, rgba=rgba)

    if r.family == "box":
        cage = _build_box_body(model, r)
    else:
        cage = _build_round_body(model, r)
    _build_support(cage, r)
    _build_interior(cage, r)
    _build_door(model, cage, r)

    cage.inertial = Inertial.from_geometry(
        Box((2 * r.half_w, 2 * r.half_d, r.top_z)),
        mass=8.0,
        origin=Origin(xyz=(0.0, 0.0, r.top_z * 0.45)),
    )
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_bird_cage(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_bird_cage(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedBirdCageConfig) -> list[tuple[str, str]]:
    return [
        ("body_form", r.body_form),
        ("door_mechanism", r.door_mechanism),
        ("support_base", r.support_base),
        ("interior", r.interior),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def _elem_names(part: Part) -> set[str]:
    return {v.name for v in part.visuals if v.name is not None}


def run_bird_cage_tests(model: ArticulatedObject, config: BirdCageConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    cage = model.get_part("cage")

    opening_part_name = "roof_hatch" if r.door_mechanism == "top_hatch" else "door"
    opening = model.get_part(opening_part_name)
    open_joint = model.get_articulation("door_slide" if r.door_mechanism == "slide_door" else "door_hinge")

    # --- captured-pin / seated-contact allowances (element scoped) ---
    if r.door_mechanism == "top_hatch":
        # Barrel-and-pin roof hinge: the cage-side rear hinge rail + its two carrier
        # posts (and the rear spring rail) are coaxial with the hatch pivot, so the
        # hatch's rear frame rails and hinge barrels wrap/capture them and stay in
        # contact throughout the swing. Declare every captured-hinge element pair.
        cage_hinge_elems = ("hatch_hinge_rail", "hatch_hinge_post_0", "hatch_hinge_post_1", "spring_rear_rail")
        hatch_hinge_elems = ("hatch_frame_rear", "hatch_frame_left", "hatch_frame_right",
                             "hatch_hinge_barrel_0", "hatch_hinge_barrel_1")
        for ea in cage_hinge_elems:
            for eb in hatch_hinge_elems:
                ctx.allow_overlap(cage, opening, elem_a=ea, elem_b=eb,
                                  reason=f"Roof-hatch captured hinge: hatch element {eb} wraps the coaxial cage rear-hinge element {ea}.")
    elif r.door_mechanism == "slide_door":
        door_elems = _elem_names(opening)
        rail_map = {"left_guide_rail": ["door_left_frame", "door_bottom_frame", "door_top_frame", "door_lug_0", "door_lug_2"],
                    "right_guide_rail": ["door_right_frame", "door_bottom_frame", "door_top_frame", "door_lug_1", "door_lug_3"]}
        for rail, elems in rail_map.items():
            for eb in elems:
                if eb in door_elems:
                    ctx.allow_overlap(cage, opening, elem_a=rail, elem_b=eb,
                                      reason=f"Guillotine door {eb} rides captured inside {rail}.")
    else:  # side_hinge / drop_front: door hinge-edge frame wraps the coaxial pin
        door_hinge_elems = ("door_left_frame", "door_right_frame", "door_bottom_frame", "door_top_frame",
                            "door_hinge_barrel_0", "door_hinge_barrel_1", "door_hinge_leaf_0", "door_hinge_leaf_1")
        for ea in ("cage_hinge_pin", "hinge_standoff_0", "hinge_standoff_1"):
            for eb in door_hinge_elems:
                ctx.allow_overlap(cage, opening, elem_a=ea, elem_b=eb,
                                  reason=f"Door hinge element {eb} wraps the coaxial cage hinge pin/standoff {ea}.")

    latch = None
    if any(a.name == "latch_pivot" for a in model.articulations):
        latch = model.get_part("latch")
        ctx.allow_overlap(opening, latch, elem_a="door_latch_boss", elem_b="latch_spindle",
                          reason="The rotating latch spindle is captured through the boss on the door.")

    # --- structural / identity checks ---
    ctx.check("cage root has enclosure geometry", cage is not None and len(cage.visuals) >= 3)
    ctx.check("access opening pivots on the cage root",
              open_joint is not None
              and (open_joint.parent if isinstance(open_joint.parent, str) else open_joint.parent.name) == "cage")
    ctx.check("access opening has a real non-fixed joint",
              open_joint is not None and open_joint.articulation_type in (ArticulationType.REVOLUTE, ArticulationType.PRISMATIC),
              details=f"joint={open_joint.name if open_joint else None} type={open_joint.articulation_type if open_joint else None}")

    perch_ct = len([v for v in cage.visuals if v.name and v.name.startswith("perch_")])
    ctx.check("interior has expected perch count", perch_ct == r.n_perches,
              details=f"found {perch_ct}, expected {r.n_perches}")
    if r.n_feed_cups:
        cup_ct = len([v for v in cage.visuals if v.name and v.name.startswith("feed_cup_")])
        ctx.check("feeder cups present", cup_ct == r.n_feed_cups, details=f"found {cup_ct}")

    # --- motion semantics (Rule 5 targeted poses) ---
    rest = ctx.part_world_aabb(opening)
    if r.door_mechanism in ("side_hinge",):
        with ctx.pose({open_joint: 0.95}):
            opened = ctx.part_world_aabb(opening)
        ctx.check("side-hinge door swings outward (-y)",
                  rest and opened and opened[0][1] < rest[0][1] - 0.06,
                  details=f"rest={rest}, open={opened}")
    elif r.door_mechanism == "drop_front":
        with ctx.pose({open_joint: 1.3}):
            opened = ctx.part_world_aabb(opening)
        ctx.check("drop-front door folds down/out",
                  rest and opened and opened[0][1] < rest[0][1] - 0.06,
                  details=f"rest={rest}, open={opened}")
    elif r.door_mechanism == "slide_door":
        with ctx.pose({open_joint: open_joint.motion_limits.upper}):
            opened = ctx.part_world_aabb(opening)
        ctx.check("guillotine door slides upward",
                  rest and opened and opened[1][2] > rest[1][2] + 0.04,
                  details=f"rest={rest}, open={opened}")
    else:  # top_hatch
        with ctx.pose({open_joint: 1.0}):
            opened = ctx.part_world_aabb(opening)
        ctx.check("roof hatch lifts up (+z)",
                  rest and opened and opened[1][2] > rest[1][2] + 0.05,
                  details=f"rest={rest}, open={opened}")

    if any(a.name == "latch_pivot" for a in model.articulations):
        latch_joint = model.get_articulation("latch_pivot")
        lr = ctx.part_element_world_aabb(latch, elem="latch_tab")
        with ctx.pose({latch_joint: 1.2}):
            lt = ctx.part_element_world_aabb(latch, elem="latch_tab")
        ctx.check("latch tab rotates", lr and lt and abs(lt[0][2] - lr[0][2]) > 0.012,
                  details=f"rest={lr}, turned={lt}")

    # --- Rule 5: no 穿模 across the sampled motion envelope ---
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)
    return ctx.report()
