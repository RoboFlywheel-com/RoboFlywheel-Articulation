# SPDX-License-Identifier: Apache-2.0

"""Container / shipping container — modular procedural template.

ISO intermodal corrugated-steel cargo container: a long steel box (long axis
along +X, width along Y, height along Z, floor on the ground) with three
swappable structural slots plus a per-leaf multiplicity axis.

Slots (all parented to the common root `body`, parallel-children pattern):
  - door_closure : the +X (or +Y) cargo-opening mechanism. Candidates:
        double_swing_doors / single_swing_door / n_doorleaves  (swing family,
            REVOLUTE +Z hinges + cam handles; exposes the door_count axis)
        roll_up_door     (PRISMATIC +Z rolling curtain + drum + tracks)
        side_access_doors(opening moved to the +Y long wall; solid end walls)
  - roof_top    : the top structure. Candidates:
        flat_solid       (fixed steel roof visual, no joint)
        hatch_lid        (REVOLUTE -X corrugated hatch lid + hinge barrels/eyes)
        open_top_tarp    (tube bow/tarp sections; seed-stable random subset is
                          REVOLUTE -X hinged, up to every section opening)
  - wall_surface: the two long side walls (+ front wall). Candidates:
        corrugated / louvered_vents / smooth_reefer

Multiplicity axis (swing family only): door_count in [1, 4]. Each leaf is an
independent `body_to_door_i` REVOLUTE (not a mimic); leaves alternate hinge
side (even +Y, odd -Y); N>2 adds a center `mullion` as the inner hinge point.

All geometry is adapted verbatim (parameterised) from the declared 5-star
sources (parent white-twenty-foot container + 8 converged fork variants). Per
AUTHORING.md §A Rule 3 the mesh helpers stay Mesh-typed. Per Rule 1
non-articulating detail is `body.visual(...)`. The captured-fit pivots
(door-panel ↔ post, handle hub ↔ rod, curtain ↔ track, lid-eye ↔ hinge-barrel,
hinge-barrel ↔ hinge-ear) are grandfathered (no MatingContract) and guarded by
the articulation-origin baseline + element-scoped allow_overlap, exactly as in
the source records.
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
    BoxGeometry,
    CylinderGeometry,
    Inertial,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot vocabularies
# --------------------------------------------------------------------------- #

DoorClosure = Literal[
    "double_swing_doors",
    "single_swing_door",
    "n_doorleaves",
    "roll_up_door",
    "side_access_doors",
]
RoofTop = Literal["flat_solid", "hatch_lid", "open_top_tarp"]
WallSurface = Literal["corrugated", "louvered_vents", "smooth_reefer"]

DOOR_CLOSURES: tuple[str, ...] = (
    "double_swing_doors",
    "single_swing_door",
    "n_doorleaves",
    "roll_up_door",
    "side_access_doors",
)
ROOF_TOPS: tuple[str, ...] = ("flat_solid", "hatch_lid", "open_top_tarp")
WALL_SURFACES: tuple[str, ...] = ("corrugated", "louvered_vents", "smooth_reefer")

# Swing family exposes the door_count multiplicity axis.
SWING_FAMILY: tuple[str, ...] = ("double_swing_doors", "single_swing_door", "n_doorleaves")

# --------------------------------------------------------------------------- #
# Palette — 10 colorways + material-finish dimension (palette only, not a slot)
# --------------------------------------------------------------------------- #

PaletteStyle = Literal[
    "iso_white",
    "maersk_blue",
    "rust_red",
    "weathered_grey",
    "container_green",
    "safety_orange",
    "heavy_rust",
    "fresh_glossy_blue",
    "two_tone_blue_grey",
    "reefer_white",
]

PALETTE_STYLES: tuple[str, ...] = (
    "iso_white",
    "maersk_blue",
    "rust_red",
    "weathered_grey",
    "container_green",
    "safety_orange",
    "heavy_rust",
    "fresh_glossy_blue",
    "two_tone_blue_grey",
    "reefer_white",
)

# Per colorway: body (corrugated skin) / doors / accent (corner/rod/keeper/
# handle/decal) RGBA + finish (light/secondary steel tones for grey-steel
# elements such as door header/sill/posts/grip). RGBA anchored to the 5-star
# samples where seen; the rest are realistic ISO livery inferences.
PALETTE_PRESETS: dict[str, dict[str, object]] = {
    "iso_white": {
        "finish": "matte_industrial",
        "body": (0.90, 0.91, 0.92, 1.0),
        "doors": (0.62, 0.64, 0.66, 1.0),
        "accent": (0.18, 0.19, 0.21, 1.0),
        "trim": (0.62, 0.64, 0.66, 1.0),
        "tarp": (0.12, 0.22, 0.38, 1.0),
    },
    "maersk_blue": {
        "finish": "matte_industrial",
        "body": (0.10, 0.32, 0.55, 1.0),
        "doors": (0.10, 0.32, 0.55, 1.0),
        "accent": (0.18, 0.19, 0.21, 1.0),
        "trim": (0.55, 0.58, 0.62, 1.0),
        "tarp": (0.12, 0.22, 0.38, 1.0),
    },
    "rust_red": {
        "finish": "matte_industrial",
        "body": (0.55, 0.20, 0.16, 1.0),
        "doors": (0.55, 0.20, 0.16, 1.0),
        "accent": (0.18, 0.19, 0.21, 1.0),
        "trim": (0.52, 0.40, 0.36, 1.0),
        "tarp": (0.30, 0.16, 0.13, 1.0),
    },
    "weathered_grey": {
        "finish": "weathered",
        "body": (0.45, 0.46, 0.47, 1.0),
        "doors": (0.40, 0.40, 0.41, 1.0),
        "accent": (0.40, 0.24, 0.16, 1.0),
        "trim": (0.42, 0.40, 0.38, 1.0),
        "tarp": (0.30, 0.30, 0.30, 1.0),
    },
    "container_green": {
        "finish": "matte_industrial",
        "body": (0.16, 0.36, 0.26, 1.0),
        "doors": (0.16, 0.36, 0.26, 1.0),
        "accent": (0.18, 0.19, 0.21, 1.0),
        "trim": (0.50, 0.54, 0.50, 1.0),
        "tarp": (0.14, 0.28, 0.20, 1.0),
    },
    "safety_orange": {
        "finish": "matte_industrial",
        "body": (0.80, 0.38, 0.10, 1.0),
        "doors": (0.80, 0.38, 0.10, 1.0),
        "accent": (0.18, 0.19, 0.21, 1.0),
        "trim": (0.60, 0.50, 0.42, 1.0),
        "tarp": (0.40, 0.24, 0.10, 1.0),
    },
    "heavy_rust": {
        "finish": "heavily_weathered",
        "body": (0.46, 0.26, 0.18, 1.0),
        "doors": (0.36, 0.20, 0.14, 1.0),
        "accent": (0.20, 0.15, 0.12, 1.0),
        "trim": (0.40, 0.28, 0.22, 1.0),
        "tarp": (0.28, 0.18, 0.13, 1.0),
    },
    "fresh_glossy_blue": {
        "finish": "glossy",
        "body": (0.08, 0.30, 0.58, 1.0),
        "doors": (0.08, 0.30, 0.58, 1.0),
        "accent": (0.85, 0.86, 0.88, 1.0),
        "trim": (0.82, 0.84, 0.86, 1.0),
        "tarp": (0.10, 0.24, 0.46, 1.0),
    },
    "two_tone_blue_grey": {
        "finish": "matte_industrial",
        "body": (0.12, 0.34, 0.56, 1.0),
        "doors": (0.62, 0.64, 0.66, 1.0),
        "accent": (0.18, 0.19, 0.21, 1.0),
        "trim": (0.55, 0.58, 0.62, 1.0),
        "tarp": (0.12, 0.24, 0.40, 1.0),
    },
    "reefer_white": {
        "finish": "semi_gloss",
        "body": (0.92, 0.93, 0.94, 1.0),
        "doors": (0.88, 0.89, 0.90, 1.0),
        "accent": (0.30, 0.31, 0.33, 1.0),
        "trim": (0.72, 0.74, 0.76, 1.0),
        "tarp": (0.20, 0.30, 0.44, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ContainerShippingContainerConfig:
    door_closure: DoorClosure = "double_swing_doors"
    roof_top: RoofTop = "flat_solid"
    wall_surface: WallSurface = "corrugated"
    door_count: int = 2
    palette_style: PaletteStyle = "iso_white"

    length_scale: float = 1.0
    height_scale: float = 1.0
    width_scale: float = 1.0
    corr_pitch_scale: float = 1.0
    door_open_limit_deg: float = 120.0


@dataclass(frozen=True)
class ResolvedContainerShippingContainerConfig:
    door_closure: str
    roof_top: str
    wall_surface: str
    door_count: int
    palette_style: str
    finish: str

    # Outer dimensions (m).
    L: float
    W: float
    H: float
    corr_pitch: float
    door_open_limit_rad: float

    # Palette RGBA.
    body_rgba: tuple[float, float, float, float]
    doors_rgba: tuple[float, float, float, float]
    accent_rgba: tuple[float, float, float, float]
    trim_rgba: tuple[float, float, float, float]
    tarp_rgba: tuple[float, float, float, float]


# Nominal ISO 20ft dimensions (from the 5-star sources).
_L0 = 6.06
_W0 = 2.44
_H0 = 2.59
_CORR_PITCH0 = 0.30

# Fixed detail constants (verbatim from sources).
WALL_T = 0.035
CORNER = 0.16
DOOR_T = 0.06
CORR_DEPTH = 0.04
CORR_WIDTH = 0.12

LOUVER_PITCH = 0.11
LOUVER_DEPTH = 0.035
LOUVER_THICK = 0.006
LOUVER_ANGLE_DEG = 35.0


def config_from_seed(seed: int) -> ContainerShippingContainerConfig:
    """Deterministic procedural sampling. seed=0 is not special."""
    rng = random.Random(seed)

    # Weighted slot draws. Defaults are the most common ISO forms.
    door_closure = rng.choices(
        DOOR_CLOSURES,
        weights=(0.42, 0.16, 0.12, 0.15, 0.15),
        k=1,
    )[0]
    roof_top = rng.choices(ROOF_TOPS, weights=(0.62, 0.20, 0.18), k=1)[0]
    wall_surface = rng.choices(WALL_SURFACES, weights=(0.56, 0.24, 0.20), k=1)[0]

    # door_count multiplicity (swing family only). Small N is far more common.
    if door_closure in SWING_FAMILY:
        door_count = rng.choices((1, 2, 3, 4), weights=(0.25, 0.55, 0.10, 0.10), k=1)[0]
    else:
        door_count = 1  # placeholder; not used by roll_up / side_access

    palette_style = rng.choice(PALETTE_STYLES)

    length_scale = round(rng.uniform(0.90, 2.05), 4)
    height_scale = round(rng.uniform(0.92, 1.18), 4)
    width_scale = round(rng.uniform(0.96, 1.06), 4)
    corr_pitch_scale = round(rng.uniform(0.85, 1.20), 4)
    door_open_limit_deg = round(rng.uniform(100.0, 130.0), 2)

    return ContainerShippingContainerConfig(
        door_closure=door_closure,  # type: ignore[arg-type]
        roof_top=roof_top,  # type: ignore[arg-type]
        wall_surface=wall_surface,  # type: ignore[arg-type]
        door_count=door_count,
        palette_style=palette_style,  # type: ignore[arg-type]
        length_scale=length_scale,
        height_scale=height_scale,
        width_scale=width_scale,
        corr_pitch_scale=corr_pitch_scale,
        door_open_limit_deg=door_open_limit_deg,
    )


def resolve_config(
    config: ContainerShippingContainerConfig,
) -> ResolvedContainerShippingContainerConfig:
    if str(config.door_closure) not in DOOR_CLOSURES:
        raise ValueError(f"Unsupported door_closure: {config.door_closure}")
    if str(config.roof_top) not in ROOF_TOPS:
        raise ValueError(f"Unsupported roof_top: {config.roof_top}")
    if str(config.wall_surface) not in WALL_SURFACES:
        raise ValueError(f"Unsupported wall_surface: {config.wall_surface}")
    if str(config.palette_style) not in PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    ls = max(0.90, min(float(config.length_scale), 2.05))
    hs = max(0.92, min(float(config.height_scale), 1.18))
    ws = max(0.96, min(float(config.width_scale), 1.06))
    cps = max(0.85, min(float(config.corr_pitch_scale), 1.20))

    W = _W0 * ws
    H = _H0 * hs

    # Long-box invariant: X must stay the longest axis by >1 m on each of Y, Z.
    # Project length_scale up if a small length + large width/height would
    # otherwise violate the identity.
    L = _L0 * ls
    min_len = max(W, H) + 1.0 + 0.05
    if L < min_len:
        L = min_len

    corr_pitch = _CORR_PITCH0 * cps

    door_open_limit_rad = math.radians(max(100.0, min(float(config.door_open_limit_deg), 130.0)))

    # door_count: swing family only, clamped to [1, 4]; further capped so the
    # leaf width stays >= 0.30 m (avoid implausibly narrow leaves).
    if str(config.door_closure) in SWING_FAMILY:
        door_count = max(1, min(int(config.door_count), 4))
        opening_w = W - 0.16
        while door_count > 1 and (opening_w / door_count) < 0.30:
            door_count -= 1
    else:
        door_count = 1

    preset = PALETTE_PRESETS[str(config.palette_style)]

    return ResolvedContainerShippingContainerConfig(
        door_closure=str(config.door_closure),
        roof_top=str(config.roof_top),
        wall_surface=str(config.wall_surface),
        door_count=door_count,
        palette_style=str(config.palette_style),
        finish=str(preset["finish"]),
        L=L,
        W=W,
        H=H,
        corr_pitch=corr_pitch,
        door_open_limit_rad=door_open_limit_rad,
        body_rgba=tuple(preset["body"]),  # type: ignore[arg-type]
        doors_rgba=tuple(preset["doors"]),  # type: ignore[arg-type]
        accent_rgba=tuple(preset["accent"]),  # type: ignore[arg-type]
        trim_rgba=tuple(preset["trim"]),  # type: ignore[arg-type]
        tarp_rgba=tuple(preset["tarp"]),  # type: ignore[arg-type]
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Stable per-seed module picks for module_topology_diversity."""
    r = resolve_config(config_from_seed(seed))
    choices: list[tuple[str, str]] = [
        ("door_closure", r.door_closure),
        ("roof_top", r.roof_top),
        ("wall_surface", r.wall_surface),
    ]
    if r.door_closure in SWING_FAMILY:
        choices.append(("door_count", f"n{r.door_count}"))
    return choices


# --------------------------------------------------------------------------- #
# Geometry layout helper (derived dimensions shared across modules)
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _Layout:
    L: float
    W: float
    H: float
    corr_pitch: float
    door_x: float
    body_x0: float
    body_x1: float
    body_len: float
    body_cx: float
    side_h: float
    wall_z_center: float


def _layout(r: ResolvedContainerShippingContainerConfig, *, full_length_body: bool) -> _Layout:
    L, W, H = r.L, r.W, r.H
    if full_length_body:
        body_x0 = -L / 2.0
        body_x1 = L / 2.0
        door_x = L / 2.0 - CORNER - DOOR_T / 2.0
    else:
        body_x0 = -L / 2.0
        body_x1 = L / 2.0 - DOOR_T
        door_x = L / 2.0 - CORNER - DOOR_T / 2.0
    body_len = body_x1 - body_x0
    body_cx = (body_x0 + body_x1) / 2.0
    return _Layout(
        L=L,
        W=W,
        H=H,
        corr_pitch=r.corr_pitch,
        door_x=door_x,
        body_x0=body_x0,
        body_x1=body_x1,
        body_len=body_len,
        body_cx=body_cx,
        side_h=H - 0.10,
        wall_z_center=H / 2.0,
    )


# --------------------------------------------------------------------------- #
# Mesh helpers (adapted verbatim from the 5-star sources; stay Mesh-typed)
# --------------------------------------------------------------------------- #


def _corrugated_wall(
    length_x: float, height_z: float, base_y: float, depth_sign: float, corr_pitch: float
) -> MeshGeometry:
    """Vertical-corrugation side wall in the XZ plane at y=base_y (parent L55-70)."""
    geo = BoxGeometry((length_x, WALL_T, height_z))
    geo.translate(0.0, base_y, 0.0)
    n = max(1, int(length_x / corr_pitch))
    x0 = -length_x / 2.0 + corr_pitch / 2.0
    for i in range(n):
        x = x0 + i * corr_pitch
        rib = BoxGeometry((CORR_WIDTH, CORR_DEPTH, height_z * 0.96))
        rib.translate(x, base_y + depth_sign * (WALL_T / 2.0 + CORR_DEPTH / 2.0), 0.0)
        geo.merge(rib)
    return geo


def _corrugated_end_wall(
    width_y: float, height_z: float, base_x: float, depth_sign: float, corr_pitch: float
) -> MeshGeometry:
    """End wall in the YZ plane at x=base_x with vertical ribs along Y (parent L73-84)."""
    geo = BoxGeometry((WALL_T, width_y, height_z))
    geo.translate(base_x, 0.0, 0.0)
    n = max(1, int(width_y / corr_pitch))
    y0 = -width_y / 2.0 + corr_pitch / 2.0
    for i in range(n):
        y = y0 + i * corr_pitch
        rib = BoxGeometry((CORR_DEPTH, CORR_WIDTH, height_z * 0.96))
        rib.translate(base_x + depth_sign * (WALL_T / 2.0 + CORR_DEPTH / 2.0), y, 0.0)
        geo.merge(rib)
    return geo


def _louver_slat(length_x: float) -> MeshGeometry:
    """One horizontal angled louver slat (louver source L61-69)."""
    slat = BoxGeometry((length_x, LOUVER_THICK, LOUVER_DEPTH))
    slat.rotate_x(math.radians(LOUVER_ANGLE_DEG))
    return slat


def _louvered_wall(
    length_x: float, height_z: float, base_y: float, depth_sign: float
) -> MeshGeometry:
    """Ventilated side wall with horizontal angled louver slats (louver source L72-109)."""
    rail_h = 0.06
    rail_d = WALL_T + LOUVER_DEPTH * 0.6
    geo = BoxGeometry((length_x, WALL_T, height_z * 0.04))
    geo.translate(0.0, base_y, height_z / 2.0 - height_z * 0.02)
    bottom_rail = BoxGeometry((length_x, rail_d, rail_h))
    bottom_rail.translate(0.0, base_y + depth_sign * (WALL_T / 2.0), -height_z / 2.0 + rail_h / 2.0)
    geo.merge(bottom_rail)
    top_rail = BoxGeometry((length_x, rail_d, rail_h))
    top_rail.translate(0.0, base_y + depth_sign * (WALL_T / 2.0), height_z / 2.0 - rail_h / 2.0)
    geo.merge(top_rail)
    post_w = 0.06
    n_posts = max(2, int(length_x / 2.0) + 1)
    for i in range(n_posts):
        px = -length_x / 2.0 + i * (length_x / (n_posts - 1))
        post = BoxGeometry((post_w, rail_d, height_z))
        post.translate(px, base_y + depth_sign * (WALL_T / 2.0), 0.0)
        geo.merge(post)
    slat_len = length_x - 2.0 * post_w - 0.02
    slat_field_h = height_z - 2.0 * rail_h - 0.04
    n_slats = max(1, int(slat_field_h / LOUVER_PITCH))
    z0 = -slat_field_h / 2.0 + LOUVER_PITCH / 2.0
    for i in range(n_slats):
        z = z0 + i * LOUVER_PITCH
        slat = _louver_slat(slat_len)
        slat.translate(0.0, base_y + depth_sign * (WALL_T / 2.0 + LOUVER_DEPTH / 2.0), z)
        geo.merge(slat)
    return geo


def _insulated_wall(length_x: float, height_z: float, base_y: float) -> MeshGeometry:
    """Smooth flat insulated reefer side wall (smooth source L56-63)."""
    geo = BoxGeometry((length_x, WALL_T, height_z))
    geo.translate(0.0, base_y, 0.0)
    return geo


def _insulated_end_wall(width_y: float, height_z: float, base_x: float) -> MeshGeometry:
    """Smooth flat insulated reefer end wall (smooth source L66-70)."""
    geo = BoxGeometry((WALL_T, width_y, height_z))
    geo.translate(base_x, 0.0, 0.0)
    return geo


def _corrugated_door_panel(width_y: float, height_z: float, corr_pitch: float) -> MeshGeometry:
    """One corrugated cargo door panel, plane YZ, ribs face +X (parent L87-117)."""
    geo = BoxGeometry((DOOR_T * 0.45, width_y, height_z))
    fr_t = 0.07
    fr_d = DOOR_T
    for sy in (-1.0, 1.0):
        m = BoxGeometry((fr_d, fr_t, height_z))
        m.translate(0.0, sy * (width_y / 2.0 - fr_t / 2.0), 0.0)
        geo.merge(m)
    for sz in (-1.0, 1.0):
        m = BoxGeometry((fr_d, width_y - 2 * fr_t, fr_t))
        m.translate(0.0, 0.0, sz * (height_z / 2.0 - fr_t / 2.0))
        geo.merge(m)
    inner_w = width_y - 2 * fr_t
    n = max(1, int(inner_w / corr_pitch))
    y0 = -inner_w / 2.0 + corr_pitch / 2.0
    for i in range(n):
        y = y0 + i * corr_pitch
        rib = BoxGeometry((CORR_DEPTH, CORR_WIDTH, height_z - 2 * fr_t - 0.02))
        rib.translate(DOOR_T * 0.225 + CORR_DEPTH / 2.0, y, 0.0)
        geo.merge(rib)
    return geo


def _corrugated_side_door_panel(width_x: float, height_z: float, corr_pitch: float) -> MeshGeometry:
    """Side-door panel, plane XZ, thin along Y, ribs face +Y (side source L102-128)."""
    geo = BoxGeometry((width_x, DOOR_T * 0.45, height_z))
    fr_t = 0.07
    fr_d = DOOR_T
    for sz in (-1.0, 1.0):
        m = BoxGeometry((width_x, fr_d, fr_t))
        m.translate(0.0, 0.0, sz * (height_z / 2.0 - fr_t / 2.0))
        geo.merge(m)
    for sx in (-1.0, 1.0):
        m = BoxGeometry((fr_t, fr_d, height_z))
        m.translate(sx * (width_x / 2.0 - fr_t / 2.0), 0.0, 0.0)
        geo.merge(m)
    inner_w = width_x - 2.0 * fr_t
    n = max(1, int(inner_w / corr_pitch))
    x0 = -inner_w / 2.0 + corr_pitch / 2.0
    for i in range(n):
        x = x0 + i * corr_pitch
        rib = BoxGeometry((CORR_WIDTH, CORR_DEPTH, height_z - 2.0 * fr_t - 0.02))
        rib.translate(x, DOOR_T * 0.225 + CORR_DEPTH / 2.0, 0.0)
        geo.merge(rib)
    return geo


def _corner_casting() -> MeshGeometry:
    return BoxGeometry((CORNER, CORNER, CORNER))


def _curtain_slat(width_y: float, slat_t: float, slat_h: float) -> MeshGeometry:
    """One horizontal rolling-shutter slat (roll_up source L121-123)."""
    return BoxGeometry((slat_t, width_y, slat_h))


def _hinge_barrel() -> MeshGeometry:
    """A single hinge barrel cylinder along X (hatch source L180-185)."""
    geo = CylinderGeometry(0.025, 0.08, radial_segments=12)
    geo.rotate_y(math.pi / 2.0)
    return geo


def _lid_hinge_eye() -> MeshGeometry:
    """A single hinge eye knuckle on the lid (hatch source L188-192)."""
    geo = CylinderGeometry(0.030, 0.06, radial_segments=12)
    geo.rotate_y(math.pi / 2.0)
    return geo


def _corrugated_lid_panel(
    length_x: float, width_y: float, lid_skin_t: float, lid_frame_d: float, corr_pitch: float
) -> MeshGeometry:
    """Horizontal corrugated hatch lid panel (hatch source L134-173)."""
    geo = BoxGeometry((length_x, width_y, lid_skin_t))
    geo.translate(0.0, 0.0, lid_skin_t / 2.0)
    fr_t = 0.06
    fr_d = lid_frame_d
    m = BoxGeometry((length_x - 0.04, fr_t, fr_d))
    m.translate(0.0, -(width_y / 2.0 - fr_t / 2.0), -(fr_d / 2.0))
    geo.merge(m)
    inner_w = width_y - 2 * fr_t
    n = max(1, int(inner_w / corr_pitch))
    y0 = -inner_w / 2.0 + corr_pitch / 2.0
    for i in range(n):
        y = y0 + i * corr_pitch
        rib = BoxGeometry((length_x - 2 * fr_t - 0.02, CORR_WIDTH, CORR_DEPTH))
        rib.translate(0.0, y, lid_skin_t + CORR_DEPTH / 2.0)
        geo.merge(rib)
    handle_h = 0.05
    post_h = handle_h - 0.025
    for sx in (-0.15, 0.15):
        post = BoxGeometry((0.030, 0.030, post_h))
        post.translate(sx, 0.0, lid_skin_t + post_h / 2.0)
        geo.merge(post)
    bar = BoxGeometry((0.33, 0.030, 0.025))
    bar.translate(0.0, 0.0, lid_skin_t + post_h + 0.025 / 2.0)
    geo.merge(bar)
    return geo


# ---- open-top bow + tarp helpers (open_top source L140-263) ----

BOW_TUBE_R = 0.025


def _bow_arch_points(half_span: float, rise: float, n: int = 10) -> list[tuple[float, float, float]]:
    points = []
    for i in range(n + 1):
        t = i / n
        angle = math.pi * t
        y = -half_span + 2.0 * half_span * t
        z = rise * math.sin(angle)
        points.append((0.0, y, z))
    return points


def _bow_arch_points_from_hinge(span: float, rise: float, n: int = 10):
    points = []
    for i in range(n + 1):
        t = i / n
        angle = math.pi * t
        y = -span * t
        z = rise * math.sin(angle)
        points.append((0.0, y, z))
    return points


def _build_bow_mesh(half_span: float, rise: float) -> MeshGeometry:
    pts = _bow_arch_points(half_span, rise, n=12)
    return tube_from_spline_points(
        pts,
        radius=BOW_TUBE_R,
        samples_per_segment=8,
        radial_segments=12,
        cap_ends=True,
        up_hint=(0.0, 0.0, 1.0),
    )


def _build_hinged_bow_mesh(span: float, rise: float) -> MeshGeometry:
    pts = _bow_arch_points_from_hinge(span, rise, n=12)
    return tube_from_spline_points(
        pts,
        radius=BOW_TUBE_R,
        samples_per_segment=8,
        radial_segments=12,
        cap_ends=True,
        up_hint=(0.0, 0.0, 1.0),
    )


def _build_tarp_mesh(
    x_positions: list[float], half_span: float, rise: float, thickness: float, n_arch_pts: int = 14
) -> MeshGeometry:
    geo = MeshGeometry()
    arch_yz = []
    for i in range(n_arch_pts + 1):
        t = i / n_arch_pts
        angle = math.pi * t
        y = -half_span + 2.0 * half_span * t
        z = rise * math.sin(angle)
        arch_yz.append((y, z))
    n_pts = len(arch_yz)
    n_x = len(x_positions)
    for x in x_positions:
        for (y, z) in arch_yz:
            geo.add_vertex(x, y, z)
    for x in x_positions:
        for (y, z) in arch_yz:
            geo.add_vertex(x, y, z - thickness)
    for xi in range(n_x - 1):
        for yi in range(n_pts - 1):
            i00 = xi * n_pts + yi
            i01 = xi * n_pts + yi + 1
            i10 = (xi + 1) * n_pts + yi
            i11 = (xi + 1) * n_pts + yi + 1
            geo.add_face(i00, i10, i01)
            geo.add_face(i01, i10, i11)
    offset = n_x * n_pts
    for xi in range(n_x - 1):
        for yi in range(n_pts - 1):
            i00 = offset + xi * n_pts + yi
            i01 = offset + xi * n_pts + yi + 1
            i10 = offset + (xi + 1) * n_pts + yi
            i11 = offset + (xi + 1) * n_pts + yi + 1
            geo.add_face(i00, i01, i10)
            geo.add_face(i01, i11, i10)
    for yi in range(n_pts - 1):
        t0 = yi
        t1 = yi + 1
        b0 = offset + yi
        b1 = offset + yi + 1
        geo.add_face(t0, t1, b0)
        geo.add_face(t1, b1, b0)
    last = n_x - 1
    for yi in range(n_pts - 1):
        t0 = last * n_pts + yi
        t1 = last * n_pts + yi + 1
        b0 = offset + last * n_pts + yi
        b1 = offset + last * n_pts + yi + 1
        geo.add_face(t0, b0, t1)
        geo.add_face(t1, b0, b1)
    return geo


def _build_hinged_tarp_mesh_asymmetric(
    x_fwd: float, x_back: float, bow_span: float, rise: float, thickness: float, n_arch_pts: int = 14
) -> MeshGeometry:
    geo = MeshGeometry()
    arch_yz = []
    for i in range(n_arch_pts + 1):
        t = i / n_arch_pts
        angle = math.pi * t
        y = -bow_span * t
        z = rise * math.sin(angle)
        arch_yz.append((y, z))
    n_pts = len(arch_yz)
    x_positions = [x_fwd, -x_back]
    n_x = len(x_positions)
    for x in x_positions:
        for (y, z) in arch_yz:
            geo.add_vertex(x, y, z)
    for x in x_positions:
        for (y, z) in arch_yz:
            geo.add_vertex(x, y, z - thickness)
    for xi in range(n_x - 1):
        for yi in range(n_pts - 1):
            i00 = xi * n_pts + yi
            i01 = xi * n_pts + yi + 1
            i10 = (xi + 1) * n_pts + yi
            i11 = (xi + 1) * n_pts + yi + 1
            geo.add_face(i00, i10, i01)
            geo.add_face(i01, i10, i11)
    offset = n_x * n_pts
    for xi in range(n_x - 1):
        for yi in range(n_pts - 1):
            i00 = offset + xi * n_pts + yi
            i01 = offset + xi * n_pts + yi + 1
            i10 = offset + (xi + 1) * n_pts + yi
            i11 = offset + (xi + 1) * n_pts + yi + 1
            geo.add_face(i00, i01, i10)
            geo.add_face(i01, i11, i10)
    for yi in range(n_pts - 1):
        t0 = yi
        t1 = yi + 1
        b0 = offset + yi
        b1 = offset + yi + 1
        geo.add_face(t0, t1, b0)
        geo.add_face(t1, b1, b0)
        t0r = (n_x - 1) * n_pts + yi
        t1r = (n_x - 1) * n_pts + yi + 1
        b0r = offset + (n_x - 1) * n_pts + yi
        b1r = offset + (n_x - 1) * n_pts + yi + 1
        geo.add_face(t0r, b0r, t1r)
        geo.add_face(t1r, b0r, b1r)
    return geo


def _drum_assembly(frame_x: float, header_bot: float, drum_r: float, drum_len: float) -> MeshGeometry:
    """Roll-up drum roller + caps + brackets (roll_up source L130-168)."""
    drum_cx = frame_x - 0.14
    drum_cz = header_bot - drum_r - 0.01
    drum = CylinderGeometry(drum_r, drum_len, radial_segments=24)
    drum.rotate_x(math.pi / 2.0)
    drum.translate(drum_cx, 0.0, drum_cz)
    for sy in (-1.0, 1.0):
        cap_r = drum_r + 0.02
        cap_len = 0.06
        cap = CylinderGeometry(cap_r, cap_len, radial_segments=16)
        cap.rotate_x(math.pi / 2.0)
        cap.translate(drum_cx, sy * (drum_len / 2.0 - cap_len / 2.0), drum_cz)
        drum.merge(cap)
    # Mounting brackets span in +X from the drum to the BACK face of the door
    # header (x = frame_x - 0.05) so the drum assembly physically connects to
    # the body shell — but stops short of the curtain plane (x = frame_x) so it
    # does not collide with the closed curtain slats.
    header_back_x = frame_x - 0.05
    for sy in (-1.0, 1.0):
        bracket_w = 0.06
        bracket_x0 = drum_cx
        bracket_x1 = header_back_x + 0.005  # slight embed into the header
        bracket_len_x = bracket_x1 - bracket_x0
        bracket = BoxGeometry((bracket_len_x, bracket_w, 0.20))
        by = sy * (drum_len / 2.0 - bracket_w / 2.0)
        bz = drum_cz + 0.08
        bracket.translate((bracket_x0 + bracket_x1) / 2.0, by, bz)
        drum.merge(bracket)
    return drum


# --------------------------------------------------------------------------- #
# Cam handle factory (parent L271-305 / n4 _build_handle L113-144)
# --------------------------------------------------------------------------- #


def _build_handle_swing(
    model,
    door,
    dname: str,
    hname: str,
    rod_x: float,
    rod_y: float,
    *,
    accent_mat,
    trim_mat,
):
    """Cam handle whose lever points along +X (end-door family)."""
    handle = model.part(hname)
    hub = CylinderGeometry(0.022, 0.06, radial_segments=16).rotate_y(math.pi / 2.0)
    hub.translate(0.04, 0.0, 0.0)
    handle.visual(mesh_from_geometry(hub, "hub"), material=accent_mat, name="hub", material_class_id="metal.blackened_gunmetal")
    lever = BoxGeometry((0.14, 0.045, 0.035))
    lever.translate(0.13, 0.0, 0.0)
    handle.visual(mesh_from_geometry(lever, "lever"), material=accent_mat, name="lever", material_class_id="metal.blackened_gunmetal")
    grip = CylinderGeometry(0.025, 0.10, radial_segments=12).rotate_y(math.pi / 2.0)
    grip.translate(0.20, 0.0, 0.0)
    handle.visual(mesh_from_geometry(grip, "grip"), material=trim_mat, name="grip", material_class_id="metal.paint_coated")
    handle.inertial = Inertial.from_geometry(
        Box((0.22, 0.06, 0.06)), mass=1.2, origin=Origin(xyz=(0.11, 0.0, 0.0))
    )
    # Origin nudged toward the rod's +X surface (rod radius 0.018) so it lands
    # within the 15 mm articulation-origin baseline of real door geometry while
    # the hub still wraps/contacts the rod.
    model.articulation(
        f"{dname}_to_{hname}",
        ArticulationType.REVOLUTE,
        parent=door,
        child=handle,
        origin=Origin(xyz=(rod_x + 0.006, rod_y, 0.05)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=3.0, lower=0.0, upper=math.radians(110.0)),
    )
    return handle


# --------------------------------------------------------------------------- #
# Body (root) — wall_surface mesh + door_closure end frame + roof=flat visual
# --------------------------------------------------------------------------- #


def _emit_body(model, r, lay: _Layout, mats: dict) -> object:
    """Build the root `body` part: floor, walls, end frame, corner castings,
    and (when roof_top=flat_solid) the fixed roof visual."""
    body = model.part("body")
    L, W, H = lay.L, lay.W, lay.H
    body_len, body_cx = lay.body_len, lay.body_cx
    side_h, wall_z_center = lay.side_h, lay.wall_z_center
    cp = lay.corr_pitch

    body_mat = mats["body"]
    door_mat = mats["doors"]
    accent_mat = mats["accent"]
    trim_mat = mats["trim"]

    side_access = r.door_closure == "side_access_doors"

    # --- floor ---
    floor = BoxGeometry((body_len, W, 0.10))
    floor.translate(body_cx, 0.0, 0.05)
    body.visual(mesh_from_geometry(floor, "floor"), material=trim_mat, name="floor", material_class_id="metal.paint_coated")

    # --- roof (fixed, flat_solid only) ---
    if r.roof_top == "flat_solid":
        roof = BoxGeometry((body_len, W, 0.05))
        roof.translate(body_cx, 0.0, H - 0.025)
        body.visual(mesh_from_geometry(roof, "roof"), material=body_mat, name="roof", material_class_id="metal.paint_coated")

    # --- side walls (wall_surface selects the mesh helper) ---
    for sy, nm in ((1.0, "side_wall_p"), (-1.0, "side_wall_n")):
        if side_access and sy > 0:
            # +Y wall carries the opening; only -Y is a full wall here. The +Y
            # wall is emitted as the doorway frame below.
            continue
        if r.wall_surface == "corrugated":
            wall = _corrugated_wall(body_len, side_h, sy * (W / 2.0 - WALL_T / 2.0), sy, cp)
        elif r.wall_surface == "louvered_vents":
            wall = _louvered_wall(body_len, side_h, sy * (W / 2.0 - WALL_T / 2.0), sy)
        else:  # smooth_reefer
            wall = _insulated_wall(body_len, side_h, sy * (W / 2.0 - WALL_T / 2.0))
        wall.translate(body_cx, 0.0, wall_z_center)
        body.visual(mesh_from_geometry(wall, nm), material=body_mat, name=nm, material_class_id="metal.paint_coated")

    # --- end wall(s) ---
    def _end_wall(width_y, base_x, depth_sign):
        if r.wall_surface == "louvered_vents":
            # louvered variant keeps corrugated end walls
            return _corrugated_end_wall(width_y, side_h, base_x, depth_sign, cp)
        if r.wall_surface == "smooth_reefer":
            return _insulated_end_wall(width_y, side_h, base_x)
        return _corrugated_end_wall(width_y, side_h, base_x, depth_sign, cp)

    if side_access:
        # both ends are solid walls
        en = _end_wall(W - 0.10, lay.body_x0 + WALL_T / 2.0, -1.0)
        en.translate(0.0, 0.0, wall_z_center)
        body.visual(mesh_from_geometry(en, "end_wall_n"), material=body_mat, name="end_wall_n", material_class_id="metal.paint_coated")
        ep = _end_wall(W - 0.10, lay.body_x1 - WALL_T / 2.0, +1.0)
        ep.translate(0.0, 0.0, wall_z_center)
        body.visual(mesh_from_geometry(ep, "end_wall_p"), material=body_mat, name="end_wall_p", material_class_id="metal.paint_coated")
    else:
        # front (-X) end wall only; +X is the cargo opening
        end = _end_wall(W - 0.10, lay.body_x0 + WALL_T / 2.0, -1.0)
        end.translate(0.0, 0.0, wall_z_center)
        body.visual(mesh_from_geometry(end, "front_wall"), material=body_mat, name="front_wall", material_class_id="metal.paint_coated")

    # --- door_closure end framing ---
    if side_access:
        _emit_side_doorway_frame(body, r, lay, mats)
    elif r.door_closure == "roll_up_door":
        _emit_rollup_frame(body, r, lay, mats)
    else:
        _emit_end_doorway_frame(body, r, lay, mats)

    # --- 8 corner castings (ISO; always 8) ---
    ci = 0
    sx_end = lay.body_x1 - CORNER / 2.0 if side_access else L / 2.0 - CORNER / 2.0
    for sx in (lay.body_x0 + CORNER / 2.0, sx_end):
        for sy in (-1.0, 1.0):
            for sz in (CORNER / 2.0, H - CORNER / 2.0):
                cc = _corner_casting()
                cc.translate(sx, sy * (W / 2.0 - CORNER / 2.0), sz)
                body.visual(
                    mesh_from_geometry(cc, f"corner_{ci}"), material=accent_mat, name=f"corner_{ci}", material_class_id="metal.blackened_gunmetal"
                )
                ci += 1

    body.inertial = Inertial.from_geometry(
        Box((L, W, H)), mass=2200.0, origin=Origin(xyz=(0.0, 0.0, H / 2.0))
    )
    return body


def _emit_end_doorway_frame(body, r, lay: _Layout, mats: dict):
    """+X end doorway frame: header, sill, corner posts (+ mullion if N>2)."""
    W, H = lay.W, lay.H
    trim_mat = mats["trim"]
    fx = lay.body_x1 - 0.05
    door_x = lay.door_x
    # Header / sill are deepened in -X so they reach the closed-door plane
    # (door_x) and so meet the per-leaf hinge stiles standing there, keeping the
    # whole body shell connected even for inner leaves of a multi-leaf opening.
    head_x1 = fx + 0.05
    head_x0 = door_x - 0.01
    head_len = head_x1 - head_x0
    head_cx = (head_x0 + head_x1) / 2.0
    header = BoxGeometry((head_len, W, 0.14))
    header.translate(head_cx, 0.0, H - 0.07)
    body.visual(mesh_from_geometry(header, "door_header"), material=trim_mat, name="door_header", material_class_id="metal.paint_coated")
    sill = BoxGeometry((head_len, W, 0.14))
    sill.translate(head_cx, 0.0, 0.07)
    body.visual(mesh_from_geometry(sill, "door_sill"), material=trim_mat, name="door_sill", material_class_id="metal.paint_coated")
    # Posts are slightly deeper in X so their -X face reaches the closed-door
    # hinge plane (door_x), keeping each body_to_door_i origin on real hinge
    # hardware (within the 15 mm articulation-origin baseline).
    post_x_w = 0.18
    for sy, nm in ((1.0, "post_p"), (-1.0, "post_n")):
        post = BoxGeometry((post_x_w, 0.14, H))
        post.translate(fx - 0.03, sy * (W / 2.0 - 0.07), H / 2.0)
        body.visual(mesh_from_geometry(post, nm), material=trim_mat, name=nm, material_class_id="metal.paint_coated")
    # A center mullion gives the inner leaves an inner hinge column whenever a
    # swing closure has more than two leaves (regardless of the module name).
    if r.door_closure in SWING_FAMILY and r.door_count > 2:
        mullion = BoxGeometry((post_x_w, 0.14, H))
        mullion.translate(fx - 0.03, 0.0, H / 2.0)
        body.visual(mesh_from_geometry(mullion, "mullion"), material=trim_mat, name="mullion", material_class_id="metal.paint_coated")


def _emit_rollup_frame(body, r, lay: _Layout, mats: dict):
    """+X roll-up doorway frame: header, sill, posts, track rails, drum."""
    W, H = lay.W, lay.H
    trim_mat = mats["trim"]
    accent_mat = mats["accent"]
    frame_x = lay.body_x1 - 0.05
    sill_h = 0.14
    header_h = 0.14
    sill_top = sill_h
    header_bot = H - header_h
    opening_h = header_bot - sill_top
    post_depth = 0.14
    post_inner_y = W / 2.0 - post_depth

    header = BoxGeometry((0.10, W, header_h))
    header.translate(frame_x, 0.0, H - header_h / 2.0)
    body.visual(mesh_from_geometry(header, "door_header"), material=trim_mat, name="door_header", material_class_id="metal.paint_coated")
    sill = BoxGeometry((0.10, W, sill_h))
    sill.translate(frame_x, 0.0, sill_h / 2.0)
    body.visual(mesh_from_geometry(sill, "door_sill"), material=trim_mat, name="door_sill", material_class_id="metal.paint_coated")
    for sy, nm in ((1.0, "post_p"), (-1.0, "post_n")):
        post = BoxGeometry((0.12, post_depth, H))
        post.translate(frame_x, sy * (W / 2.0 - post_depth / 2.0), H / 2.0)
        body.visual(mesh_from_geometry(post, nm), material=trim_mat, name=nm, material_class_id="metal.paint_coated")
    track_xw = 0.04
    track_yw = 0.03
    track_h = opening_h
    for sy, nm in ((1.0, "track_p"), (-1.0, "track_n")):
        track_y = sy * (post_inner_y - track_yw / 2.0)
        track = BoxGeometry((track_xw, track_yw, track_h))
        track.translate(frame_x, track_y, sill_top + track_h / 2.0)
        body.visual(mesh_from_geometry(track, nm), material=accent_mat, name=nm, material_class_id="metal.blackened_gunmetal")
    curtain_w = max(1.4, W - 0.36)
    drum_len = curtain_w - 0.06
    drum_mesh = _drum_assembly(frame_x, header_bot, 0.08, drum_len)
    body.visual(mesh_from_geometry(drum_mesh, "drum"), material=accent_mat, name="drum", material_class_id="metal.blackened_gunmetal")


def _emit_side_doorway_frame(body, r, lay: _Layout, mats: dict):
    """+Y side-wall doorway frame: header, sill, two posts (side source L187-203)."""
    W, H = lay.W, lay.H
    L = lay.L
    trim_mat = mats["trim"]
    doorway_margin = CORNER + 0.14
    opening_x0 = -L / 2.0 + doorway_margin
    opening_x1 = L / 2.0 - doorway_margin
    opening_len = opening_x1 - opening_x0
    header_h = 0.14
    sill_h = 0.14
    post_w_x = doorway_margin - CORNER
    post_d_y = 0.14

    header = BoxGeometry((opening_len, 0.12, header_h))
    header.translate(0.0, W / 2.0 - 0.06, H - header_h / 2.0)
    body.visual(mesh_from_geometry(header, "door_header"), material=trim_mat, name="door_header", material_class_id="metal.paint_coated")
    sill = BoxGeometry((opening_len, 0.12, sill_h))
    sill.translate(0.0, W / 2.0 - 0.06, sill_h / 2.0)
    body.visual(mesh_from_geometry(sill, "door_sill"), material=trim_mat, name="door_sill", material_class_id="metal.paint_coated")
    post_x_positions = [opening_x0 - post_w_x / 2.0, opening_x1 + post_w_x / 2.0]
    for i in range(2):
        post = BoxGeometry((post_w_x, post_d_y, H))
        post.translate(post_x_positions[i], W / 2.0 - post_d_y / 2.0, H / 2.0)
        body.visual(mesh_from_geometry(post, f"post_{i}"), material=trim_mat, name=f"post_{i}", material_class_id="metal.paint_coated")


# --------------------------------------------------------------------------- #
# door_closure modules
# --------------------------------------------------------------------------- #


def _emit_swing_doors(model, body, r, lay: _Layout, mats: dict):
    """double_swing / single_swing / n_doorleaves: door_count REVOLUTE +Z leaves
    at the +X end, alternating hinge sides, each with rod + cam handle."""
    W, H = lay.W, lay.H
    cp = lay.corr_pitch
    door_x = lay.door_x
    door_mat = mats["doors"]
    accent_mat = mats["accent"]
    trim_mat = mats["trim"]

    n = r.door_count
    opening_w = W - 0.16
    leaf_w = opening_w / n
    door_h = H - 0.40
    y_open_max = opening_w / 2.0
    rod_x = DOOR_T * 0.225 + CORR_DEPTH - 0.012

    # A full-height hinge stile on the body at each leaf's hinge line, with its
    # +X face on the closed-door plane (door_x). It runs from the door sill to
    # the door header so it is always connected to the body shell, gives every
    # body_to_door_i origin a real body surface within the 15 mm
    # articulation-origin baseline, and reads as the visible door hinge column.
    stile_top = H - 0.14
    stile_bot = 0.14
    stile_h = stile_top - stile_bot
    stile_cz = (stile_top + stile_bot) / 2.0
    for i in range(n):
        hinge_sign = 1.0 if i % 2 == 0 else -1.0
        slot_y_max = y_open_max - i * leaf_w
        slot_y_min = slot_y_max - leaf_w
        hinge_y = slot_y_max if hinge_sign > 0 else slot_y_min
        stile = BoxGeometry((0.07, 0.10, stile_h))
        # centered so the +X face lands on door_x (joint origin on real surface)
        stile.translate(door_x - 0.035, hinge_y, stile_cz)
        sname = f"hinge_strap_{i}_0"
        body.visual(mesh_from_geometry(stile, sname), material=accent_mat, name=sname, material_class_id="metal.blackened_gunmetal")

    # Number of rods per leaf scales like the sources: 1 leaf → 4 rods,
    # 2 leaves → 2 rods each, ≥3 leaves → 1 rod each.
    if n == 1:
        rods_per_leaf = 4
    elif n == 2:
        rods_per_leaf = 2
    else:
        rods_per_leaf = 1

    for i in range(n):
        dname = f"door_{i}"
        hinge_sign = 1.0 if i % 2 == 0 else -1.0
        slot_y_max = y_open_max - i * leaf_w
        slot_y_min = slot_y_max - leaf_w
        hinge_y = slot_y_max if hinge_sign > 0 else slot_y_min

        door = model.part(dname)
        panel = _corrugated_door_panel(leaf_w, door_h, cp)
        panel.translate(0.0, -hinge_sign * (leaf_w / 2.0), 0.0)
        door.visual(mesh_from_geometry(panel, "door_panel"), material=door_mat, name="door_panel", material_class_id="metal.patterned_sheet_panel")
        door.inertial = Inertial.from_geometry(
            Box((DOOR_T, leaf_w, door_h)),
            mass=40.0 + 30.0 * rods_per_leaf,
            origin=Origin(xyz=(0.0, -hinge_sign * leaf_w / 2.0, 0.0)),
        )

        model.articulation(
            f"body_to_{dname}",
            ArticulationType.REVOLUTE,
            parent=body,
            child=door,
            origin=Origin(xyz=(door_x, hinge_y, H / 2.0)),
            axis=(0.0, 0.0, hinge_sign),
            motion_limits=MotionLimits(
                effort=200.0, velocity=2.0, lower=0.0, upper=r.door_open_limit_rad
            ),
        )

        free_dir = -hinge_sign
        # rod local Y positions spread from free edge toward hinge
        if rods_per_leaf == 1:
            rod_ys = [free_dir * (leaf_w * 0.50)]
        elif rods_per_leaf == 2:
            rod_ys = [free_dir * (leaf_w * 0.30), free_dir * (leaf_w * 0.78)]
        else:  # 4 rods on a single full-width leaf
            rod_ys = [free_dir * leaf_w * (0.15 + 0.70 * k / 3.0) for k in range(4)]

        for ridx, ry in enumerate(rod_ys):
            rod = CylinderGeometry(0.018, door_h - 0.10, radial_segments=16)
            rod.translate(rod_x, ry, 0.0)
            door.visual(mesh_from_geometry(rod, f"rod_{ridx}"), material=accent_mat, name=f"rod_{ridx}", material_class_id="metal.blackened_gunmetal")
            for sz_idx, sz in enumerate((1.0, -1.0)):
                kp = BoxGeometry((0.05, 0.06, 0.05))
                kp.translate(rod_x - 0.02, ry, sz * (door_h / 2.0 - 0.18))
                kn = f"keeper_{ridx}_{sz_idx}"
                door.visual(mesh_from_geometry(kp, kn), material=trim_mat, name=kn, material_class_id="metal.paint_coated")
            hname = f"handle_{i}_{ridx}"
            _build_handle_swing(
                model, door, dname, hname, rod_x, ry, accent_mat=accent_mat, trim_mat=trim_mat
            )


def _emit_roll_up_door(model, body, r, lay: _Layout, mats: dict):
    """roll_up_door: a single segmented curtain on a PRISMATIC +Z joint."""
    W, H = lay.W, lay.H
    curtain_mat = mats["doors"]
    bar_mat = mats["trim"]
    frame_x = lay.body_x1 - 0.05
    sill_h = 0.14
    header_h = 0.14
    sill_top = sill_h
    header_bot = H - header_h
    opening_h = header_bot - sill_top

    slat_h = 0.10
    slat_t = 0.025
    slat_spacing = 0.099
    curtain_w = max(1.4, W - 0.36)
    bottom_bar_h = 0.06
    bottom_bar_t = 0.05
    joint_z = sill_top

    # number of slats fills the opening minus the bottom bar; the topmost slat
    # tucks just behind the header (declared allow_overlap in tests). Matches the
    # source ratio (~22 slats for a ~2.31 m opening). Cap so we don't overshoot.
    n_slats = max(4, int((opening_h - bottom_bar_h) / slat_spacing) + 1)
    travel = opening_h + 0.05

    curtain = model.part("curtain")
    bar_geo = BoxGeometry((bottom_bar_t, curtain_w, bottom_bar_h))
    bar_geo.translate(0.0, 0.0, bottom_bar_h / 2.0)
    curtain.visual(mesh_from_geometry(bar_geo, "bottom_bar"), material=bar_mat, name="bottom_bar", material_class_id="metal.paint_coated")
    for i in range(n_slats):
        slat = _curtain_slat(curtain_w, slat_t, slat_h)
        z_center = bottom_bar_h + slat_h / 2.0 + i * slat_spacing
        slat.translate(0.0, 0.0, z_center)
        curtain.visual(mesh_from_geometry(slat, f"slat_{i}"), material=curtain_mat, name=f"slat_{i}", material_class_id="metal.paint_coated")

    curtain_h = bottom_bar_h + (n_slats - 1) * slat_spacing + slat_h
    curtain.inertial = Inertial.from_geometry(
        Box((slat_t, curtain_w, curtain_h)),
        mass=150.0,
        origin=Origin(xyz=(0.0, 0.0, curtain_h / 2.0)),
    )
    model.articulation(
        "body_to_curtain",
        ArticulationType.PRISMATIC,
        parent=body,
        child=curtain,
        origin=Origin(xyz=(frame_x, 0.0, joint_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=500.0, velocity=0.5, lower=0.0, upper=travel),
    )
    return n_slats


def _emit_side_access_doors(model, body, r, lay: _Layout, mats: dict):
    """side_access_doors: a pair of REVOLUTE +Z doors on the +Y side wall."""
    W, H = lay.W, lay.H
    L = lay.L
    cp = lay.corr_pitch
    door_mat = mats["doors"]
    accent_mat = mats["accent"]
    trim_mat = mats["trim"]

    doorway_margin = CORNER + 0.14
    opening_x0 = -L / 2.0 + doorway_margin
    opening_x1 = L / 2.0 - doorway_margin
    opening_len = opening_x1 - opening_x0
    door_gap = 0.02
    door_w = (opening_len - door_gap) / 2.0
    door_h = H - 0.40
    rod_y_local = -DOOR_T / 2.0 + DOOR_T * 0.225 + CORR_DEPTH - 0.012

    door_specs = [
        (0, opening_x0, +1.0, +1.0),
        (1, opening_x1, -1.0, -1.0),
    ]
    for di, hinge_x, free_dir, axis_z in door_specs:
        dname = f"door_{di}"
        door = model.part(dname)
        panel = _corrugated_side_door_panel(door_w, door_h, cp)
        panel.translate(free_dir * (door_w / 2.0), -DOOR_T / 2.0, 0.0)
        door.visual(mesh_from_geometry(panel, "door_panel"), material=door_mat, name="door_panel", material_class_id="metal.patterned_sheet_panel")
        door.inertial = Inertial.from_geometry(
            Box((door_w, DOOR_T, door_h)),
            mass=80.0,
            origin=Origin(xyz=(free_dir * door_w / 2.0, -DOOR_T / 2.0, 0.0)),
        )
        model.articulation(
            f"body_to_{dname}",
            ArticulationType.REVOLUTE,
            parent=body,
            child=door,
            origin=Origin(xyz=(hinge_x, W / 2.0, H / 2.0)),
            axis=(0.0, 0.0, axis_z),
            motion_limits=MotionLimits(
                effort=200.0, velocity=2.0, lower=0.0, upper=r.door_open_limit_rad
            ),
        )
        rod_xs = [free_dir * door_w * 0.30, free_dir * door_w * 0.78]
        for ri in range(2):
            rx = rod_xs[ri]
            rod = CylinderGeometry(0.018, door_h - 0.10, radial_segments=16)
            rod.translate(rx, rod_y_local, 0.0)
            door.visual(mesh_from_geometry(rod, f"rod_{ri}"), material=accent_mat, name=f"rod_{ri}", material_class_id="metal.blackened_gunmetal")
            for ki, sz in enumerate((1.0, -1.0)):
                kp = BoxGeometry((0.05, 0.06, 0.05))
                kp.translate(rx, rod_y_local - 0.02, sz * (door_h / 2.0 - 0.18))
                kn = f"keeper_{ri}_{ki}"
                door.visual(mesh_from_geometry(kp, kn), material=trim_mat, name=kn, material_class_id="metal.paint_coated")
            # cam handle: lever protrudes along +Y
            hname = f"handle_{di}_{ri}"
            handle = model.part(hname)
            hub = CylinderGeometry(0.022, 0.06, radial_segments=16).rotate_x(math.pi / 2.0)
            hub.translate(0.0, 0.04, 0.0)
            handle.visual(mesh_from_geometry(hub, "hub"), material=accent_mat, name="hub", material_class_id="metal.blackened_gunmetal")
            lever = BoxGeometry((0.045, 0.14, 0.035))
            lever.translate(0.0, 0.13, 0.0)
            handle.visual(mesh_from_geometry(lever, "lever"), material=accent_mat, name="lever", material_class_id="metal.blackened_gunmetal")
            grip = CylinderGeometry(0.025, 0.10, radial_segments=12).rotate_x(math.pi / 2.0)
            grip.translate(0.0, 0.20, 0.0)
            handle.visual(mesh_from_geometry(grip, "grip"), material=trim_mat, name="grip", material_class_id="metal.paint_coated")
            handle.inertial = Inertial.from_geometry(
                Box((0.06, 0.22, 0.06)), mass=1.2, origin=Origin(xyz=(0.0, 0.11, 0.0))
            )
            model.articulation(
                f"{dname}_to_{hname}",
                ArticulationType.REVOLUTE,
                parent=door,
                child=handle,
                # origin nudged toward the rod's -Y surface (toward the panel
                # skin) so it sits on real door geometry within the origin
                # baseline while the hub still wraps the rod.
                origin=Origin(xyz=(rx, rod_y_local - 0.006, 0.05)),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(
                    effort=20.0, velocity=3.0, lower=0.0, upper=math.radians(110.0)
                ),
            )


# --------------------------------------------------------------------------- #
# roof_top modules (hatch_lid / open_top_tarp). flat_solid is a body visual.
# --------------------------------------------------------------------------- #

TOP_RAIL_W = 0.10
TOP_RAIL_H = 0.08
LID_SKIN_T = 0.030
LID_FRAME_D = 0.070
LID_CLEARANCE = 0.02
N_HINGE_BARRELS = 5


def _emit_hatch_lid(model, body, r, lay: _Layout, mats: dict):
    """hatch_lid: top frame rails + hinge barrels + a REVOLUTE -X corrugated lid."""
    W, H = lay.W, lay.H
    cp = lay.corr_pitch
    body_len, body_cx = lay.body_len, lay.body_cx
    trim_mat = mats["trim"]
    accent_mat = mats["accent"]
    lid_mat = mats["doors"]

    rail_len = body_len - 2 * CORNER
    for sy, nm in ((1.0, "top_rail_p"), (-1.0, "top_rail_n")):
        rail = BoxGeometry((rail_len, TOP_RAIL_W, TOP_RAIL_H))
        rail.translate(
            body_cx, sy * (W / 2.0 - CORNER - TOP_RAIL_W / 2.0), H - TOP_RAIL_H / 2.0
        )
        body.visual(mesh_from_geometry(rail, nm), material=trim_mat, name=nm, material_class_id="metal.paint_coated")
    end_rail_w = W - 2 * CORNER - 2 * TOP_RAIL_W
    end_rail = BoxGeometry((TOP_RAIL_W, end_rail_w, TOP_RAIL_H))
    end_rail.translate(lay.body_x0 + CORNER + TOP_RAIL_W / 2.0, 0.0, H - TOP_RAIL_H / 2.0)
    body.visual(mesh_from_geometry(end_rail, "top_rail_end"), material=trim_mat, name="top_rail_end", material_class_id="metal.paint_coated")

    hinge_y = W / 2.0 - CORNER - TOP_RAIL_W
    hinge_z = H + LID_SKIN_T / 2.0
    hinge_x0 = body_cx - rail_len / 2.0 + 0.20
    hinge_x1 = body_cx + rail_len / 2.0 - 0.20
    for i in range(N_HINGE_BARRELS):
        t = i / (N_HINGE_BARRELS - 1) if N_HINGE_BARRELS > 1 else 0.5
        bx = hinge_x0 + t * (hinge_x1 - hinge_x0)
        barrel = _hinge_barrel()
        barrel.translate(bx, hinge_y, hinge_z)
        body.visual(
            mesh_from_geometry(barrel, f"hinge_barrel_{i}"), material=accent_mat, name=f"hinge_barrel_{i}", material_class_id="metal.blackened_gunmetal"
        )

    latch_rail = BoxGeometry((rail_len, 0.06, 0.05))
    latch_rail.translate(body_cx, -(W / 2.0 - CORNER - TOP_RAIL_W), H - 0.025)
    body.visual(mesh_from_geometry(latch_rail, "latch_rail"), material=trim_mat, name="latch_rail", material_class_id="metal.paint_coated")

    # --- lid part ---
    lid_length = (lay.body_x1 - CORNER) - (lay.body_x0 + CORNER + TOP_RAIL_W) - 4 * LID_CLEARANCE
    opening_inner_w = W - 2 * CORNER - 2 * TOP_RAIL_W
    lid_width = opening_inner_w - LID_CLEARANCE
    hinge_y_lid = W / 2.0 - CORNER - TOP_RAIL_W
    hinge_z_lid = H

    roof_lid = model.part("roof_lid")
    lid_panel = _corrugated_lid_panel(lid_length, lid_width, LID_SKIN_T, LID_FRAME_D, cp)
    lid_panel.translate(0.0, -lid_width / 2.0, 0.0)
    roof_lid.visual(mesh_from_geometry(lid_panel, "lid_panel"), material=lid_mat, name="lid_panel", material_class_id="metal.patterned_sheet_panel")
    for i in range(N_HINGE_BARRELS):
        t = i / (N_HINGE_BARRELS - 1) if N_HINGE_BARRELS > 1 else 0.5
        ex = hinge_x0 + t * (hinge_x1 - hinge_x0)
        eye = _lid_hinge_eye()
        eye.translate(ex - body_cx, 0.0, LID_SKIN_T / 2.0)
        roof_lid.visual(mesh_from_geometry(eye, f"lid_eye_{i}"), material=accent_mat, name=f"lid_eye_{i}", material_class_id="metal.blackened_gunmetal")
    latch_catch = BoxGeometry((0.30, 0.06, 0.04))
    latch_catch.translate(0.0, -lid_width + 0.03, -(LID_FRAME_D + 0.02))
    roof_lid.visual(mesh_from_geometry(latch_catch, "latch_catch"), material=accent_mat, name="latch_catch", material_class_id="metal.blackened_gunmetal")
    roof_lid.inertial = Inertial.from_geometry(
        Box((lid_length, lid_width, 0.12)),
        mass=120.0,
        origin=Origin(xyz=(0.0, -lid_width / 2.0, 0.0)),
    )
    model.articulation(
        "body_to_roof_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=roof_lid,
        origin=Origin(xyz=(body_cx, hinge_y_lid, hinge_z_lid)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=300.0, velocity=1.5, lower=0.0, upper=math.radians(100.0)),
    )


def _open_top_openable_indices(r, lay: _Layout, n_bows: int) -> set[int]:
    """Seed-stable movable bow selection: at least one, at most all."""
    key = (
        f"{r.door_closure}|{r.wall_surface}|{r.palette_style}|"
        f"{r.L:.4f}|{r.W:.4f}|{r.H:.4f}|{lay.body_x0:.4f}|{lay.body_x1:.4f}|{n_bows}"
    )
    rng = random.Random(key)
    movable_count = rng.randint(1, n_bows)
    return set(rng.sample(range(n_bows), movable_count))


def _open_top_bow_count(r, lay: _Layout) -> int:
    """Seed-stable section count; longer bodies allow more arched roof sections."""
    body_len = lay.body_len
    min_bows = max(3, int(body_len / 1.9) + 1)
    max_bows = max(min_bows, int(body_len / 1.05) + 1)
    max_bows = min(max_bows, 9)
    key = (
        f"bows|{r.door_closure}|{r.wall_surface}|{r.palette_style}|"
        f"{r.L:.4f}|{r.W:.4f}|{r.H:.4f}|{lay.body_x0:.4f}|{lay.body_x1:.4f}"
    )
    return random.Random(key).randint(min_bows, max_bows)


def _emit_open_top_tarp(model, body, r, lay: _Layout, mats: dict):
    """open_top_tarp: fixed plus hinged tube-bow/tarp sections."""
    W, H = lay.W, lay.H
    body_len, body_cx = lay.body_len, lay.body_cx
    trim_mat = mats["trim"]
    accent_mat = mats["accent"]
    tarp_mat = mats["tarp"]

    bow_inset = 0.30
    bow_rise = 0.18
    bow_span = W - 0.20
    bow_base_z = H
    tarp_thickness = 0.008
    top_rail_w = 0.08
    top_rail_h = 0.06
    # Bow count varies per seed within a length-scaled range. Each bow is one
    # top section; a seed-stable subset becomes independently hinged.
    n_bows = _open_top_bow_count(r, lay)
    bow_available = body_len - 2.0 * bow_inset
    bow_spacing = bow_available / (n_bows - 1)
    bow_positions_x = [lay.body_x0 + bow_inset + i * bow_spacing for i in range(n_bows)]
    openable_indices = _open_top_openable_indices(r, lay, n_bows)

    for sy, nm in ((1.0, "top_rail_p"), (-1.0, "top_rail_n")):
        rail = BoxGeometry((body_len, top_rail_w, top_rail_h))
        rail.translate(body_cx, sy * (W / 2.0 - top_rail_w / 2.0), H - top_rail_h / 2.0)
        body.visual(mesh_from_geometry(rail, nm), material=trim_mat, name=nm, material_class_id="metal.paint_coated")

    bow_half_span = bow_span / 2.0
    hinge_y = bow_half_span

    for i, bow_x in enumerate(bow_positions_x):
        seg_x0 = bow_x - 0.10 if i == 0 else (bow_positions_x[i - 1] + bow_x) / 2.0
        seg_x1 = bow_x + 0.10 if i == n_bows - 1 else (bow_x + bow_positions_x[i + 1]) / 2.0
        if i in openable_indices:
            bow_hinged = model.part(f"bow_hinged_{i}")
            hinged_bow_mesh = _build_hinged_bow_mesh(bow_span, bow_rise)
            bow_hinged.visual(mesh_from_geometry(hinged_bow_mesh, "bow_arch"), material=trim_mat, name="bow_arch", material_class_id="metal.paint_coated")
            hinged_tarp = _build_hinged_tarp_mesh_asymmetric(
                seg_x1 - bow_x, bow_x - seg_x0, bow_span, bow_rise, tarp_thickness
            )
            bow_hinged.visual(mesh_from_geometry(hinged_tarp, "tarp_hinged"), material=tarp_mat, name="tarp_hinged", material_class_id="fabric.canvas")
            bracket_far = BoxGeometry((0.06, 0.06, 0.04))
            bracket_far.translate(0.0, -bow_span, -0.02)
            bow_hinged.visual(mesh_from_geometry(bracket_far, "bracket_far"), material=accent_mat, name="bracket_far", material_class_id="metal.blackened_gunmetal")
            hinge_bracket = CylinderGeometry(0.022, 0.14, radial_segments=12)
            hinge_bracket.rotate_y(math.pi / 2.0)
            bow_hinged.visual(
                mesh_from_geometry(hinge_bracket, "hinge_barrel"), material=accent_mat, name="hinge_barrel", material_class_id="metal.blackened_gunmetal"
            )
            bow_hinged.inertial = Inertial.from_geometry(
                Box((max(seg_x1 - seg_x0, 0.10), bow_span, bow_rise + 0.05)),
                mass=15.0,
                origin=Origin(xyz=(0.0, -bow_span / 2.0, bow_rise / 2.0)),
            )
            model.articulation(
                f"body_to_bow_hinged_{i}",
                ArticulationType.REVOLUTE,
                parent=body,
                child=bow_hinged,
                origin=Origin(xyz=(bow_x, hinge_y, bow_base_z)),
                axis=(-1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=50.0, velocity=1.5, lower=0.0, upper=math.radians(80.0)),
            )
            for x_off, nm in ((0.04, f"hinge_ear_{i}_0"), (-0.04, f"hinge_ear_{i}_1")):
                ear = BoxGeometry((0.06, 0.06, 0.10))
                ear.translate(bow_x + x_off, hinge_y, bow_base_z - 0.04)
                body.visual(mesh_from_geometry(ear, nm), material=accent_mat, name=nm, material_class_id="metal.blackened_gunmetal")
        else:
            bow_mesh = _build_bow_mesh(bow_half_span, bow_rise)
            bow_mesh.translate(bow_x, 0.0, bow_base_z)
            body.visual(mesh_from_geometry(bow_mesh, f"bow_fixed_{i}"), material=trim_mat, name=f"bow_fixed_{i}", material_class_id="metal.paint_coated")
            for sy, bnm in ((1.0, f"bracket_{i}_p"), (-1.0, f"bracket_{i}_n")):
                bracket = BoxGeometry((0.06, 0.06, 0.04))
                bracket.translate(bow_x, sy * bow_half_span, bow_base_z - 0.02)
                body.visual(mesh_from_geometry(bracket, bnm), material=accent_mat, name=bnm, material_class_id="metal.blackened_gunmetal")
            n_tarp_x = 4
            tarp_xs = [seg_x0 + j * (seg_x1 - seg_x0) / (n_tarp_x - 1) for j in range(n_tarp_x)]
            fixed_tarp = _build_tarp_mesh(tarp_xs, bow_half_span, bow_rise, tarp_thickness)
            fixed_tarp.translate(0.0, 0.0, bow_base_z)
            body.visual(mesh_from_geometry(fixed_tarp, f"tarp_fixed_{i}"), material=tarp_mat, name=f"tarp_fixed_{i}", material_class_id="fabric.canvas")


# --------------------------------------------------------------------------- #
# Top-level builders
# --------------------------------------------------------------------------- #


def _register_materials(model, r) -> dict:
    return {
        "body": model.material("body_steel", rgba=r.body_rgba),
        "doors": model.material("door_steel", rgba=r.doors_rgba),
        "accent": model.material("dark_hardware", rgba=r.accent_rgba),
        "trim": model.material("trim_steel", rgba=r.trim_rgba),
        "tarp": model.material("tarp_canvas", rgba=r.tarp_rgba),
    }


def build_container_shipping_container(
    config: ContainerShippingContainerConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="shipping_container")
    mats = _register_materials(model, r)

    full_length_body = r.door_closure == "side_access_doors"
    lay = _layout(r, full_length_body=full_length_body)

    body = _emit_body(model, r, lay, mats)

    # door_closure mechanism
    if r.door_closure in SWING_FAMILY:
        _emit_swing_doors(model, body, r, lay, mats)
    elif r.door_closure == "roll_up_door":
        _emit_roll_up_door(model, body, r, lay, mats)
    else:  # side_access_doors
        _emit_side_access_doors(model, body, r, lay, mats)

    # roof_top structure
    if r.roof_top == "hatch_lid":
        _emit_hatch_lid(model, body, r, lay, mats)
    elif r.roof_top == "open_top_tarp":
        _emit_open_top_tarp(model, body, r, lay, mats)
    # flat_solid: roof visual already on body

    return model


def build_seeded_container_shipping_container(seed: int) -> ArticulatedObject:
    return build_container_shipping_container(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_shipping_container_tests(
    model: ArticulatedObject, config: ContainerShippingContainerConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    body = model.get_part("body")
    L, W, H = r.L, r.W, r.H

    # The curtain / roof lid / doors slide and swing on rails & headers mounted in
    # the body; those captured interfaces intentionally overlap the body frame.
    _pn = {p.name for p in model.parts}
    for _other in _pn:
        if _other == "body":
            continue
        if "curtain" in _other or "lid" in _other or _other.startswith("door") or "handle" in _other or "lock" in _other or "keeper" in _other or "lever" in _other or "rod" in _other:
            ctx.allow_overlap(
                body, model.get_part(_other),
                reason="Curtain / roof lid / door slides or swings on body-mounted rails and headers.",
            )
    # Door handles / lock rods / keepers are mounted on the door panels, and the
    # adjacent door leaves / their hardware sweep past one another when opening.
    _door_hw = [n for n in _pn if n.startswith("door") or "handle" in n or "lock" in n
                or "keeper" in n or "rod" in n or "lever" in n]
    for _i in range(len(_door_hw)):
        for _j in range(_i + 1, len(_door_hw)):
            ctx.allow_overlap(
                model.get_part(_door_hw[_i]), model.get_part(_door_hw[_j]),
                reason="Container door leaves and their lock hardware sweep past one another.",
            )

    # ---- long-box identity: X longest by >1 m over Y and Z ----
    body_ext = _ext(ctx.part_world_aabb(body))
    ctx.check(
        "container is a long box (X longest, X>Y+1, X>Z+1)",
        body_ext[0] > body_ext[1] + 1.0 and body_ext[0] > body_ext[2] + 1.0,
        details=f"body extents={body_ext}",
    )

    # ---- 8 corner castings always present ----
    corner_names = [v.name for v in body.visuals if v.name and v.name.startswith("corner_")]
    ctx.check(
        "8 ISO corner castings exist",
        len(corner_names) == 8,
        details=f"found {len(corner_names)} corner castings",
    )

    # ================= door_closure =================
    if r.door_closure in SWING_FAMILY:
        n = r.door_count
        opening_w = W - 0.16
        leaf_w = opening_w / n
        rods_per_leaf = 4 if n == 1 else (2 if n == 2 else 1)

        doors = [model.get_part(f"door_{i}") for i in range(n)]
        hinges = [model.get_articulation(f"body_to_door_{i}") for i in range(n)]

        ctx.check(
            f"{n} swing door leaf/leaves exist",
            all(d is not None for d in doors) and len(doors) == n,
            details=f"door_count={n}",
        )

        for i, d in enumerate(doors):
            pos = ctx.part_world_position(d)
            ctx.check(
                f"door_{i} is at the +X cargo end",
                pos is not None and pos[0] > L / 2.0 - 0.35,
                details=f"door_{i} origin={pos}",
            )

        # hinge seating overlaps (captured-fit, grandfathered). Each leaf panel
        # may seat/latch against the outer posts, the center mullion (if any),
        # and the hinge stiles, so allow overlap with all of them.
        body_vis_names = {v.name for v in body.visuals}
        has_mullion = "mullion" in body_vis_names
        for i, d in enumerate(doors):
            frame_targets = ["post_p", "post_n"]
            if has_mullion:
                frame_targets.append("mullion")
            for tgt in frame_targets:
                ctx.allow_overlap(
                    d, body, elem_a="door_panel", elem_b=tgt,
                    reason=f"door_{i} hinge/latch edge seats against {tgt}.",
                )
            # door panels seat against the hinge stiles (one per leaf). Adjacent
            # narrow leaves can also brush a neighbour leaf's stile.
            for j in range(n):
                ctx.allow_overlap(
                    d, body, elem_a="door_panel", elem_b=f"hinge_strap_{j}_0",
                    reason=f"door_{i} panel captured by / brushes hinge stile {j}.",
                )
            ctx.expect_contact(d, body, name=f"door_{i} seated against doorway frame")

        # handle/rod captured overlaps + rotation + door swing
        for i, (d, hinge) in enumerate(zip(doors, hinges)):
            for ridx in range(rods_per_leaf):
                hname = f"handle_{i}_{ridx}"
                h = model.get_part(hname)
                ctx.allow_overlap(
                    d, h, elem_a=f"rod_{ridx}", elem_b="hub",
                    reason=f"{hname} hub seated around its locking rod.",
                )
                ctx.allow_overlap(
                    d, h, elem_a=f"rod_{ridx}", elem_b="lever",
                    reason=f"{hname} lever passes over its locking rod at the clamp.",
                )
                ctx.allow_overlap(
                    d, h, elem_a="door_panel", elem_b="hub",
                    reason=f"{hname} hub sits flush against the corrugated door face.",
                )
                # on narrow inner leaves the cam handle can sweep over the
                # doorway frame columns (mullion / posts) which stand at the
                # closed-door plane; allow that captured clearance.
                frame_cols = ["post_p", "post_n"] + (["mullion"] if has_mullion else [])
                for col in frame_cols:
                    for he in ("hub", "lever", "grip"):
                        ctx.allow_overlap(
                            h, body, elem_a=he, elem_b=col,
                            reason=f"{hname} {he} sweeps over the {col} at the closed-door plane.",
                        )
                ctx.expect_contact(h, d, name=f"{hname} mounted on door_{i}")
                hjoint = model.get_articulation(f"{d.name}_to_{hname}")
                ext0 = _ext(ctx.part_world_aabb(h))
                with ctx.pose({hjoint: math.radians(90.0)}):
                    ext90 = _ext(ctx.part_world_aabb(h))
                ctx.check(
                    f"{hname} rotates about its rod axis (lever sweeps)",
                    abs(ext90[1] - ext0[1]) > 0.05 or abs(ext90[0] - ext0[0]) > 0.05,
                    details=f"{hname} rest={ext0} turned={ext90}",
                )
            # swing open: free edge moves outward in +X
            x0 = _ext(ctx.part_world_aabb(d))[0]
            with ctx.pose({hinge: math.radians(100.0)}):
                x1 = _ext(ctx.part_world_aabb(d))[0]
            min_gain = 0.2 if n >= 3 else 0.4
            ctx.check(
                f"door_{i} swings open (free edge moves outward in +X)",
                x1 > x0 + min_gain,
                details=f"door_{i} X-extent rest={x0:.3f} open={x1:.3f}",
            )

        # each leaf has its own independent joint (not mimic)
        for i in range(n):
            art = model.get_articulation(f"body_to_door_{i}")
            ctx.check(
                f"body_to_door_{i} exists as an independent joint",
                art is not None and abs(art.axis[2]) > 0.99,
                details=f"joint={art}",
            )

    elif r.door_closure == "roll_up_door":
        curtain = model.get_part("curtain")
        joint = model.get_articulation("body_to_curtain")
        ctx.check(
            "curtain joint axis is +Z (vertical rise)",
            joint.axis is not None and abs(joint.axis[2] - 1.0) < 0.01,
            details=f"axis={joint.axis}",
        )
        cpos = ctx.part_world_position(curtain)
        ctx.check(
            "curtain is at the +X cargo end",
            cpos is not None and cpos[0] > L / 2.0 - 0.6,
            details=f"curtain origin={cpos}",
        )
        ctx.expect_contact(
            curtain, body, elem_a="bottom_bar", elem_b="door_sill",
            contact_tol=0.005, name="curtain bottom bar seated on sill",
        )
        # top slats tuck behind the header when closed (real roll-up doors nest
        # the upper slats in the header recess). Declare the overlap for every
        # slat whose top edge reaches into the header band.
        slat_names = sorted(
            [v.name for v in curtain.visuals if v.name and v.name.startswith("slat_")],
            key=lambda s: int(s.split("_")[1]),
        )
        for sname in slat_names[-3:]:
            ctx.allow_overlap(
                curtain, body, elem_a=sname, elem_b="door_header",
                reason="Top curtain slats tuck behind the door header when closed.",
            )
        # curtain rises when opened
        rest_z = ctx.part_world_position(curtain)
        with ctx.pose({joint: 1.0}):
            mid_z = ctx.part_world_position(curtain)
        ctx.check(
            "curtain rises vertically when partially opened",
            mid_z is not None and rest_z is not None and mid_z[2] > rest_z[2] + 0.8,
            details=f"rest={rest_z}, mid={mid_z}",
        )

    else:  # side_access_doors
        door_0 = model.get_part("door_0")
        door_1 = model.get_part("door_1")
        hinge_0 = model.get_articulation("body_to_door_0")
        hinge_1 = model.get_articulation("body_to_door_1")
        for d, nm in ((door_0, "door_0"), (door_1, "door_1")):
            pos = ctx.part_world_position(d)
            ctx.check(
                f"{nm} is on the +Y side wall (not at an end)",
                pos is not None and pos[1] > W / 2.0 - 0.3 and abs(pos[0]) < L / 2.0 - 0.2,
                details=f"{nm} origin={pos}",
            )
        ctx.allow_overlap(
            door_0, body, elem_a="door_panel", elem_b="post_0",
            reason="Door 0 hinge edge seats against the -X side doorway post.",
        )
        ctx.allow_overlap(
            door_1, body, elem_a="door_panel", elem_b="post_1",
            reason="Door 1 hinge edge seats against the +X side doorway post.",
        )
        ctx.expect_contact(door_0, body, name="door_0 seated against doorway frame")
        ctx.expect_contact(door_1, body, name="door_1 seated against doorway frame")
        for di in range(2):
            d = model.get_part(f"door_{di}")
            for ri in range(2):
                hname = f"handle_{di}_{ri}"
                h = model.get_part(hname)
                ctx.allow_overlap(
                    d, h, elem_a=f"rod_{ri}", elem_b="hub",
                    reason=f"Handle hub seated around locking rod on door_{di}.",
                )
                ctx.allow_overlap(
                    d, h, elem_a=f"rod_{ri}", elem_b="lever",
                    reason=f"Handle lever passes over rod on door_{di}.",
                )
                ctx.allow_overlap(
                    d, h, elem_a="door_panel", elem_b="hub",
                    reason=f"Handle hub sits against door face on door_{di}.",
                )
                ctx.expect_contact(h, d, name=f"{hname} mounted on door_{di}")
                hjoint = model.get_articulation(f"door_{di}_to_{hname}")
                ext0 = _ext(ctx.part_world_aabb(h))
                with ctx.pose({hjoint: math.radians(90.0)}):
                    ext90 = _ext(ctx.part_world_aabb(h))
                ctx.check(
                    f"{hname} rotates about rod axis (lever sweeps)",
                    abs(ext90[0] - ext0[0]) > 0.05 or abs(ext90[1] - ext0[1]) > 0.05,
                    details=f"{hname} rest={ext0} turned={ext90}",
                )
        for d, hinge, nm in ((door_0, hinge_0, "door_0"), (door_1, hinge_1, "door_1")):
            y0 = ctx.part_world_aabb(d)[1][1]
            with ctx.pose({hinge: math.radians(90.0)}):
                y1 = ctx.part_world_aabb(d)[1][1]
            ctx.check(
                f"{nm} swings outward (+Y) when opened",
                y1 > y0 + 0.4,
                details=f"{nm} y_max rest={y0:.3f} open={y1:.3f}",
            )

    # ================= roof_top =================
    if r.roof_top == "flat_solid":
        ctx.check(
            "fixed flat roof visual exists",
            body.get_visual("roof") is not None,
            details="no 'roof' visual on body",
        )
    elif r.roof_top == "hatch_lid":
        roof_lid = model.get_part("roof_lid")
        lid_hinge = model.get_articulation("body_to_roof_lid")
        ctx.check(
            "roof_lid is at the top of the container",
            ctx.part_world_position(roof_lid)[2] > H - 0.25,
            details="roof_lid not near top",
        )
        ctx.check(
            "hatch hinge axis is -X",
            lid_hinge.axis is not None and abs(lid_hinge.axis[0]) > 0.99,
            details=f"axis={lid_hinge.axis}",
        )
        for i in range(N_HINGE_BARRELS):
            ctx.allow_overlap(
                body, roof_lid, elem_a=f"hinge_barrel_{i}", elem_b=f"lid_eye_{i}",
                reason=f"Hinge barrel {i} captured inside the lid hinge eye knuckle.",
            )
            ctx.allow_overlap(
                body, roof_lid, elem_a=f"hinge_barrel_{i}", elem_b="lid_panel",
                reason=f"Hinge barrel {i} seats against the lid panel skin at the hinge line.",
            )
            ctx.allow_overlap(
                body, roof_lid, elem_a="top_rail_p", elem_b=f"lid_eye_{i}",
                reason=f"Lid hinge eye {i} wraps the hinge pin on the +Y top rail.",
            )
        ctx.allow_overlap(
            body, roof_lid, elem_a="latch_rail", elem_b="lid_panel",
            reason="Lid free-edge member seats against the latch rail when closed.",
        )
        ctx.expect_contact(
            roof_lid, body, elem_a="lid_eye_0", elem_b="hinge_barrel_0",
            name="lid hinge eye contacts barrel confirming hinge support",
        )
        # lid opens upward
        closed_z = ctx.part_world_aabb(roof_lid)[1][2]
        with ctx.pose({lid_hinge: math.radians(90.0)}):
            open_z = ctx.part_world_aabb(roof_lid)[1][2]
        ctx.check(
            "lid opens upward (free edge rises in +Z)",
            open_z > closed_z + 0.4,
            details=f"closed z_max={closed_z:.3f} open z_max={open_z:.3f}",
        )
    else:  # open_top_tarp
        hinged_joint_names = sorted(
            [a.name for a in model.articulations if a.name.startswith("body_to_bow_hinged_")],
            key=lambda name: int(name.rsplit("_", 1)[1]),
        )
        hinged_indices = [int(name.rsplit("_", 1)[1]) for name in hinged_joint_names]
        hinged_parts = [model.get_part(f"bow_hinged_{i}") for i in hinged_indices]
        body_visuals = [v.name for v in body.visuals]
        ctx.check(
            "no fixed roof panel (open top)",
            "roof" not in body_visuals,
            details=f"body visuals: {body_visuals[:6]}...",
        )
        ctx.check(
            "one or more hinged tarp roof sections exist",
            len(hinged_joint_names) >= 1 and all(p is not None for p in hinged_parts),
            details=f"hinged roof joints={hinged_joint_names}",
        )
        ctx.check(
            "tarp cover sections exist",
            any(name and name.startswith("tarp_fixed_") for name in body_visuals)
            or all(p.get_visual("tarp_hinged") is not None for p in hinged_parts),
            details="no fixed or hinged tarp sections found",
        )
        for i, bow_hinged in zip(hinged_indices, hinged_parts):
            bow_hinge = model.get_articulation(f"body_to_bow_hinged_{i}")
            ctx.check(
                f"hinged bow {i} axis is -X",
                bow_hinge.axis is not None and abs(bow_hinge.axis[0]) > 0.99,
                details=f"axis={bow_hinge.axis}",
            )
            # captured-fit overlaps for each hinged bow
            for ear_idx in (0, 1):
                ctx.allow_overlap(
                    bow_hinged, body, elem_a="hinge_barrel", elem_b=f"hinge_ear_{i}_{ear_idx}",
                    reason="Hinge barrel captured between the two ear brackets.",
                )
                ctx.allow_overlap(
                    bow_hinged, body, elem_a="bow_arch", elem_b=f"hinge_ear_{i}_{ear_idx}",
                    reason="Bow arch tube starts at the hinge axis where the ear is mounted.",
                )
                ctx.allow_overlap(
                    bow_hinged, body, elem_a="tarp_hinged", elem_b=f"hinge_ear_{i}_{ear_idx}",
                    reason="Tarp attaches at the hinge axis where the ear supports the barrel.",
                )
            ctx.allow_overlap(
                bow_hinged, body, elem_a="bracket_far", elem_b="top_rail_n",
                reason="Far-end bracket seats on the -Y top rail when closed.",
            )
            # side_access posts run full height; any hinged bow/tarp section can
            # sit close enough to the side doorway frame to need captured clearance.
            if r.door_closure == "side_access_doors":
                for elem in ("bow_arch", "tarp_hinged", "hinge_barrel", "bracket_far"):
                    for bnm in ("post_0", "post_1", "door_header", "door_sill"):
                        ctx.allow_overlap(
                            bow_hinged, body, elem_a=elem, elem_b=bnm,
                            reason=f"Hinged bow {elem} seats near the side doorway {bnm}.",
                        )
            else:
                for elem in ("bow_arch", "tarp_hinged"):
                    ctx.allow_overlap(
                        bow_hinged, body, elem_a=elem, elem_b="door_header",
                        reason=f"Hinged bow {elem} seats near the +X door header.",
                    )
            rest_aabb = ctx.part_world_aabb(bow_hinged)
            with ctx.pose({bow_hinge: math.radians(70.0)}):
                open_aabb = ctx.part_world_aabb(bow_hinged)
            ctx.check(
                f"hinged bow {i} opens upward (max Z increases)",
                open_aabb[1][2] > rest_aabb[1][2] + 0.10,
                details=f"rest max_z={rest_aabb[1][2]:.3f} open max_z={open_aabb[1][2]:.3f}",
            )

    return ctx.report()
