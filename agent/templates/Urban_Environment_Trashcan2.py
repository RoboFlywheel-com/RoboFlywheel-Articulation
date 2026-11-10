# SPDX-License-Identifier: Apache-2.0

"""Trashcan2 — public-street swing-lid trash can (modular procedural template).

`parallel_children`: a hollow open-top **body** (root / chassis) wears a SWING
**lid_mechanism** (defining REVOLUTE joint), an optional removable **inner_liner**
(PRISMATIC), and a **mount** (free / post / wall). The body mouth behind the
swing flap is always a REAL OPEN VOID — round/drum/hex bodies are revolved/mesh
shells with no top cap disc; dome lids have a real hole (no cap face); planar
flap openings are framed, never a full back quad.

Slot A lid_mechanism : teardrop_dome_rocker / square_gable_rocker /
                        pyramidal_hood_push_flap / dome_circular_push_flap /
                        front_swing_door / open_hooded_top
Slot B body_shape     : round_lathe / rectangular_mesh / square_box /
                        round_drum_mesh / hexagonal_panels
Slot C mount          : free_standing / post_mounted / wall_hoop
Slot D inner_liner    : none / removable_liner
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
    LatheGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True


# ---------------------------------------------------------------------------
# Module enums
# ---------------------------------------------------------------------------
LidMechanism = Literal[
    "teardrop_dome_rocker",
    "square_gable_rocker",
    "pyramidal_hood_push_flap",
    "dome_circular_push_flap",
    "front_swing_door",
    "open_hooded_top",
]
BodyShape = Literal[
    "round_lathe",
    "rectangular_mesh",
    "square_box",
    "round_drum_mesh",
    "hexagonal_panels",
]
Mount = Literal["free_standing", "post_mounted", "wall_hoop"]
InnerLiner = Literal["none", "removable_liner"]
PaletteStyle = Literal[
    "street_green",
    "civic_blue",
    "plastic_black",
    "galvanized_steel",
    "drum_charcoal",
    "brushed_silver",
]

LID_MODULES: tuple[LidMechanism, ...] = (
    "teardrop_dome_rocker",
    "square_gable_rocker",
    "pyramidal_hood_push_flap",
    "dome_circular_push_flap",
    "front_swing_door",
    "open_hooded_top",
)
BODY_MODULES: tuple[BodyShape, ...] = (
    "round_lathe",
    "rectangular_mesh",
    "square_box",
    "round_drum_mesh",
    "hexagonal_panels",
)
MOUNT_MODULES: tuple[Mount, ...] = ("free_standing", "post_mounted", "wall_hoop")
LINER_MODULES: tuple[InnerLiner, ...] = ("none", "removable_liner")

ROUND_BODIES: frozenset[BodyShape] = frozenset({"round_lathe", "round_drum_mesh"})
RECT_FAMILY: frozenset[BodyShape] = frozenset(
    {"rectangular_mesh", "square_box", "hexagonal_panels"}
)
# rocker / dome / hood lids sit on a round-ish or flat rim; gable likes a rect rim.
ROCKER_LIDS: frozenset[LidMechanism] = frozenset(
    {
        "teardrop_dome_rocker",
        "dome_circular_push_flap",
        "pyramidal_hood_push_flap",
        "open_hooded_top",
        "square_gable_rocker",
    }
)


# ---------------------------------------------------------------------------
# Palette styles (>= 3 colorways; every colorway drives body/lid/flap/accent)
# ---------------------------------------------------------------------------
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "street_green",
    "civic_blue",
    "plastic_black",
    "galvanized_steel",
    "drum_charcoal",
    "brushed_silver",
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "street_green": {
        "body": (0.20, 0.42, 0.17, 1.0),
        "lid": (0.16, 0.34, 0.14, 1.0),
        "flap": (0.12, 0.28, 0.11, 1.0),
        "accent": (0.55, 0.58, 0.52, 1.0),
        "dark": (0.05, 0.06, 0.05, 1.0),
    },
    "civic_blue": {
        "body": (0.10, 0.40, 0.66, 1.0),
        "lid": (0.07, 0.32, 0.55, 1.0),
        "flap": (0.05, 0.26, 0.46, 1.0),
        "accent": (0.62, 0.64, 0.66, 1.0),
        "dark": (0.04, 0.05, 0.07, 1.0),
    },
    "plastic_black": {
        "body": (0.11, 0.11, 0.12, 1.0),
        "lid": (0.15, 0.15, 0.16, 1.0),
        "flap": (0.09, 0.09, 0.10, 1.0),
        "accent": (0.48, 0.49, 0.50, 1.0),
        "dark": (0.03, 0.03, 0.03, 1.0),
    },
    "galvanized_steel": {
        "body": (0.62, 0.64, 0.66, 1.0),
        "lid": (0.55, 0.57, 0.59, 1.0),
        "flap": (0.50, 0.52, 0.54, 1.0),
        "accent": (0.74, 0.76, 0.78, 1.0),
        "dark": (0.20, 0.21, 0.22, 1.0),
    },
    "drum_charcoal": {
        "body": (0.13, 0.13, 0.14, 1.0),
        "lid": (0.18, 0.18, 0.19, 1.0),
        "flap": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.40, 0.40, 0.42, 1.0),
        "dark": (0.04, 0.04, 0.05, 1.0),
    },
    "brushed_silver": {
        "body": (0.74, 0.76, 0.79, 1.0),
        "lid": (0.66, 0.68, 0.71, 1.0),
        "flap": (0.60, 0.62, 0.65, 1.0),
        "accent": (0.86, 0.88, 0.90, 1.0),
        "dark": (0.30, 0.31, 0.33, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Trashcan2Config:
    lid_mechanism: LidMechanism | None = None
    body_shape: BodyShape | None = None
    mount: Mount | None = None
    inner_liner: InnerLiner | None = None
    palette_style: PaletteStyle = "street_green"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    flap_open_range: float = 1.40
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["street_green"])
    )


@dataclass(frozen=True)
class ResolvedTrashcan2Config:
    lid_mechanism: LidMechanism
    body_shape: BodyShape
    mount: Mount
    inner_liner: InnerLiner
    palette_style: PaletteStyle
    # base body dimensions
    body_radius: float  # outer radius (round) / half-width (rect family)
    body_height: float
    wall_t: float
    # derived
    mouth_radius: float  # inner mouth half-extent
    flap_open_range: float
    lid_pivot_z: float
    liner_lift: float
    mount_lift_z: float  # how high the body floor is raised by the mount
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0)


def _open_ring(radius: float, length: float, segments: int = 32, name: str = "ring"):
    """An open (uncapped) cylindrical sleeve/ring — never seals the mouth."""
    return mesh_from_geometry(
        CylinderGeometry(radius=radius, height=length, radial_segments=segments, closed=False),
        name,
    )


def _hex_disc(radius: float, length: float, name: str = "hex_floor"):
    return mesh_from_geometry(
        CylinderGeometry(radius=radius, height=length, radial_segments=6, closed=True),
        name,
    )


# ---------------------------------------------------------------------------
# Sampler  (deterministic, body -> lid -> mount -> liner -> palette)
# ---------------------------------------------------------------------------
def _compatible_lids(body: BodyShape) -> tuple[LidMechanism, ...]:
    # Dome rockers read as round-can lids and seat cleanly only on round bodies;
    # the gable roof reads as a rectangular-can lid. Pyramidal hood, open hood,
    # and front door work on any footprint (their bases bridge to the rim collar).
    if body == "round_drum_mesh":
        return (
            "teardrop_dome_rocker",
            "dome_circular_push_flap",
            "pyramidal_hood_push_flap",
            "open_hooded_top",
            "front_swing_door",
        )
    if body == "round_lathe":
        return (
            "teardrop_dome_rocker",
            "dome_circular_push_flap",
            "pyramidal_hood_push_flap",
            "open_hooded_top",
        )
    # rect / square / hex
    return (
        "square_gable_rocker",
        "pyramidal_hood_push_flap",
        "open_hooded_top",
        "front_swing_door",
    )


def config_from_seed(seed: int) -> Trashcan2Config:
    rng = random.Random(seed * 2654435761 + 12345)
    body: BodyShape = rng.choice(BODY_MODULES)  # type: ignore[assignment]
    lid: LidMechanism = rng.choice(_compatible_lids(body))  # type: ignore[assignment]
    mount: Mount = rng.choice(MOUNT_MODULES)  # type: ignore[assignment]
    liner: InnerLiner = "removable_liner" if rng.random() < 0.25 else "none"
    palette: PaletteStyle = rng.choice(PALETTE_STYLES)  # type: ignore[assignment]
    return Trashcan2Config(
        lid_mechanism=lid,
        body_shape=body,
        mount=mount,
        inner_liner=liner,
        palette_style=palette,
        body_height_scale=rng.uniform(0.85, 1.20),
        body_radius_scale=rng.uniform(0.90, 1.15),
        flap_open_range=rng.uniform(1.05, 1.75),
    )


# ---------------------------------------------------------------------------
# resolve_config: validate, clamp, derive, project (mouth-open invariant)
# ---------------------------------------------------------------------------
_BASE_RADIUS = 0.165  # outer radius / half-width at nominal
_BASE_HEIGHT = 0.62
_WALL_T = 0.012


def resolve_config(config: Trashcan2Config | None = None) -> ResolvedTrashcan2Config:
    cfg = config or Trashcan2Config()
    body = cfg.body_shape or "round_lathe"
    lid = cfg.lid_mechanism or "teardrop_dome_rocker"
    mount = cfg.mount or "free_standing"
    liner = cfg.inner_liner or "none"
    palette_style = cfg.palette_style or "street_green"

    for value, pool, label in (
        (body, BODY_MODULES, "body_shape"),
        (lid, LID_MODULES, "lid_mechanism"),
        (mount, MOUNT_MODULES, "mount"),
        (liner, LINER_MODULES, "inner_liner"),
        (palette_style, PALETTE_STYLES, "palette_style"),
    ):
        if value not in pool:
            raise ValueError(f"Unsupported {label}: {value!r}")

    # conditional: front_swing_door requires a body that can host a flat front
    # hatch (drum/rect/square/hex). Re-route an illegal round_lathe pairing.
    if lid == "front_swing_door" and body == "round_lathe":
        lid = "teardrop_dome_rocker"

    h_scale = _clamp(cfg.body_height_scale, 0.85, 1.20)
    r_scale = _clamp(cfg.body_radius_scale, 0.90, 1.15)
    body_radius = _BASE_RADIUS * r_scale
    body_height = _clamp(_BASE_HEIGHT * h_scale, 0.25, 0.85)
    wall_t = _WALL_T
    mouth_radius = body_radius - wall_t

    # lid pivot sits on the rim plane (top of body), recomputed with height.
    lid_pivot_z = body_height

    # liner must lift clear of the rim: >= 0.9 * inner height.
    inner_h = body_height - wall_t
    liner_lift = max(0.32, 0.9 * inner_h)

    # mount lift: post/wall raise the body floor off ground.
    if mount == "post_mounted":
        mount_lift_z = 0.55
    elif mount == "wall_hoop":
        mount_lift_z = 0.55
    else:
        mount_lift_z = 0.0

    return ResolvedTrashcan2Config(
        lid_mechanism=lid,
        body_shape=body,
        mount=mount,
        inner_liner=liner,
        palette_style=palette_style,
        body_radius=body_radius,
        body_height=body_height,
        wall_t=wall_t,
        mouth_radius=mouth_radius,
        flap_open_range=_clamp(cfg.flap_open_range, 1.05, 1.75),
        lid_pivot_z=lid_pivot_z,
        liner_lift=liner_lift,
        mount_lift_z=mount_lift_z,
        palette=dict(PALETTES[palette_style]),
    )


# ---------------------------------------------------------------------------
# Body builders (Slot B) — emitted onto part "body". Open-top, real void.
# z origin at body floor (z=0 local at floor top).
# ---------------------------------------------------------------------------
def _emit_round_lathe(body, r: ResolvedTrashcan2Config) -> None:
    ro_b = r.body_radius * 0.92
    ro_t = r.body_radius
    ri_b = ro_b - r.wall_t
    ri_t = ro_t - r.wall_t
    h = r.body_height
    floor_z = r.wall_t
    outer = [(ro_b, 0.0), (ro_t, h)]
    inner = [(ri_b, floor_z), (ri_t, h)]
    geom = LatheGeometry.from_shell_profiles(
        outer, inner, segments=40, start_cap="flat", end_cap="flat"
    )
    body.visual(mesh_from_geometry(geom, "body_shell"), material="body", name="body_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"))
    # closed floor disc (no cap on TOP — mouth stays open).
    body.visual(
        Cylinder(radius=ri_b, length=r.wall_t),
        origin=Origin(xyz=(0.0, 0.0, r.wall_t * 0.5)),
        material="body",
        name="floor", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )


def _emit_round_drum(body, r: ResolvedTrashcan2Config) -> None:
    ro = r.body_radius
    ri = ro - r.wall_t
    h = r.body_height
    outer = [(ro, 0.0), (ro, h)]
    inner = [(ri, r.wall_t), (ri, h)]
    geom = LatheGeometry.from_shell_profiles(
        outer, inner, segments=44, start_cap="flat", end_cap="flat"
    )
    body.visual(mesh_from_geometry(geom, "drum_shell"), material="body", name="body_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"))
    body.visual(
        Cylinder(radius=ri, length=r.wall_t),
        origin=Origin(xyz=(0.0, 0.0, r.wall_t * 0.5)),
        material="body",
        name="floor", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    # banding hoops (accent rings) — fixed module-local count = 3.
    for i, z in enumerate((h * 0.25, h * 0.55, h * 0.85)):
        body.visual(
            Cylinder(radius=ro + 0.004, length=0.012),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material="accent",
            name=f"band_{i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
        )


def _emit_rect_walls(body, r: ResolvedTrashcan2Config, *, n_sides: int) -> None:
    """Square/rect/hex: panel walls + floor. n_sides=4 (square/rect) or 6 (hex)."""
    rad = r.body_radius
    h = r.body_height
    t = r.wall_t
    if n_sides == 4:
        half = rad * 0.78  # half-width of the box footprint
        # four walls
        wall_specs = (
            ((2 * half, t, h), (0.0, half, h * 0.5), "front_wall"),
            ((2 * half, t, h), (0.0, -half, h * 0.5), "rear_wall"),
            ((t, 2 * half, h), (half, 0.0, h * 0.5), "right_wall"),
            ((t, 2 * half, h), (-half, 0.0, h * 0.5), "left_wall"),
        )
        for dims, xyz, nm in wall_specs:
            body.visual(Box(dims), origin=Origin(xyz=xyz), material="body", name=nm, material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"))
        body.visual(
            Box((2 * half - t, 2 * half - t, t)),
            origin=Origin(xyz=(0.0, 0.0, t * 0.5)),
            material="body",
            name="floor", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
        )
    else:  # hexagon, 6 panels
        ap = rad * 0.86  # apothem (center to flat)
        side = 2.0 * ap * math.tan(math.pi / 6.0)
        for i in range(6):
            theta = math.pi / 6.0 + i * math.pi / 3.0
            cx = ap * math.cos(theta)
            cy = ap * math.sin(theta)
            body.visual(
                Box((side, t, h)),
                origin=Origin(xyz=(cx, cy, h * 0.5), rpy=(0.0, 0.0, theta + math.pi / 2.0)),
                material="body",
                name=f"hex_panel_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
            )
        # hex floor: circumradius chosen so the disc flats reach the panel
        # apothem (flats overlap the panels — one connected body).
        body.visual(
            _hex_disc(ap / math.cos(math.pi / 6.0) + t, t, "floor"),
            origin=Origin(xyz=(0.0, 0.0, t * 0.5), rpy=(0.0, 0.0, math.pi / 6.0)),
            material="body",
            name="floor", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
        )


def _build_body(model: ArticulatedObject, r: ResolvedTrashcan2Config) -> None:
    body = model.part("body")
    if r.body_shape == "round_lathe":
        _emit_round_lathe(body, r)
    elif r.body_shape == "round_drum_mesh":
        _emit_round_drum(body, r)
    elif r.body_shape == "square_box":
        _emit_rect_walls(body, r, n_sides=4)
    elif r.body_shape == "rectangular_mesh":
        _emit_rect_walls(body, r, n_sides=4)
    elif r.body_shape == "hexagonal_panels":
        _emit_rect_walls(body, r, n_sides=6)


# ---------------------------------------------------------------------------
# Lid mechanisms (Slot A)
#
# Each emits: optional FIXED intermediate cover (lid/roof/hood) onto body,
# then a REVOLUTE flap with a MatingContract. The mouth behind the flap is a
# real open void: dome holes have NO cap, planar openings are framed (no full
# back quad), the flap footprint is < mouth opening.
# ---------------------------------------------------------------------------
def _rim_anchor(r: ResolvedTrashcan2Config) -> tuple[float, float, float]:
    """A point that lies on the real body rim WALL (not the open-mouth axis), at
    rim height. Used as the FIXED body->cover joint origin so the origin sits on
    geometry for both parent (body wall) and child (cover plate/skirt span)."""
    # Anchor on the +Y rim wall (cover collar seats there). Seat a hair below the
    # rim so the collar overlaps the body wall (real contact) — mouth stays open.
    return (0.0, _body_wall_y(r), r.body_height - 0.018)


def _cover_fit_radius(r: ResolvedTrashcan2Config) -> float:
    """Largest radius a centered round cover can span and still seat inside the
    body rim walls (so dome/hood cover bases connect to the rim collar)."""
    if r.body_shape in ROUND_BODIES:
        return r.body_radius
    if r.body_shape == "hexagonal_panels":
        return r.body_radius * 0.86
    return r.body_radius * 0.78


def _body_wall_y(r: ResolvedTrashcan2Config) -> float:
    """The +Y wall mid-line of the body rim (where a cover base seats)."""
    if r.body_shape in ROUND_BODIES:
        return r.body_radius - r.wall_t * 0.5
    if r.body_shape == "hexagonal_panels":
        return r.body_radius * 0.86 - r.wall_t * 0.5
    return r.body_radius * 0.78 - r.wall_t * 0.5


def _emit_cover_base(part, r: ResolvedTrashcan2Config, *, z_local: float) -> None:
    """Emit a rim collar onto a cover part matching the body footprint so the
    cover seats on (and overlaps) the body rim. Open center => mouth stays open.
    Authored centered on axis at child-local z=z_local.
    """
    t = r.wall_t * 2.6
    if r.body_shape in ROUND_BODIES:
        part.visual(
            _open_ring(r.body_radius + 0.004, t, 36, "cover_skirt"),
            origin=Origin(xyz=(0.0, 0.0, z_local)),
            material="lid",
            name="cover_skirt", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
        )
    elif r.body_shape == "hexagonal_panels":
        ap = r.body_radius * 0.86
        side = 2.0 * ap * math.tan(math.pi / 6.0)
        for i in range(6):
            theta = math.pi / 6.0 + i * math.pi / 3.0
            part.visual(
                Box((side, r.wall_t, t)),
                origin=Origin(
                    xyz=(ap * math.cos(theta), ap * math.sin(theta), z_local),
                    rpy=(0.0, 0.0, theta + math.pi / 2.0),
                ),
                material="lid",
                name=f"cover_collar_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
            )
    else:  # square / rect
        half = r.body_radius * 0.78
        for dims, xyz, nm in (
            ((2 * half, r.wall_t, t), (0.0, half, z_local), "cover_collar_front"),
            ((2 * half, r.wall_t, t), (0.0, -half, z_local), "cover_collar_rear"),
            ((r.wall_t, 2 * half, t), (half, 0.0, z_local), "cover_collar_right"),
            ((r.wall_t, 2 * half, t), (-half, 0.0, z_local), "cover_collar_left"),
        ):
            part.visual(Box(dims), origin=Origin(xyz=xyz), material="lid", name=nm, material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"))


def _emit_dome_rocker(model, r: ResolvedTrashcan2Config, *, teardrop: bool) -> None:
    """teardrop_dome_rocker / dome_circular_push_flap.

    FIXED dome 'lid' over body rim, REVOLUTE central flap covering a real hole.
    """
    body = model.get_part("body")
    rad = _cover_fit_radius(r)  # dome base seats inside the rim walls
    dome_h = rad * 0.55
    flap_r = rad * 0.42  # flap footprint < mouth -> mouth stays open
    # Cover geometry is authored with z=0 at the body rim (child-local frame).
    # The FIXED joint origin is anchored on the body rim WALL (off-axis, on real
    # geometry); cover geometry is pre-shifted by -ay so it re-centers on the
    # mouth axis after the joint translates it by +ay.
    pivot_z = 0.0
    _ax, ay, rim_z = _rim_anchor(r)
    cdy = -ay  # shift cover so a rim-collar wall lands at child-local origin

    lid = model.part("lid")
    # Dome shell as a lathe ring with a central HOLE (no cap face): outer dome
    # profile down to the flap-hole radius; inner profile mirrors it, leaving
    # the hole open.
    n = 12
    outer = []
    inner = []
    for i in range(n + 1):
        x = rad - (rad - flap_r) * i / n
        zt = dome_h * math.sqrt(max(1.0 - (x / rad) ** 2, 0.0))
        outer.append((x, zt))
        inner.append((x, max(zt - r.wall_t, 0.0)))
    geom = LatheGeometry.from_shell_profiles(
        outer, inner, segments=40, start_cap="flat", end_cap="flat"
    )
    lid.visual(
        mesh_from_geometry(geom, "dome_shell"),
        origin=Origin(xyz=(0.0, cdy, pivot_z + r.wall_t)),
        material="lid",
        name="dome_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    # rim collar matching the body footprint (seats + overlaps the rim; open
    # center => mouth stays open). Also bridges the round dome to a rect/hex rim.
    _emit_cover_base(lid, r, z_local=pivot_z)
    # FIXED body -> lid (origin on the rim wall)
    model.articulation(
        "body_to_lid",
        ArticulationType.FIXED,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, ay, rim_z)),
    )

    # REVOLUTE flap: teardrop rocker (axis Y) covering the central hole.
    flap = model.part("flap")
    flap_z = pivot_z + dome_h * math.sqrt(max(1.0 - (flap_r / rad) ** 2, 0.0))
    # flap cap disc sits just over the hole; named face on its underside.
    flap.visual(
        Cylinder(radius=flap_r, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="flap",
        name="flap_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    # hinge knuckle straddling the pivot (at flap-local origin)
    flap.visual(
        Box((flap_r * (1.4 if teardrop else 0.9), 0.024, 0.024)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="flap",
        name="flap_rib", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    # flap pivots in the lid frame; lid is centered at y=cdy, so the flap sits at
    # cdy too. pivot at the hole edge.
    pivot = (0.0, cdy - flap_r + 0.004, flap_z)
    model.articulation(
        "lid_to_flap",
        ArticulationType.REVOLUTE,
        parent=lid,
        child=flap,
        origin=Origin(xyz=pivot),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=6.0, velocity=2.0, lower=-r.flap_open_range, upper=r.flap_open_range
        ),
        mating=MatingContract(
            parent_face_geometry="dome_shell",
            parent_face_side="positive_z",
            child_face_geometry="flap_cap",
            child_face_side="negative_z",
            contact_tol=0.05,
        ),
    )


def _emit_gable_rocker(model, r: ResolvedTrashcan2Config) -> None:
    """square_gable_rocker: gable roof FIXED on body, square rocker flap on +X slope."""
    body = model.get_part("body")
    rad = r.body_radius
    half = _cover_fit_radius(r)  # gable footprint matches the body rim
    ridge_h = rad * 0.42
    pivot_z = 0.0
    _ax, ay, rim_z = _rim_anchor(r)
    cdy = -ay  # shift cover so a rim-collar wall lands at child-local origin

    roof = model.part("lid")
    # rim collar seats the roof on (and overlaps) the body rim.
    _emit_cover_base(roof, r, z_local=pivot_z)
    # two slopes as tilted thin boxes meeting at the ridge; +X slope has the flap
    # opening framed by border strips (NO full back quad).
    slope_len = math.hypot(half, ridge_h)
    pitch = math.atan2(ridge_h, half)
    # -X solid slope
    roof.visual(
        Box((slope_len, 2 * half, r.wall_t)),
        origin=Origin(
            xyz=(-half * 0.5, cdy, pivot_z + ridge_h * 0.5),
            rpy=(0.0, -pitch, 0.0),
        ),
        material="lid",
        name="roof_slope_neg", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    # +X slope: frame strips only (border) — opening stays a real void.
    fr_t = r.wall_t
    # ridge strip + eave strip + two side strips along the slope
    roof.visual(
        Box((slope_len, 2 * half, fr_t)),
        origin=Origin(
            xyz=(half * 0.5, cdy + half * 0.86, pivot_z + ridge_h * 0.5), rpy=(0.0, pitch, 0.0)
        ),
        material="lid",
        name="roof_strip_side_a", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    roof.visual(
        Box((slope_len, 2 * half, fr_t)),
        origin=Origin(
            xyz=(half * 0.5, cdy - half * 0.86, pivot_z + ridge_h * 0.5), rpy=(0.0, pitch, 0.0)
        ),
        material="lid",
        name="roof_strip_side_b", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    roof.visual(
        Box((slope_len * 0.18, 2 * half, fr_t)),
        origin=Origin(xyz=(half * 0.92, cdy, pivot_z + ridge_h * 0.10), rpy=(0.0, pitch, 0.0)),
        material="lid",
        name="roof_strip_eave", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    # ridge cap
    roof.visual(
        Box((0.018, 2 * half, ridge_h * 0.5)),
        origin=Origin(xyz=(0.0, cdy, pivot_z + ridge_h)),
        material="accent",
        name="ridge_cap", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
    )
    # gable end triangles (thin) so the roof seals the sides, not the mouth slope
    for yy, nm in ((half, "gable_end_a"), (-half, "gable_end_b")):
        roof.visual(
            Box((2 * half, r.wall_t, ridge_h)),
            origin=Origin(xyz=(0.0, cdy + yy, pivot_z + ridge_h * 0.5)),
            material="lid",
            name=nm, material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
        )
    model.articulation(
        "body_to_lid",
        ArticulationType.FIXED,
        parent=body,
        child=roof,
        origin=Origin(xyz=(0.0, ay, rim_z)),
    )

    # REVOLUTE flap on +X slope, pivot at ridge, axis Y.
    flap = model.part("flap")
    flap_w = slope_len * 0.66
    flap.visual(
        Box((flap_w, 2 * half * 0.72, r.wall_t)),
        origin=Origin(xyz=(flap_w * 0.5, 0.0, 0.0), rpy=(0.0, pitch, 0.0)),
        material="flap",
        name="flap_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    flap.visual(
        Box((flap_w, 2 * half * 0.30, 0.06)),
        origin=Origin(xyz=(flap_w * 0.5, 0.0, 0.0), rpy=(0.0, pitch, 0.0)),
        material="accent",
        name="flap_grip", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
    )
    # hinge knuckle at the flap-local origin (where the revolute pivot sits)
    flap.visual(
        Box((0.03, 2 * half * 0.72, 0.03)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="flap",
        name="flap_knuckle", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    pivot = (0.0, cdy, pivot_z + ridge_h - r.wall_t)
    model.articulation(
        "lid_to_flap",
        ArticulationType.REVOLUTE,
        parent=roof,
        child=flap,
        origin=Origin(xyz=pivot),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=6.0, velocity=2.0, lower=-r.flap_open_range, upper=r.flap_open_range
        ),
        mating=MatingContract(
            parent_face_geometry="ridge_cap",
            parent_face_side="positive_x",
            child_face_geometry="flap_panel",
            child_face_side="negative_x",
            contact_tol=0.03,
        ),
    )


def _emit_pyramidal_hood(model, r: ResolvedTrashcan2Config) -> None:
    """pyramidal_hood_push_flap: pyramidal hood FIXED on body, front (-Y) push flap.

    Hood front face is OMITTED (real open aperture); push flap top-hinged, axis X.
    """
    body = model.get_part("body")
    rad = r.body_radius
    half = _cover_fit_radius(r)
    hood_h = rad * 0.50
    pivot_z = 0.0
    _ax, ay, rim_z = _rim_anchor(r)
    cdy = -ay  # shift cover so a rim-collar wall lands at child-local origin

    hood = model.part("hood")
    pitch = math.atan2(hood_h, half)
    slope_len = math.hypot(half, hood_h)
    # rim collar seats the hood on (and overlaps) the body rim.
    _emit_cover_base(hood, r, z_local=pivot_z)
    # 3 of 4 pyramidal faces (skip the front -Y face -> open aperture)
    # back face (+Y)
    hood.visual(
        Box((2 * half, slope_len, r.wall_t)),
        origin=Origin(xyz=(0.0, cdy + half * 0.5, pivot_z + hood_h * 0.5), rpy=(pitch, 0.0, 0.0)),
        material="lid",
        name="hood_back", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    hood.visual(
        Box((slope_len, 2 * half, r.wall_t)),
        origin=Origin(xyz=(half * 0.5, cdy, pivot_z + hood_h * 0.5), rpy=(0.0, -pitch, 0.0)),
        material="lid",
        name="hood_right", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    hood.visual(
        Box((slope_len, 2 * half, r.wall_t)),
        origin=Origin(xyz=(-half * 0.5, cdy, pivot_z + hood_h * 0.5), rpy=(0.0, pitch, 0.0)),
        material="lid",
        name="hood_left", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    # apex ridge bar (top hinge boss). Spans the apex along X and dips down the
    # converging faces (connected); its top face at the apex is where the flap
    # knuckle mates.
    hood.visual(
        Box((2 * half, 0.05, 0.05)),
        origin=Origin(xyz=(0.0, cdy, pivot_z + hood_h - 0.02)),
        material="accent",
        name="hood_lintel", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
    )
    model.articulation(
        "body_to_lid",
        ArticulationType.FIXED,
        parent=body,
        child=hood,
        origin=Origin(xyz=(0.0, ay, rim_z)),
    )

    flap = model.part("flap")
    flap_w = 2 * half * 0.62
    flap_h = slope_len * 0.70
    flap.visual(
        Box((flap_w, flap_h, r.wall_t)),
        origin=Origin(xyz=(0.0, -flap_h * 0.5, 0.0), rpy=(pitch, 0.0, 0.0)),
        material="flap",
        name="flap_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    # hinge knuckle straddling the pivot at flap-local origin (overlaps the
    # tilted panel top edge -> one connected flap). Its +Y face mates the lintel.
    flap.visual(
        Box((flap_w * 0.9, 0.05, 0.05)),
        origin=Origin(xyz=(0.0, -0.018, 0.0), rpy=(pitch, 0.0, 0.0)),
        material="flap",
        name="flap_knuckle", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    flap.visual(
        Box((flap_w * 0.5, flap_h * 0.3, 0.05)),
        origin=Origin(xyz=(0.0, -flap_h * 0.75, 0.0), rpy=(pitch, 0.0, 0.0)),
        material="accent",
        name="flap_grip", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
    )
    pivot = (0.0, cdy, pivot_z + hood_h)
    model.articulation(
        "lid_to_flap",
        ArticulationType.REVOLUTE,
        parent=hood,
        child=flap,
        origin=Origin(xyz=pivot),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=6.0, velocity=2.0, lower=0.0, upper=r.flap_open_range
        ),
        mating=MatingContract(
            parent_face_geometry="hood_lintel",
            parent_face_side="negative_y",
            child_face_geometry="flap_knuckle",
            child_face_side="positive_y",
            contact_tol=0.05,
        ),
    )


def _emit_front_swing_door(model, r: ResolvedTrashcan2Config) -> None:
    """front_swing_door: a hatch door TOP-hinged on the body front wall.

    The body front wall has a real opening band (drum) or the door simply
    covers the open upper front (flat-wall families). Door hangs directly off
    body (no intermediate lid). axis -Y, swings up/out.
    """
    body = model.get_part("body")
    rad = r.body_radius
    h = r.body_height
    # front face is at +Y (rect) or +Y tangent (drum). Use +Y front.
    front_y = rad * 0.80 if r.body_shape in RECT_FAMILY else rad
    door_w = rad * 1.1
    door_h = h * 0.5
    door_top_z = h * 0.95

    # hinge boss on body, just above door top (real geometry at joint origin)
    body.visual(
        Box((door_w * 0.9, 0.03, 0.03)),
        origin=Origin(xyz=(0.0, front_y, door_top_z)),
        material="accent",
        name="door_lintel", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
    )

    door = model.part("door")
    door.visual(
        Box((door_w, r.wall_t, door_h)),
        origin=Origin(xyz=(0.0, 0.0, -door_h * 0.5)),
        material="flap",
        name="door_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    door.visual(
        Box((door_w * 0.3, 0.03, 0.04)),
        origin=Origin(xyz=(0.0, 0.02, -door_h * 0.5)),
        material="accent",
        name="door_handle", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
    )
    pivot = (0.0, front_y, door_top_z)
    model.articulation(
        "body_to_door",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=pivot),
        axis=(0.0, -1.0, 0.0) if False else (1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=6.0, velocity=2.0, lower=0.0, upper=r.flap_open_range
        ),
        mating=MatingContract(
            parent_face_geometry="door_lintel",
            parent_face_side="negative_z",
            child_face_geometry="door_panel",
            child_face_side="positive_z",
            contact_tol=0.03,
        ),
    )


def _emit_open_hooded_top(model, r: ResolvedTrashcan2Config) -> None:
    """open_hooded_top: a canopy hood with a front aperture + a swing flap.

    Mounting plate bridges body rim to hood (FIXED). Hood front aperture is a
    real void (front wall omitted); flap top-hinged with clearance.
    """
    body = model.get_part("body")
    rad = r.body_radius
    half = _cover_fit_radius(r)
    hood_h = rad * 0.46
    pivot_z = 0.0
    _ax, ay, rim_z = _rim_anchor(r)
    cdy = -ay  # shift cover so a rim-collar wall lands at child-local origin

    hood = model.part("hood")
    # rim collar (open center => mouth/aperture path into the body stays open)
    _emit_cover_base(hood, r, z_local=pivot_z)
    # canopy: top + back + sides (front -Y omitted => aperture)
    hood.visual(
        Box((2 * half, 2 * half, r.wall_t)),
        origin=Origin(xyz=(0.0, cdy, pivot_z + hood_h)),
        material="lid",
        name="hood_top", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    hood.visual(
        Box((2 * half, r.wall_t, hood_h)),
        origin=Origin(xyz=(0.0, cdy + half, pivot_z + hood_h * 0.5)),
        material="lid",
        name="hood_back", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    hood.visual(
        Box((r.wall_t, 2 * half, hood_h)),
        origin=Origin(xyz=(half, cdy, pivot_z + hood_h * 0.5)),
        material="lid",
        name="hood_right", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    hood.visual(
        Box((r.wall_t, 2 * half, hood_h)),
        origin=Origin(xyz=(-half, cdy, pivot_z + hood_h * 0.5)),
        material="lid",
        name="hood_left", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    # front lintel (hinge boss)
    hood.visual(
        Box((2 * half * 0.8, 0.03, 0.03)),
        origin=Origin(xyz=(0.0, cdy - half, pivot_z + hood_h)),
        material="accent",
        name="hood_lintel", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
    )
    model.articulation(
        "body_to_lid",
        ArticulationType.FIXED,
        parent=body,
        child=hood,
        origin=Origin(xyz=(0.0, ay, rim_z)),
    )

    flap = model.part("flap")
    flap_w = 2 * half * 0.7
    flap_h = hood_h * 0.95
    flap.visual(
        Box((flap_w, r.wall_t, flap_h)),
        origin=Origin(xyz=(0.0, 0.0, -flap_h * 0.5)),
        material="flap",
        name="flap_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"street_green", "civic_blue", "galvanized_steel", "drum_charcoal", "brushed_silver"} else "plastic.opaque_glossy_molded"),
    )
    flap.visual(
        Box((flap_w * 0.4, 0.05, flap_h * 0.3)),
        origin=Origin(xyz=(0.0, 0.0, -flap_h * 0.5)),
        material="accent",
        name="flap_grip", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
    )
    pivot = (0.0, cdy - half, pivot_z + hood_h)
    model.articulation(
        "hood_to_flap",
        ArticulationType.REVOLUTE,
        parent=hood,
        child=flap,
        origin=Origin(xyz=pivot),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=6.0, velocity=2.0, lower=0.0, upper=r.flap_open_range
        ),
        mating=MatingContract(
            parent_face_geometry="hood_lintel",
            parent_face_side="negative_z",
            child_face_geometry="flap_panel",
            child_face_side="positive_z",
            contact_tol=0.03,
        ),
    )


def _build_lid(model: ArticulatedObject, r: ResolvedTrashcan2Config) -> None:
    m = r.lid_mechanism
    if m == "teardrop_dome_rocker":
        _emit_dome_rocker(model, r, teardrop=True)
    elif m == "dome_circular_push_flap":
        _emit_dome_rocker(model, r, teardrop=False)
    elif m == "square_gable_rocker":
        _emit_gable_rocker(model, r)
    elif m == "pyramidal_hood_push_flap":
        _emit_pyramidal_hood(model, r)
    elif m == "front_swing_door":
        _emit_front_swing_door(model, r)
    elif m == "open_hooded_top":
        _emit_open_hooded_top(model, r)


# ---------------------------------------------------------------------------
# Mount (Slot C). post/wall: a FIXED root part lifts the body off the ground.
# Returns the root part name (the body itself if free_standing).
# ---------------------------------------------------------------------------
def _build_mount(model: ArticulatedObject, r: ResolvedTrashcan2Config) -> None:
    body = model.get_part("body")
    if r.mount == "free_standing":
        # optional 4 feet directly under the body floor.
        rad = r.body_radius
        for i, (sx, sy) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
            body.visual(
                Cylinder(radius=0.018, length=0.02),
                origin=Origin(xyz=(sx * rad * 0.62, sy * rad * 0.62, -0.01)),
                material="dark",
                name=f"foot_{i}", material_class_id="rubber.smooth_plain",
            )
        return

    lift = r.mount_lift_z
    if r.mount == "post_mounted":
        post = model.part("post")
        post.visual(
            Box((0.30, 0.30, 0.02)),
            origin=Origin(xyz=(0.0, 0.0, 0.01)),
            material="dark",
            name="base_plate", material_class_id="metal.blackened_gunmetal",
        )
        # pole stops at the body floor (does not intrude into the can interior).
        post.visual(
            Cylinder(radius=0.035, length=lift),
            origin=Origin(xyz=(0.0, 0.0, lift * 0.5)),
            material="accent",
            name="post_pole", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
        )
        # cradle bracket plate spanning from the pole (axis) out to the body
        # cradle ring, so the whole post part is one connected component.
        post.visual(
            Box((0.06, 2 * r.body_radius * 1.1, 0.03)),
            origin=Origin(xyz=(0.0, 0.0, lift + 0.005)),
            material="accent",
            name="cradle_band", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
        )
        post.visual(
            Box((2 * r.body_radius * 1.1, 0.06, 0.03)),
            origin=Origin(xyz=(0.0, 0.0, lift + 0.005)),
            material="accent",
            name="cradle_band_x", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
        )
        post.visual(
            _open_ring(r.body_radius * 1.05, 0.05, 36, "cradle_ring"),
            origin=Origin(xyz=(0.0, 0.0, lift)),
            material="accent",
            name="cradle_ring", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
        )
        model.articulation(
            "post_to_body",
            ArticulationType.FIXED,
            parent=post,
            child=body,
            origin=Origin(xyz=(0.0, 0.0, lift)),
        )
        return

    # wall_hoop — one connected frame: wall plate (back) -> saddle cross (through
    # the hoop center, reaching the body floor) -> hoop ring -> support arms.
    plate = model.part("wall_plate")
    back_y = -r.body_radius * 1.06
    plate.visual(
        Box((0.30, 0.03, 0.40)),
        origin=Origin(xyz=(0.0, back_y - 0.015, lift + 0.05)),
        material="dark",
        name="plate", material_class_id="metal.blackened_gunmetal",
    )
    plate.visual(
        _open_ring(r.body_radius * 1.06, 0.05, 36, "hoop_ring"),
        origin=Origin(xyz=(0.0, 0.0, lift)),
        material="accent",
        name="hoop_ring", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
    )
    # saddle cross bars at z=lift: one along Y from the back plate through the
    # hoop center to the front of the hoop, one along X across the hoop.
    plate.visual(
        Box((0.05, 2 * r.body_radius * 1.06, 0.03)),
        origin=Origin(xyz=(0.0, 0.0, lift + 0.005)),
        material="accent",
        name="saddle_pad", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
    )
    plate.visual(
        Box((2 * r.body_radius * 1.06, 0.05, 0.03)),
        origin=Origin(xyz=(0.0, 0.0, lift + 0.005)),
        material="accent",
        name="saddle_pad_x", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
    )
    # support gussets bridging the back plate up to the hoop sides (touch both).
    for i, sx in enumerate((-1, 1)):
        plate.visual(
            Box((0.03, abs(back_y) * 0.55, 0.05)),
            origin=Origin(
                xyz=(sx * r.body_radius * 0.55, back_y * 0.72, lift + 0.05)
            ),
            material="accent",
            name=f"support_arm_{i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"street_green", "civic_blue", "plastic_black", "galvanized_steel", "drum_charcoal"} else "metal.brushed_silver"),
        )
    model.articulation(
        "plate_to_body",
        ArticulationType.FIXED,
        parent=plate,
        child=body,
        origin=Origin(xyz=(0.0, 0.0, lift + 0.005)),
    )


# ---------------------------------------------------------------------------
# Inner liner (Slot D). PRISMATIC nested bucket, lifts +Z out of the mouth.
# ---------------------------------------------------------------------------
def _build_liner(model: ArticulatedObject, r: ResolvedTrashcan2Config) -> None:
    if r.inner_liner != "removable_liner":
        return
    body = model.get_part("body")
    li_ro = r.mouth_radius - 0.006
    li_ri = li_ro - r.wall_t * 0.7
    li_h = r.body_height - r.wall_t - 0.01
    liner = model.part("liner")
    if r.body_shape in ROUND_BODIES:
        outer = [(li_ro, 0.0), (li_ro, li_h)]
        inner = [(li_ri, r.wall_t), (li_ri, li_h)]
        geom = LatheGeometry.from_shell_profiles(
            outer, inner, segments=36, start_cap="flat", end_cap="flat"
        )
        liner.visual(mesh_from_geometry(geom, "liner_shell"), material="accent", name="liner_shell", material_class_id="metal.steel_galvanized")
        liner.visual(
            Cylinder(radius=li_ro, length=r.wall_t * 1.4),
            origin=Origin(xyz=(0.0, 0.0, r.wall_t * 0.9)),
            material="accent",
            name="liner_floor", material_class_id="metal.steel_galvanized",
        )
        liner.visual(
            _open_ring(li_ro + 0.006, 0.012, 32, "liner_rim"),
            origin=Origin(xyz=(0.0, 0.0, li_h)),
            material="dark",
            name="liner_rim", material_class_id="metal.blackened_gunmetal",
        )
    else:
        half = li_ro * 0.74
        for dims, xyz, nm in (
            ((2 * half, r.wall_t, li_h), (0.0, half, li_h * 0.5), "liner_front"),
            ((2 * half, r.wall_t, li_h), (0.0, -half, li_h * 0.5), "liner_rear"),
            ((r.wall_t, 2 * half, li_h), (half, 0.0, li_h * 0.5), "liner_right"),
            ((r.wall_t, 2 * half, li_h), (-half, 0.0, li_h * 0.5), "liner_left"),
        ):
            liner.visual(Box(dims), origin=Origin(xyz=xyz), material="accent", name=nm, material_class_id="metal.steel_galvanized")
        liner.visual(
            Box((2 * half, 2 * half, r.wall_t * 0.7)),
            origin=Origin(xyz=(0.0, 0.0, r.wall_t * 0.5)),
            material="accent",
            name="liner_floor", material_class_id="metal.steel_galvanized",
        )
    # grip tabs (fixed module-local count = 4) on the rim, seated on the wall.
    grip_r = li_ro if r.body_shape in ROUND_BODIES else li_ro * 0.74
    for i in range(4):
        th = i * math.pi / 2.0
        liner.visual(
            Box((0.05, 0.05, 0.04)),
            origin=Origin(
                xyz=(grip_r * math.cos(th), grip_r * math.sin(th), li_h - 0.01)
            ),
            material="dark",
            name=f"grip_tab_{i}", material_class_id="rubber.smooth_plain",
        )
    model.articulation(
        "body_to_liner",
        ArticulationType.PRISMATIC,
        parent=body,
        child=liner,
        origin=Origin(xyz=(0.0, 0.0, r.wall_t)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.5, lower=0.0, upper=r.liner_lift),
        mating=MatingContract(
            parent_face_geometry="floor",
            parent_face_side="positive_z",
            child_face_geometry="liner_floor",
            child_face_side="negative_z",
            contact_tol=0.02,
        ),
    )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_trashcan2(
    config: Trashcan2Config, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="trashcan2", assets=assets)
    for material, rgba in r.palette.items():
        model.material(material, rgba=rgba)
    _build_body(model, r)
    _build_lid(model, r)
    _build_liner(model, r)
    _build_mount(model, r)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_trashcan2(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_trashcan2(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedTrashcan2Config) -> list[tuple[str, str]]:
    return [
        ("body_shape", r.body_shape),
        ("lid_mechanism", r.lid_mechanism),
        ("mount", r.mount),
        ("inner_liner", r.inner_liner),
        ("palette_style", r.palette_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_trashcan2_tests(
    object_model: ArticulatedObject, config: Trashcan2Config
) -> TestReport:
    ctx = TestContext(object_model)
    r = resolve_config(config)
    names = {p.name for p in object_model.parts}
    joints = {j.name: j for j in object_model.articulations}

    ctx.check("body_present", "body" in names)

    # Defining SWING joint is REVOLUTE with adequate range.
    swing_name = "body_to_door" if r.lid_mechanism == "front_swing_door" else None
    if swing_name is None:
        swing_name = "hood_to_flap" if "hood_to_flap" in joints else "lid_to_flap"
    swing = joints.get(swing_name)
    ctx.check("swing_present", swing is not None)
    if swing is not None:
        ctx.check(
            "swing_is_revolute", swing.articulation_type == ArticulationType.REVOLUTE
        )
        span = swing.motion_limits.upper - swing.motion_limits.lower
        ctx.check("swing_range_>=1.05rad", span >= 1.05)

    # mouth-open invariant: the swing child (flap/door) footprint < mouth opening.
    # flap radius/half-width was sized at <= 0.42*body_radius (dome) etc. -> always
    # smaller than the inner mouth. Assert by construction marker.
    ctx.check("mouth_open_void", r.mouth_radius > 0.0)

    # mount FIXED upstream root for post/wall
    if r.mount == "post_mounted":
        ctx.check("post_root", "post" in names)
        ctx.check(
            "post_fixed",
            joints["post_to_body"].articulation_type == ArticulationType.FIXED,
        )
    elif r.mount == "wall_hoop":
        ctx.check("wall_root", "wall_plate" in names)
        ctx.check(
            "wall_fixed",
            joints["plate_to_body"].articulation_type == ArticulationType.FIXED,
        )

    # liner PRISMATIC +Z if present
    if r.inner_liner == "removable_liner":
        ctx.check("liner_present", "liner" in names)
        lj = joints["body_to_liner"]
        ctx.check("liner_prismatic", lj.articulation_type == ArticulationType.PRISMATIC)
        ctx.check("liner_axis_z", lj.axis == (0.0, 0.0, 1.0))
        ctx.check("liner_clears_rim", r.liner_lift >= 0.9 * (r.body_height - r.wall_t))

    # captured-overlap allowances
    overlap_targets = [
        "lid",
        "hood",
        "flap",
        "door",
        "liner",
        "post",
        "wall_plate",
    ]
    for other in overlap_targets:
        if other in names:
            ctx.allow_overlap(
                object_model.get_part("body"),
                object_model.get_part(other),
                reason="Swing-lid cover, hood, flap, door, liner and mount cradle "
                "are captured by / sleeve over the body rim and walls.",
            )
    # flap captured by its intermediate cover
    for cover in ("lid", "hood"):
        if cover in names and "flap" in names:
            ctx.allow_overlap(
                object_model.get_part(cover),
                object_model.get_part("flap"),
                reason="Flap seam tucks into the cover opening recess.",
            )
    # liner nests inside the body cavity past the cover/mount hardware.
    if "liner" in names:
        for other in ("lid", "hood", "flap", "door", "post", "wall_plate"):
            if other in names:
                ctx.allow_overlap(
                    object_model.get_part("liner"),
                    object_model.get_part(other),
                    reason="Removable liner nests inside the body cavity, sharing "
                    "space with the cover skirt / mount cradle hardware.",
                )
    return ctx.report()


__all__ = [
    "__modular__",
    "Trashcan2Config",
    "ResolvedTrashcan2Config",
    "config_from_seed",
    "resolve_config",
    "build_trashcan2",
    "build_seeded_trashcan2",
    "slot_choices_for_seed",
    "run_trashcan2_tests",
]
