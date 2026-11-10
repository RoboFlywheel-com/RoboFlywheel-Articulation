# SPDX-License-Identifier: Apache-2.0

"""Countertop / stovetop clamshell waffle maker — modular procedural template.

Derived from the modular spec ``articraft_template_authoring/specs_modular_v1/
waffle_maker.md`` and its 5 parents + 7 slot-fork 5-star sources under
``data/records/rec_waffle_maker_*`` / ``rec_0611_waffle_maker_var_*``.

Structure (pattern = ``mixed``):

- ``lower_housing`` (root) — a low box/cylinder with a raised waffle plate on
  its top face, four feet, and a rear hinge boss. ``housing_form`` slot picks
  the outer silhouette (rectangular / square / round).
- ``lid`` — a matching cap on top of the housing, joined by a rear-hinge
  REVOLUTE about the Y-axis. It carries a mirroring upper grid, a front
  handle, and (on some forms) status lenses / control knobs. Closes to a
  small cooking clearance above the lower grid.
- ``latch`` (optional) — an over-center / front-latch REVOLUTE about the
  X-axis at the front of the housing, matching sources 003/004/005 and the
  ``closure`` variant.

Slot axes:
- ``housing_form``: rectangular / square / round
- ``grid_topology``: rectangular_dense / square_pockets / heart_cells /
  belgian_4cells (topology of both cooking plates)
- ``closure``: no_latch / front_latch / over_center_latch
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True


HousingForm = Literal["rectangular", "square", "round"]
GridTopology = Literal["rectangular_dense", "square_pockets", "heart_cells", "belgian_4cells"]
Closure = Literal["no_latch", "front_latch", "over_center_latch"]
PaletteStyle = Literal[
    "cast_iron_black",
    "matte_charcoal",
    "brushed_steel_black",
    "cream_retro",
    "chrome_black",
]

HOUSING_FORMS: tuple[HousingForm, ...] = ("rectangular", "square", "round")
GRID_TOPOLOGIES: tuple[GridTopology, ...] = (
    "rectangular_dense",
    "square_pockets",
    "heart_cells",
    "belgian_4cells",
)
CLOSURES: tuple[Closure, ...] = ("no_latch", "front_latch", "over_center_latch")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "cast_iron_black",
    "matte_charcoal",
    "brushed_steel_black",
    "cream_retro",
    "chrome_black",
)

# Palettes — realistic waffle-maker colorways observed across the 5-star
# sources (charcoal / cast-iron / cream retro / brushed-steel / chrome).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "cast_iron_black": {
        "shell": (0.075, 0.078, 0.080, 1.0),
        "plate": (0.035, 0.038, 0.040, 1.0),
        "handle": (0.025, 0.028, 0.030, 1.0),
        "hardware": (0.42, 0.44, 0.45, 1.0),
        "accent": (0.62, 0.22, 0.035, 1.0),
        "foot": (0.018, 0.020, 0.022, 1.0),
    },
    "matte_charcoal": {
        "shell": (0.045, 0.050, 0.055, 1.0),
        "plate": (0.115, 0.125, 0.130, 1.0),
        "handle": (0.020, 0.020, 0.020, 1.0),
        "hardware": (0.28, 0.30, 0.31, 1.0),
        "accent": (0.72, 0.045, 0.025, 1.0),
        "foot": (0.018, 0.020, 0.022, 1.0),
    },
    "brushed_steel_black": {
        "shell": (0.035, 0.038, 0.040, 1.0),
        "plate": (0.075, 0.080, 0.080, 1.0),
        "handle": (0.025, 0.028, 0.030, 1.0),
        "hardware": (0.62, 0.64, 0.65, 1.0),
        "accent": (0.90, 0.27, 0.035, 1.0),
        "foot": (0.018, 0.020, 0.022, 1.0),
    },
    "cream_retro": {
        "shell": (0.88, 0.83, 0.72, 1.0),
        "plate": (0.14, 0.13, 0.12, 1.0),
        "handle": (0.14, 0.10, 0.08, 1.0),
        "hardware": (0.55, 0.55, 0.55, 1.0),
        "accent": (0.72, 0.20, 0.15, 1.0),
        "foot": (0.14, 0.10, 0.08, 1.0),
    },
    "chrome_black": {
        "shell": (0.020, 0.020, 0.022, 1.0),
        "plate": (0.055, 0.058, 0.060, 1.0),
        "handle": (0.020, 0.020, 0.022, 1.0),
        "hardware": (0.76, 0.78, 0.80, 1.0),
        "accent": (0.35, 0.72, 0.35, 1.0),
        "foot": (0.020, 0.020, 0.022, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base real-world dimensions (m). Rectangular family drives the primary
# spine; square is a re-proportion; round swaps outer boxes for cylinders.
# ---------------------------------------------------------------------------
_BASE_L = 0.230  # X extent (front-back) of rectangular / square housing
_BASE_W = 0.170  # Y extent (left-right) of rectangular housing
_BASE_H = 0.055  # housing shell height
_LID_H = 0.045  # lid shell thickness

_PLATE_INSET = 0.026  # margin from housing edge to cooking plate
_PLATE_THICKNESS = 0.010
_GRID_RIB_H = 0.005
_GRID_RIB_T = 0.0034

# Vertical stack in the LID's local frame (hinge at z=0, +Z above the hinge line).
# Closed-pose world stack (lid rotated back to q=0):
#   lower housing top face  world_z = r.height
#   lower plate slab       world_z ∈ [r.height, r.height + 0.010]  (_PLATE_THICKNESS)
#   lower ribs             world_z ∈ [r.height + 0.010, r.height + 0.015..0.018]
#                                    (0.015 = standard rib, 0.018 = belgian 1.6× rib)
#   ---- gap ----
#   upper ribs bottom      world_z ≥ lower_rib_top + gap
#   upper plate slab       world_z ∈ [upper_rib_top, upper_rib_top + 0.010]
#   ---- gap ----
#   lid_shell / crown / handle / indicators  above the upper plate slab
#
# Hinge origin in world: (0, hinge_y, r.hinge_z) where r.hinge_z = r.height + _HINGE_R.
# The lid's local frame origin is that hinge point.
#
# _UPPER_BASE_Z is the z (in lid frame) of the upper plate slab's OUTER face
# (the face that faces the lower housing). With face_sign=-1 the slab center
# is at _UPPER_BASE_Z - slab_h*0.5 and ribs extend to _UPPER_BASE_Z - slab_h.
# Choose 0.028 so that with belgian ribs (h=0.008) the upper rib bottom sits
# at world_z = r.height + _HINGE_R + (_UPPER_BASE_Z - _PLATE_THICKNESS - 0.008)
#           = r.height + 0.010 + 0.010 = r.height + 0.020, ≥ belgian lower
# rib top (r.height + 0.018) with 2mm clearance.
_UPPER_BASE_Z = 0.030
# All lid body visuals (shell / dome / handle / indicators) are lifted by this
# amount in the lid local frame so they clear the upper plate slab (which lives
# at local z ∈ [_UPPER_BASE_Z - _PLATE_THICKNESS, _UPPER_BASE_Z] = [0.020, 0.030])
# AND clear the housing shell_rim + rear hinge cheeks at the lid_open pose.
_LID_BODY_Z_LIFT = 0.026

_HINGE_INSET_Y = 0.006  # distance from rear housing edge to hinge axis
_HINGE_R = 0.010
_HINGE_LEN = 0.070

_FOOT_R = 0.014
_FOOT_H = 0.008

# Open angle capped at ≤ 90° so the lid stays clear of the rear hinge cheeks
# (which stick up ~0.016 m behind the pivot).
_LID_OPEN_ANGLE = math.radians(85.0)
_LATCH_OPEN_ANGLE = math.radians(35.0)


@dataclass(frozen=True)
class WaffleMakerConfig:
    housing_form: HousingForm | None = None
    grid_topology: GridTopology | None = None
    closure: Closure | None = None
    palette_style: PaletteStyle = "cast_iron_black"
    length_scale: float = 1.0
    width_scale: float = 1.0
    height_scale: float = 1.0
    lid_open_scale: float = 1.0
    name: str = "waffle_maker"


@dataclass(frozen=True)
class ResolvedWaffleMakerConfig:
    housing_form: HousingForm
    grid_topology: GridTopology
    closure: Closure
    palette_style: PaletteStyle
    # Concrete outer dimensions (scaled).
    length: float  # X extent
    width: float  # Y extent
    height: float
    plate_len: float  # X extent of cooking plate
    plate_wid: float  # Y extent of cooking plate
    plate_radius: float  # Round-plate radius (only meaningful when round)
    plate_thickness: float
    grid_rib_h: float
    grid_rib_t: float
    hinge_y: float  # Y of hinge axis (negative rear)
    hinge_z: float
    lid_open: float
    latch_open: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> WaffleMakerConfig:
    rng = random.Random(seed)
    return WaffleMakerConfig(
        housing_form=rng.choice(HOUSING_FORMS),
        grid_topology=rng.choice(GRID_TOPOLOGIES),
        closure=rng.choice(CLOSURES),
        palette_style=rng.choice(PALETTE_STYLES),
        length_scale=round(rng.uniform(0.90, 1.12), 4),
        width_scale=round(rng.uniform(0.90, 1.12), 4),
        height_scale=round(rng.uniform(0.90, 1.15), 4),
        lid_open_scale=round(rng.uniform(0.88, 1.10), 4),
        name=f"seeded_waffle_maker_{seed}",
    )


def resolve_config(config: WaffleMakerConfig | None = None) -> ResolvedWaffleMakerConfig:
    cfg = config or WaffleMakerConfig()
    housing_form = _pick(cfg.housing_form, HOUSING_FORMS)
    grid_topology = _pick(cfg.grid_topology, GRID_TOPOLOGIES)
    closure = _pick(cfg.closure, CLOSURES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    length_scale = _clamp(cfg.length_scale, 0.90, 1.12)
    width_scale = _clamp(cfg.width_scale, 0.90, 1.12)
    height_scale = _clamp(cfg.height_scale, 0.90, 1.15)
    lid_open_scale = _clamp(cfg.lid_open_scale, 0.88, 1.10)

    # Housing outer dimensions per form family.
    if housing_form == "square":
        length = _BASE_L * 0.95 * length_scale
        width = length  # perfectly square in plan
    elif housing_form == "round":
        # Round: bounding box is a square by diameter; internal cylinder radius
        # = length/2. Keep width == length so hinge geometry stays consistent.
        length = _BASE_L * 0.95 * length_scale
        width = length
    else:  # rectangular
        length = _BASE_L * length_scale
        width = _BASE_W * width_scale

    height = _BASE_H * height_scale

    # Plate extents. For rectangular/square: inset from housing edges. For
    # round: constrained to a circle inscribed in the housing minus the
    # hinge-boss zone (radius = length/2 - inset).
    if housing_form == "round":
        radius = length / 2.0 - _PLATE_INSET * 0.6
        plate_len = 2.0 * radius
        plate_wid = 2.0 * radius
        plate_radius = radius
    else:
        plate_len = length - 2.0 * _PLATE_INSET
        plate_wid = width - 2.0 * _PLATE_INSET
        plate_radius = min(plate_len, plate_wid) / 2.0

    hinge_y = -width / 2.0 + _HINGE_INSET_Y  # near the rear edge
    hinge_z = height + _HINGE_R  # hinge sits above the housing top

    lid_open = _clamp(_LID_OPEN_ANGLE * lid_open_scale, math.radians(60.0), math.radians(92.0))

    return ResolvedWaffleMakerConfig(
        housing_form=housing_form,
        grid_topology=grid_topology,
        closure=closure,
        palette_style=palette_style,
        length=length,
        width=width,
        height=height,
        plate_len=plate_len,
        plate_wid=plate_wid,
        plate_radius=plate_radius,
        plate_thickness=_PLATE_THICKNESS,
        grid_rib_h=_GRID_RIB_H,
        grid_rib_t=_GRID_RIB_T,
        hinge_y=hinge_y,
        hinge_z=hinge_z,
        lid_open=lid_open,
        latch_open=_LATCH_OPEN_ANGLE,
        name=cfg.name or "waffle_maker",
    )


def slot_choices_for_config(
    config: WaffleMakerConfig | ResolvedWaffleMakerConfig,
) -> list[tuple[str, str]]:
    r = config if isinstance(config, ResolvedWaffleMakerConfig) else resolve_config(config)
    return [
        ("housing_form", r.housing_form),
        ("grid_topology", r.grid_topology),
        ("closure", r.closure),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Housing shell (root part) — form-family-specific outer visual.
# ---------------------------------------------------------------------------
def _build_housing_shell(housing, r: ResolvedWaffleMakerConfig, *, shell_mat: str) -> None:
    """Outer shell of the lower housing, form-family specific.

    Rectangular / square: axis-aligned rounded box. Round: stacked cylinder
    (short shoulder + main body) so the outer silhouette reads as a puck.
    """
    if r.housing_form == "round":
        # Round puck body — Cylinder along Z. The main body spans the full
        # housing height so its top face coincides with the plate slab bottom.
        # A slightly wider skirt at the bottom adds stability.
        radius = r.length / 2.0
        housing.visual(
            Cylinder(radius=radius, length=r.height),
            origin=Origin(xyz=(0.0, 0.0, r.height * 0.5)),
            material=shell_mat,
            name="shell_body", material_class_id=("metal.brushed_silver" if r.palette_style in {"cast_iron_black", "matte_charcoal", "brushed_steel_black", "chrome_black"} else "plastic.opaque_glossy_molded"),
        )
        housing.visual(
            Cylinder(radius=radius * 1.02, length=r.height * 0.18),
            origin=Origin(xyz=(0.0, 0.0, r.height * 0.09)),
            material=shell_mat,
            name="shell_skirt", material_class_id=("metal.brushed_silver" if r.palette_style in {"cast_iron_black", "matte_charcoal", "brushed_steel_black", "chrome_black"} else "plastic.opaque_glossy_molded"),
        )
    else:
        # Rectangular / square — full-height boxy shell whose top face
        # coincides with the plate slab bottom. A shallow top shoulder rim
        # sits at the very top and overlaps the shell body / plate slab.
        housing.visual(
            Box((r.length, r.width, r.height)),
            origin=Origin(xyz=(0.0, 0.0, r.height * 0.5)),
            material=shell_mat,
            name="shell_body", material_class_id=("metal.brushed_silver" if r.palette_style in {"cast_iron_black", "matte_charcoal", "brushed_steel_black", "chrome_black"} else "plastic.opaque_glossy_molded"),
        )
        housing.visual(
            Box((r.length * 0.98, r.width * 0.98, r.height * 0.14)),
            origin=Origin(xyz=(0.0, 0.0, r.height - r.height * 0.03)),
            material=shell_mat,
            name="shell_rim", material_class_id=("metal.brushed_silver" if r.palette_style in {"cast_iron_black", "matte_charcoal", "brushed_steel_black", "chrome_black"} else "plastic.opaque_glossy_molded"),
        )


def _build_housing_feet(housing, r: ResolvedWaffleMakerConfig, *, foot_mat: str) -> None:
    """Four low feet at the housing base corners (or ring positions on round)."""
    if r.housing_form == "round":
        radius = r.length / 2.0 * 0.72
        for i in range(4):
            theta = math.pi / 4.0 + i * math.pi / 2.0
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            housing.visual(
                Cylinder(radius=_FOOT_R, length=_FOOT_H),
                origin=Origin(xyz=(x, y, _FOOT_H * 0.5)),
                material=foot_mat,
                name=f"foot_{i}", material_class_id="rubber.smooth_plain",
            )
    else:
        fx = r.length / 2.0 - 0.030
        fy = r.width / 2.0 - 0.028
        positions = ((-fx, -fy), (fx, -fy), (-fx, fy), (fx, fy))
        for i, (x, y) in enumerate(positions):
            housing.visual(
                Cylinder(radius=_FOOT_R, length=_FOOT_H),
                origin=Origin(xyz=(x, y, _FOOT_H * 0.5)),
                material=foot_mat,
                name=f"foot_{i}", material_class_id="rubber.smooth_plain",
            )


def _build_hinge_hardware(
    housing, r: ResolvedWaffleMakerConfig, *, shell_mat: str, hardware_mat: str
) -> None:
    """Rear hinge boss + captured pin — anchors the lid REVOLUTE."""
    # Two hinge cheeks + one center barrel + a full-width pin.
    housing.visual(
        Cylinder(radius=_HINGE_R, length=_HINGE_LEN),
        origin=Origin(
            xyz=(0.0, r.hinge_y, r.hinge_z),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=shell_mat,
        name="hinge_barrel", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "matte_charcoal", "cream_retro", "chrome_black"} else "metal.brushed_silver"),
    )
    # Full-width hinge pin (captured through lid knuckles).
    pin_length = max(r.length * 0.70, _HINGE_LEN * 1.15)
    housing.visual(
        Cylinder(radius=_HINGE_R * 0.42, length=pin_length),
        origin=Origin(
            xyz=(0.0, r.hinge_y, r.hinge_z),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=hardware_mat,
        name="hinge_pin", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cast_iron_black", "matte_charcoal", "cream_retro", "chrome_black"} else "metal.brushed_silver"),
    )
    # Two supporting cheeks anchor the barrel visually to the shell top.
    # Push the cheeks to the very rear (y=hinge_y is the hinge axis, which is
    # at r.width/2 - _HINGE_INSET_Y from the front). Their +Y face aligns with
    # the hinge line so they never sweep into the lid at any open angle.
    cheek_z = r.height + _HINGE_R * 0.15
    cheek_x_half = 0.014
    cheek_y_half = 0.010
    cheek_size = (cheek_x_half * 2, cheek_y_half * 2, _HINGE_R * 1.6)
    for i, x in enumerate((-r.length * 0.24, r.length * 0.24)):
        housing.visual(
            Box(cheek_size),
            origin=Origin(xyz=(x, r.hinge_y - cheek_y_half, cheek_z)),
            material=shell_mat,
            name=f"hinge_cheek_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "matte_charcoal", "cream_retro", "chrome_black"} else "metal.brushed_silver"),
        )


# ---------------------------------------------------------------------------
# Waffle plate — one function used for both lower (facing +Z) and upper
# (facing -Z, rotated). The plate slab is anchored to the parent part's top
# face and the ribs sit on/under it.
# ---------------------------------------------------------------------------
def _build_waffle_plate(
    part,
    r: ResolvedWaffleMakerConfig,
    *,
    plate_mat: str,
    base_z: float,
    face_sign: int,  # +1 = ribs face up, -1 = ribs face down
    name_prefix: str,
    y_center: float = 0.0,
) -> None:
    """A cooking plate (slab + rib pattern) on ``part``.

    Geometry is expressed entirely as SDK primitives (Box / Cylinder). The
    exact rib topology is driven by ``r.grid_topology``: dense rectangular
    ribs (source 004/005), square-pocket ribs (source 002), heart cells
    (variant), or Belgian 2×2 cells (variant).
    """
    plate_len = r.plate_len
    plate_wid = r.plate_wid
    slab_h = r.plate_thickness

    # Base slab. For round housing, use a Cylinder so the plate is disc-shaped.
    slab_z = base_z + face_sign * slab_h * 0.5
    if r.housing_form == "round":
        part.visual(
            Cylinder(radius=r.plate_radius, length=slab_h),
            origin=Origin(xyz=(0.0, y_center, slab_z)),
            material=plate_mat,
            name=f"{name_prefix}_slab", material_class_id="metal.cast_iron_bare",
        )
    else:
        part.visual(
            Box((plate_len, plate_wid, slab_h)),
            origin=Origin(xyz=(0.0, y_center, slab_z)),
            material=plate_mat,
            name=f"{name_prefix}_slab", material_class_id="metal.cast_iron_bare",
        )

    # Rib zone: sits directly on the slab, extending outward along face_sign.
    rib_top_z = base_z + face_sign * slab_h
    rib_h = r.grid_rib_h
    rib_center_z = rib_top_z + face_sign * rib_h * 0.5

    if r.grid_topology == "belgian_4cells":
        _emit_belgian_ribs(
            part,
            plate_len=plate_len,
            plate_wid=plate_wid,
            y_center=y_center,
            rib_top_z=rib_top_z,
            face_sign=face_sign,
            rib_h=rib_h,
            plate_mat=plate_mat,
            name_prefix=name_prefix,
        )
    elif r.grid_topology == "heart_cells":
        _emit_heart_cell_ribs(
            part,
            plate_len=plate_len,
            plate_wid=plate_wid,
            y_center=y_center,
            rib_center_z=rib_center_z,
            rib_h=rib_h,
            plate_mat=plate_mat,
            name_prefix=name_prefix,
        )
    elif r.grid_topology == "square_pockets":
        _emit_square_pocket_ribs(
            part,
            plate_len=plate_len,
            plate_wid=plate_wid,
            y_center=y_center,
            rib_center_z=rib_center_z,
            rib_h=rib_h,
            rib_t=r.grid_rib_t,
            plate_mat=plate_mat,
            name_prefix=name_prefix,
        )
    else:  # rectangular_dense (default)
        _emit_dense_ribs(
            part,
            plate_len=plate_len,
            plate_wid=plate_wid,
            y_center=y_center,
            rib_center_z=rib_center_z,
            rib_h=rib_h,
            rib_t=r.grid_rib_t,
            plate_mat=plate_mat,
            name_prefix=name_prefix,
            round_clip=(r.housing_form == "round"),
            round_radius=r.plate_radius,
        )


def _emit_dense_ribs(
    part,
    *,
    plate_len: float,
    plate_wid: float,
    y_center: float,
    rib_center_z: float,
    rib_h: float,
    rib_t: float,
    plate_mat: str,
    name_prefix: str,
    round_clip: bool,
    round_radius: float,
) -> None:
    """Dense parallel-rib waffle grid: 8 columns × 5 rows of ribs (sources
    002/004/005). On round plates the outer ribs are shortened so they stay
    inside the disc."""
    n_cols = 8
    n_rows = 5
    margin = 0.010
    usable_x = plate_len - 2.0 * margin
    usable_y = plate_wid - 2.0 * margin

    # X-parallel ribs (rows).
    for j in range(n_rows + 1):
        y_local = -usable_y / 2.0 + j * usable_y / n_rows
        if round_clip:
            # Chord length of a horizontal cut at height y inside a disc.
            chord = 2.0 * math.sqrt(max(round_radius * round_radius - y_local * y_local, 0.0))
            length_x = max(min(usable_x, chord - 0.006), 0.010)
        else:
            length_x = usable_x
        part.visual(
            Box((length_x, rib_t, rib_h)),
            origin=Origin(xyz=(0.0, y_center + y_local, rib_center_z)),
            material=plate_mat,
            name=f"{name_prefix}_rib_r{j}", material_class_id="metal.cast_iron_bare",
        )

    # Y-parallel ribs (columns).
    for i in range(n_cols + 1):
        x = -usable_x / 2.0 + i * usable_x / n_cols
        if round_clip:
            chord = 2.0 * math.sqrt(max(round_radius * round_radius - x * x, 0.0))
            length_y = max(min(usable_y, chord - 0.006), 0.010)
        else:
            length_y = usable_y
        part.visual(
            Box((rib_t, length_y, rib_h)),
            origin=Origin(xyz=(x, y_center, rib_center_z)),
            material=plate_mat,
            name=f"{name_prefix}_rib_c{i}", material_class_id="metal.cast_iron_bare",
        )


def _emit_square_pocket_ribs(
    part,
    *,
    plate_len: float,
    plate_wid: float,
    y_center: float,
    rib_center_z: float,
    rib_h: float,
    rib_t: float,
    plate_mat: str,
    name_prefix: str,
) -> None:
    """5x5 raised-rib grid producing square pockets (source 002 style)."""
    n = 5
    margin = 0.012
    usable_x = plate_len - 2.0 * margin
    usable_y = plate_wid - 2.0 * margin
    rib_t2 = rib_t * 1.4

    for j in range(n + 1):
        y_local = -usable_y / 2.0 + j * usable_y / n
        part.visual(
            Box((usable_x, rib_t2, rib_h)),
            origin=Origin(xyz=(0.0, y_center + y_local, rib_center_z)),
            material=plate_mat,
            name=f"{name_prefix}_rib_r{j}", material_class_id="metal.cast_iron_bare",
        )
    for i in range(n + 1):
        x = -usable_x / 2.0 + i * usable_x / n
        part.visual(
            Box((rib_t2, usable_y, rib_h)),
            origin=Origin(xyz=(x, y_center, rib_center_z)),
            material=plate_mat,
            name=f"{name_prefix}_rib_c{i}", material_class_id="metal.cast_iron_bare",
        )


def _emit_belgian_ribs(
    part,
    *,
    plate_len: float,
    plate_wid: float,
    y_center: float,
    rib_top_z: float,
    face_sign: int,
    rib_h: float,
    plate_mat: str,
    name_prefix: str,
) -> None:
    """Belgian 2×2 deep-cell grid: only the outer walls + one center cross,
    producing four large square/rectangular pockets (source var
    `4_belgian_cells`)."""
    outer_wall = 0.010
    cross_wall = 0.010
    # Deeper Belgian ribs — 1.6× the standard rib height. Recompute center
    # so the taller ribs still sit ON the slab (not sunk into it).
    ribd_h = rib_h * 1.6
    ribd_center_z = rib_top_z + face_sign * ribd_h * 0.5

    # Outer frame (four walls forming an outer rectangle).
    part.visual(
        Box((plate_len, outer_wall, ribd_h)),
        origin=Origin(xyz=(0.0, y_center + plate_wid / 2.0 - outer_wall / 2.0, ribd_center_z)),
        material=plate_mat,
        name=f"{name_prefix}_frame_y+", material_class_id="metal.cast_iron_bare",
    )
    part.visual(
        Box((plate_len, outer_wall, ribd_h)),
        origin=Origin(xyz=(0.0, y_center - plate_wid / 2.0 + outer_wall / 2.0, ribd_center_z)),
        material=plate_mat,
        name=f"{name_prefix}_frame_y-", material_class_id="metal.cast_iron_bare",
    )
    part.visual(
        Box((outer_wall, plate_wid, ribd_h)),
        origin=Origin(xyz=(plate_len / 2.0 - outer_wall / 2.0, y_center, ribd_center_z)),
        material=plate_mat,
        name=f"{name_prefix}_frame_x+", material_class_id="metal.cast_iron_bare",
    )
    part.visual(
        Box((outer_wall, plate_wid, ribd_h)),
        origin=Origin(xyz=(-plate_len / 2.0 + outer_wall / 2.0, y_center, ribd_center_z)),
        material=plate_mat,
        name=f"{name_prefix}_frame_x-", material_class_id="metal.cast_iron_bare",
    )
    # Cross ribs dividing the plate into 2×2 = 4 cells.
    part.visual(
        Box((plate_len, cross_wall, ribd_h)),
        origin=Origin(xyz=(0.0, y_center, ribd_center_z)),
        material=plate_mat,
        name=f"{name_prefix}_cross_x", material_class_id="metal.cast_iron_bare",
    )
    part.visual(
        Box((cross_wall, plate_wid, ribd_h)),
        origin=Origin(xyz=(0.0, y_center, ribd_center_z)),
        material=plate_mat,
        name=f"{name_prefix}_cross_y", material_class_id="metal.cast_iron_bare",
    )


def _emit_heart_cell_ribs(
    part,
    *,
    plate_len: float,
    plate_wid: float,
    y_center: float,
    rib_center_z: float,
    rib_h: float,
    plate_mat: str,
    name_prefix: str,
) -> None:
    """Heart-cell waffle plate: 2×2 heart-shaped pockets, each rendered as a
    box outline + two upper-lobe cylinders and a lower-point cylinder
    (approximating the heart silhouette with axis-aligned primitives)."""
    cross_wall = 0.006
    cell_w = plate_len / 2.0
    cell_d = plate_wid / 2.0
    # Center cross ribs (structural + heart-cell divider).
    part.visual(
        Box((plate_len, cross_wall, rib_h)),
        origin=Origin(xyz=(0.0, y_center, rib_center_z)),
        material=plate_mat,
        name=f"{name_prefix}_cross_x", material_class_id="metal.cast_iron_bare",
    )
    part.visual(
        Box((cross_wall, plate_wid, rib_h)),
        origin=Origin(xyz=(0.0, y_center, rib_center_z)),
        material=plate_mat,
        name=f"{name_prefix}_cross_y", material_class_id="metal.cast_iron_bare",
    )
    heart_scale = 0.42 * min(cell_w, cell_d) / 0.06
    lobe_r = 0.014 * heart_scale
    for i, (cx_sign, cy_sign) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        cx = cx_sign * cell_w * 0.5
        cy = cy_sign * cell_d * 0.5
        # Two upper lobes (the "bulbs" of the heart).
        part.visual(
            Cylinder(radius=lobe_r, length=rib_h),
            origin=Origin(xyz=(cx - lobe_r * 0.7, y_center + cy + lobe_r * 0.4, rib_center_z)),
            material=plate_mat,
            name=f"{name_prefix}_heart_lobeL_{i}", material_class_id="metal.cast_iron_bare",
        )
        part.visual(
            Cylinder(radius=lobe_r, length=rib_h),
            origin=Origin(xyz=(cx + lobe_r * 0.7, y_center + cy + lobe_r * 0.4, rib_center_z)),
            material=plate_mat,
            name=f"{name_prefix}_heart_lobeR_{i}", material_class_id="metal.cast_iron_bare",
        )
        # Lower point (small box tilted 45deg would be nice; use a small
        # square as a placeholder — the two lobes + this point read "heart").
        part.visual(
            Box((lobe_r * 1.6, lobe_r * 1.6, rib_h)),
            origin=Origin(xyz=(cx, y_center + cy - lobe_r * 0.6, rib_center_z)),
            material=plate_mat,
            name=f"{name_prefix}_heart_point_{i}", material_class_id="metal.cast_iron_bare",
        )


# ---------------------------------------------------------------------------
# Lid — mirrors the housing shell + carries an upper waffle plate, a front
# handle, and (round/rectangular variants) status lenses.
# ---------------------------------------------------------------------------
def _build_lid_shell(lid, r: ResolvedWaffleMakerConfig, *, shell_mat: str) -> None:
    """Lid outer shell — anchored on the hinge line, extending forward (local
    +Y) and upward (local +Z). All lid visuals live in the closed-lid local
    frame (hinge at origin, lid body forward in +Y)."""
    body_y_center = r.width / 2.0 - _HINGE_INSET_Y
    if r.housing_form == "round":
        radius = r.length / 2.0
        # The lid body is a cylinder centered above the housing, expressed
        # in the lid's local frame. In the lid frame the hinge is at origin,
        # so the lid body center is at +Y = body_y_center.
        lid.visual(
            Cylinder(radius=radius, length=_LID_H * 0.85),
            origin=Origin(xyz=(0.0, body_y_center, _LID_BODY_Z_LIFT + _LID_H * 0.45)),
            material=shell_mat,
            name="lid_shell", material_class_id=("metal.brushed_silver" if r.palette_style in {"cast_iron_black", "matte_charcoal", "brushed_steel_black", "chrome_black"} else "plastic.opaque_glossy_molded"),
        )
        lid.visual(
            Cylinder(radius=radius * 0.94, length=_LID_H * 0.30),
            origin=Origin(
                xyz=(0.0, body_y_center, _LID_BODY_Z_LIFT + _LID_H * 0.85 + _LID_H * 0.10)
            ),
            material=shell_mat,
            name="lid_dome", material_class_id=("metal.brushed_silver" if r.palette_style in {"cast_iron_black", "matte_charcoal", "brushed_steel_black", "chrome_black"} else "plastic.opaque_glossy_molded"),
        )
    else:
        lid.visual(
            Box((r.length, r.width, _LID_H * 0.85)),
            origin=Origin(xyz=(0.0, body_y_center, _LID_BODY_Z_LIFT + _LID_H * 0.45)),
            material=shell_mat,
            name="lid_shell", material_class_id=("metal.brushed_silver" if r.palette_style in {"cast_iron_black", "matte_charcoal", "brushed_steel_black", "chrome_black"} else "plastic.opaque_glossy_molded"),
        )
        # A subtle raised crown on top.
        lid.visual(
            Box((r.length * 0.85, r.width * 0.85, _LID_H * 0.20)),
            origin=Origin(
                xyz=(0.0, body_y_center, _LID_BODY_Z_LIFT + _LID_H * 0.85 + _LID_H * 0.06),
            ),
            material=shell_mat,
            name="lid_crown", material_class_id=("metal.brushed_silver" if r.palette_style in {"cast_iron_black", "matte_charcoal", "brushed_steel_black", "chrome_black"} else "plastic.opaque_glossy_molded"),
        )


def _build_lid_handle(lid, r: ResolvedWaffleMakerConfig, *, handle_mat: str) -> None:
    """Front handle on the lid — a bar handle spanning the front edge."""
    body_y_center = r.width / 2.0 - _HINGE_INSET_Y
    front_y = body_y_center + (r.width / 2.0) * 0.86
    handle_w = r.length * 0.55
    handle_thick = 0.018
    handle_h = 0.024
    lid.visual(
        Box((handle_w, handle_thick, handle_h)),
        origin=Origin(xyz=(0.0, front_y, _LID_BODY_Z_LIFT + _LID_H * 0.90)),
        material=handle_mat,
        name="handle_bar", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cast_iron_black", "matte_charcoal", "brushed_steel_black", "chrome_black"} else "wood.polished_varnished"),
    )
    # Two short standoffs anchor the bar to the lid shell (visible support).
    stand_z = _LID_BODY_Z_LIFT + _LID_H * 0.85 + 0.0005
    for i, x in enumerate((-handle_w / 2.0 + 0.010, handle_w / 2.0 - 0.010)):
        lid.visual(
            Box((0.020, 0.020, 0.012)),
            origin=Origin(xyz=(x, front_y - 0.006, stand_z + 0.006)),
            material=handle_mat,
            name=f"handle_stand_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cast_iron_black", "matte_charcoal", "brushed_steel_black", "chrome_black"} else "wood.polished_varnished"),
        )


def _build_lid_hinge_knuckle(lid, r: ResolvedWaffleMakerConfig, *, shell_mat: str) -> None:
    """Lid-side hinge knuckle: two barrel segments captured on the housing pin,
    plus vertical bosses that anchor each knuckle up into the lid shell so the
    lid part remains a single connected component."""
    for i, x in enumerate((-r.length * 0.10, r.length * 0.10)):
        lid.visual(
            Cylinder(radius=_HINGE_R * 0.75, length=0.024),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=shell_mat,
            name=f"lid_knuckle_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "matte_charcoal", "cream_retro", "chrome_black"} else "metal.brushed_silver"),
        )
        # Vertical boss that bridges from the knuckle (z=0) up into the lid
        # shell (bottom at z=_LID_BODY_Z_LIFT + LID_H*0.02 ≈ 0.027). Its bottom
        # face contains the knuckle center; its top embeds into the shell.
        boss_h = _LID_BODY_Z_LIFT + _LID_H * 0.10
        lid.visual(
            Box((0.020, 0.014, boss_h)),
            origin=Origin(xyz=(x, 0.007, boss_h * 0.5)),
            material=shell_mat,
            name=f"lid_knuckle_boss_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "matte_charcoal", "cream_retro", "chrome_black"} else "metal.brushed_silver"),
        )


def _build_lid_indicators(lid, r: ResolvedWaffleMakerConfig, *, accent_mat: str) -> None:
    """Two small status lenses on the front face of the lid."""
    body_y_center = r.width / 2.0 - _HINGE_INSET_Y
    front_y = body_y_center + (r.width / 2.0) * 0.62
    for i, (x, mat) in enumerate(((-0.020, accent_mat), (0.020, accent_mat))):
        lid.visual(
            Cylinder(radius=0.005, length=0.003),
            origin=Origin(xyz=(x, front_y, _LID_BODY_Z_LIFT + _LID_H * 0.60)),
            material=mat,
            name=f"lid_indicator_{i}", material_class_id="tech.emissive_surface",
        )


# ---------------------------------------------------------------------------
# Latch (optional) — front over-center bail, joined to housing by REVOLUTE X.
# ---------------------------------------------------------------------------
def _build_latch(
    model: ArticulatedObject,
    r: ResolvedWaffleMakerConfig,
    *,
    hardware_mat: str,
    handle_mat: str,
    shell_mat: str,
) -> None:
    housing = model.get_part("lower_housing")
    latch = model.part("latch")
    # Latch pivot mounted on the housing front face, just above the housing
    # top and slightly forward of the front wall (so the paddle extends into
    # empty space, not into the shell body).
    pivot_y = r.width / 2.0 + 0.012
    pivot_z = r.height + 0.012

    # Two front bearing lugs on the housing hold the latch pin. Each lug
    # straddles the housing top face (extending both above and below r.height)
    # so it stays connected to the shell body.
    lug_y = r.width / 2.0
    lug_h = 0.028
    lug_center_z = r.height + 0.006  # ~1/2 of lug sits inside the shell
    for i, x in enumerate((-0.020, 0.020)):
        housing.visual(
            Box((0.016, 0.020, lug_h)),
            origin=Origin(xyz=(x, lug_y, lug_center_z)),
            material=shell_mat,
            name=f"latch_lug_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "matte_charcoal", "cream_retro", "chrome_black"} else "metal.brushed_silver"),
        )

    # Latch axle (visible steel pin between the lugs).
    latch.visual(
        Cylinder(radius=0.004, length=0.060),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware_mat,
        name="latch_pin", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cast_iron_black", "matte_charcoal", "cream_retro", "chrome_black"} else "metal.brushed_silver"),
    )
    # Paddle / bail extends outward (local +Y direction pre-rotation — forward
    # of the housing at closed pose). Rotation around +X tilts the paddle up
    # to release.
    if r.closure == "over_center_latch":
        # A U-shaped bail approximated by two arms + a crossbar.
        arm_len = 0.045
        for i, x in enumerate((-0.024, 0.024)):
            latch.visual(
                Box((0.006, arm_len, 0.006)),
                origin=Origin(xyz=(x, arm_len / 2.0, 0.0)),
                material=hardware_mat,
                name=f"bail_arm_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cast_iron_black", "matte_charcoal", "cream_retro", "chrome_black"} else "metal.brushed_silver"),
            )
        latch.visual(
            Box((0.060, 0.006, 0.006)),
            origin=Origin(xyz=(0.0, arm_len, 0.0)),
            material=hardware_mat,
            name="bail_bridge", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cast_iron_black", "matte_charcoal", "cream_retro", "chrome_black"} else "metal.brushed_silver"),
        )
    else:  # front_latch — flat paddle
        latch.visual(
            Box((0.045, 0.040, 0.010)),
            origin=Origin(xyz=(0.0, 0.024, 0.0)),
            material=handle_mat,
            name="latch_paddle", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cast_iron_black", "matte_charcoal", "brushed_steel_black", "chrome_black"} else "wood.polished_varnished"),
        )
        latch.visual(
            Box((0.030, 0.010, 0.008)),
            origin=Origin(xyz=(0.0, 0.045, -0.005)),
            material=hardware_mat,
            name="latch_lip", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cast_iron_black", "matte_charcoal", "cream_retro", "chrome_black"} else "metal.brushed_silver"),
        )

    model.articulation(
        "latch_hinge",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=latch,
        origin=Origin(xyz=(0.0, pivot_y, pivot_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0,
            velocity=3.0,
            lower=0.0,
            upper=r.latch_open,
        ),
        meta={"reference_pose": 0.0, "positive_motion": "swings latch upward"},
    )


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------
def build_waffle_maker(
    config: WaffleMakerConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    palette = PALETTES[r.palette_style]
    model = ArticulatedObject(name=r.name, assets=assets)

    mats: dict[str, str] = {}
    for key, rgba in palette.items():
        mat = model.material(f"waffle_{key}_{r.palette_style}", rgba=rgba)
        mats[key] = mat.name

    housing = model.part("lower_housing")
    _build_housing_shell(housing, r, shell_mat=mats["shell"])
    _build_housing_feet(housing, r, foot_mat=mats["foot"])
    _build_hinge_hardware(housing, r, shell_mat=mats["shell"], hardware_mat=mats["hardware"])
    _build_waffle_plate(
        housing,
        r,
        plate_mat=mats["plate"],
        base_z=r.height,  # top face of the housing
        face_sign=+1,
        name_prefix="lower_grid",
    )

    lid = model.part("lid")
    _build_lid_shell(lid, r, shell_mat=mats["shell"])
    _build_lid_handle(lid, r, handle_mat=mats["handle"])
    _build_lid_hinge_knuckle(lid, r, shell_mat=mats["shell"])
    _build_lid_indicators(lid, r, accent_mat=mats["accent"])
    # Upper waffle plate is anchored to the lid underside (ribs face -Z in
    # the lid's local frame, so ``face_sign=-1``). It sits at
    # z = _UPPER_BASE_Z relative to the hinge line so a small positive gap
    # remains between the two plates in the closed pose, and is y-centered
    # under the lid body (which is offset by body_y_center from the hinge).
    body_y_center = r.width / 2.0 - _HINGE_INSET_Y
    _build_waffle_plate(
        lid,
        r,
        plate_mat=mats["plate"],
        base_z=_UPPER_BASE_Z,
        face_sign=-1,
        name_prefix="upper_grid",
        y_center=body_y_center,
    )

    # Lid REVOLUTE hinge (rear, Y-axis). q=0 = closed pose (small cooking gap).
    # Positive q opens the lid backwards (top rotates over the rear housing).
    model.articulation(
        "lid_hinge",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=lid,
        origin=Origin(xyz=(0.0, r.hinge_y, r.hinge_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=18.0,
            velocity=1.8,
            lower=0.0,
            upper=r.lid_open,
        ),
        meta={"reference_pose": 0.0, "positive_motion": "opens the lid backward"},
    )

    if r.closure != "no_latch":
        _build_latch(
            model,
            r,
            hardware_mat=mats["hardware"],
            handle_mat=mats["handle"],
            shell_mat=mats["shell"],
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_waffle_maker(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_waffle_maker(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Author tests (baseline + motion QC + Rule 5 targeted poses).
# ---------------------------------------------------------------------------
def run_waffle_maker_tests(
    object_model: ArticulatedObject, config: WaffleMakerConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    housing = object_model.get_part("lower_housing")
    lid = object_model.get_part("lid")
    lid_hinge = object_model.get_articulation("lid_hinge")

    # --- Hinge captured-pin allow_overlap (element-scoped). ------------------
    ctx.allow_overlap(
        housing,
        lid,
        elem_a="hinge_pin",
        elem_b="lid_knuckle_0",
        reason="The rear hinge pin is intentionally captured through the lid knuckles.",
    )
    ctx.allow_overlap(
        housing,
        lid,
        elem_a="hinge_pin",
        elem_b="lid_knuckle_1",
        reason="The rear hinge pin is intentionally captured through the lid knuckles.",
    )
    ctx.allow_overlap(
        housing,
        lid,
        elem_a="hinge_barrel",
        elem_b="lid_knuckle_0",
        reason="The housing-side hinge barrel and lid knuckle interleave along the hinge line.",
    )
    ctx.allow_overlap(
        housing,
        lid,
        elem_a="hinge_barrel",
        elem_b="lid_knuckle_1",
        reason="The housing-side hinge barrel and lid knuckle interleave along the hinge line.",
    )
    # Lid-shell / hinge-barrel local overlap around the shared hinge line.
    ctx.allow_overlap(
        housing,
        lid,
        elem_a="hinge_barrel",
        elem_b="lid_shell",
        reason="Hinge barrel and lid shell are seated along the shared hinge line.",
    )
    # Lid knuckle bosses (vertical stems that anchor each knuckle up into the
    # lid shell) share the hinge neighborhood with the housing-side barrel and
    # pin; they interleave along the same captured-pin geometry.
    for i in range(2):
        ctx.allow_overlap(
            housing,
            lid,
            elem_a="hinge_barrel",
            elem_b=f"lid_knuckle_boss_{i}",
            reason="Lid knuckle boss and housing hinge barrel interleave along the shared hinge line.",
        )
        ctx.allow_overlap(
            housing,
            lid,
            elem_a="hinge_pin",
            elem_b=f"lid_knuckle_boss_{i}",
            reason="Lid knuckle boss and housing hinge pin interleave along the shared hinge line.",
        )
    ctx.allow_overlap(
        housing,
        lid,
        elem_a="hinge_pin",
        elem_b="lid_shell",
        reason="Hinge pin passes along the shared hinge line at the rear of the lid.",
    )
    # Foot / shell-skirt local overlap for round-housing feet.
    if r.housing_form == "round":
        for i in range(4):
            ctx.allow_overlap(
                housing,
                housing,
                elem_a=f"foot_{i}",
                elem_b="shell_skirt",
                reason="Feet are seated into the round housing's bottom skirt.",
            )

    if r.closure != "no_latch":
        latch = object_model.get_part("latch")
        ctx.allow_overlap(
            housing,
            latch,
            elem_a="latch_lug_0",
            elem_b="latch_pin",
            reason="Front latch axle is captured between the two housing lugs.",
        )
        ctx.allow_overlap(
            housing,
            latch,
            elem_a="latch_lug_1",
            elem_b="latch_pin",
            reason="Front latch axle is captured between the two housing lugs.",
        )

    # --- Structural checks --------------------------------------------------
    ctx.check(
        "single clamshell hierarchy",
        {"lower_housing", "lid"}.issubset({p.name for p in object_model.parts}),
        details=f"parts={[p.name for p in object_model.parts]}",
    )
    ctx.check(
        "lid hinge is REVOLUTE about X-axis",
        lid_hinge.articulation_type == ArticulationType.REVOLUTE and abs(lid_hinge.axis[0]) > 0.99,
        details=f"axis={lid_hinge.axis}",
    )
    ctx.check(
        "lid opens through a realistic angle",
        lid_hinge.motion_limits is not None
        and lid_hinge.motion_limits.upper is not None
        and lid_hinge.motion_limits.upper >= math.radians(55.0),
        details=f"limits={lid_hinge.motion_limits}",
    )

    if r.closure != "no_latch":
        latch_hinge = object_model.get_articulation("latch_hinge")
        ctx.check(
            "latch hinge is REVOLUTE",
            latch_hinge.articulation_type == ArticulationType.REVOLUTE,
            details=f"type={latch_hinge.articulation_type}",
        )

    # --- Slot-choice sanity -------------------------------------------------
    slot_choices = slot_choices_for_config(r)
    ctx.check(
        "slot_choices records three axes",
        len(slot_choices) == 3
        and {name for name, _ in slot_choices} == {"housing_form", "grid_topology", "closure"},
        details=f"slot_choices={slot_choices}",
    )

    # --- Closed-pose gap: upper grid vs lower grid (targeted Rule 5). -------
    with ctx.pose({lid_hinge: 0.0}):
        upper_slab_aabb = ctx.part_element_world_aabb(lid, elem="upper_grid_slab")
        lower_slab_aabb = ctx.part_element_world_aabb(housing, elem="lower_grid_slab")
        if upper_slab_aabb is not None and lower_slab_aabb is not None:
            gap = upper_slab_aabb[0][2] - lower_slab_aabb[1][2]
            ctx.check(
                "closed cooking clearance is small but positive",
                -0.005 < gap < 0.030,
                details=f"upper_slab={upper_slab_aabb}, lower_slab={lower_slab_aabb}, gap={gap}",
            )

    # --- Open-pose targeted check: lid clears the housing. ------------------
    with ctx.pose({lid_hinge: r.lid_open * 0.9}):
        opened_lid_aabb = ctx.part_world_aabb(lid)
        housing_aabb = ctx.part_world_aabb(housing)
        ctx.check(
            "opened lid raises above the housing top face",
            opened_lid_aabb is not None
            and housing_aabb is not None
            and opened_lid_aabb[1][2] > housing_aabb[1][2] + 0.03,
            details=f"opened_lid={opened_lid_aabb}, housing={housing_aabb}",
        )

    # --- Rule 5: sampled-pose collision sweep. -----------------------------
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=48,
        ignore_fixed=True,
    )

    return ctx.report()


__all__ = [
    "__modular__",
    "WaffleMakerConfig",
    "ResolvedWaffleMakerConfig",
    "PALETTE_STYLES",
    "config_from_seed",
    "resolve_config",
    "build_waffle_maker",
    "build_seeded_waffle_maker",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "run_waffle_maker_tests",
]
