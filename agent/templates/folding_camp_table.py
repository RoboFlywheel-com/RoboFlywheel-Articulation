# SPDX-License-Identifier: Apache-2.0

"""Folding camp table — modular procedural template (parallel-children).

Category identity: a portable, foldable/collapsible camp table — a raised
rectangular work surface on four-corner supports with at least one real
fold/telescope/collapse articulation, that packs down small.

Single root part ``tabletop`` carries the work surface + perimeter frame +
hardware + (optional) under-table storage as fixed visuals. Moving children
hang off it in parallel (no serial chain):

  * ``support_style`` (Slot B) — four folding/telescoping legs, each a REVOLUTE
    or PRISMATIC child of ``tabletop``.
  * ``top_extension`` (Slot D, optional) — a rear drop-leaf on its own REVOLUTE
    child part.

Two purely-visual (no new part) axes ride on the root:

  * ``surface_construction`` (Slot A, ③ Primary Form Family) — roll-top slats /
    solid panel / taut fabric membrane. Carries the slat-count multiplicity.
  * ``under_table_storage`` (Slot C) — none / fabric hammock / rigid lower shelf,
    emitted as root visuals sized to a central band that clears the legs.

Sources (5-star pool): origin A ``…1a04de6b…`` (compact slat roll-top, straight
REVOLUTE folding legs), origin B ``…e67ceec6…`` (rectangular slat top,
PRISMATIC telescoping legs, fabric+mesh hammock), plus forks
``var_solid_panel_top``, ``var_mesh_fabric_top``, ``var_splayed_aframe_legs``,
``var_x_cross_legs``, ``var_rigid_lower_shelf``, ``var_drop_leaf_extension``,
``var_slats_6`` / ``var_slats_20``.

Canonical spec: ``articraft_template_authoring/specs_modular_v1/folding_camp_table.md``
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
    ExtrudeGeometry,
    Inertial,
    MotionLimits,
    Origin,
    PerforatedPanelGeometry,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
SurfaceConstruction = Literal["roll_top_slats", "solid_panel", "fabric_mesh"]
SupportStyle = Literal[
    "straight_folding_legs",
    "telescoping_legs",
    "splayed_aframe_legs",
    "x_cross_legs",
]
UnderStorage = Literal["none", "fabric_hammock", "rigid_shelf"]
TopExtension = Literal["none", "drop_leaf"]
PaletteStyle = Literal[
    "gray_aluminum",
    "bamboo_wood",
    "olive_field",
    "coyote_two_tone",
    "graphite_orange",
]

SURFACE_CONSTRUCTIONS: tuple[SurfaceConstruction, ...] = (
    "roll_top_slats",
    "solid_panel",
    "fabric_mesh",
)
SUPPORT_STYLES: tuple[SupportStyle, ...] = (
    "straight_folding_legs",
    "telescoping_legs",
    "splayed_aframe_legs",
    "x_cross_legs",
)
UNDER_STORAGES: tuple[UnderStorage, ...] = ("none", "fabric_hammock", "rigid_shelf")
TOP_EXTENSIONS: tuple[TopExtension, ...] = ("none", "drop_leaf")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "gray_aluminum",
    "bamboo_wood",
    "olive_field",
    "coyote_two_tone",
    "graphite_orange",
)

# ---------------------------------------------------------------------------
# Material palettes. Roles: deck (work surface), frame (black perimeter rails +
# plastic connectors), accent (screws / hardware / hinge pins), tube (leg metal),
# rubber (feet), fabric (storage panel), binding (storage bound edge).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "gray_aluminum": {
        "deck": (0.54, 0.55, 0.54, 1.0),
        "frame": (0.05, 0.05, 0.05, 1.0),
        "accent": (0.83, 0.82, 0.78, 1.0),
        "tube": (0.54, 0.55, 0.54, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
        "fabric": (0.18, 0.18, 0.18, 1.0),
        "binding": (0.10, 0.11, 0.12, 1.0),
    },
    "bamboo_wood": {
        "deck": (0.72, 0.56, 0.36, 1.0),
        "frame": (0.09, 0.08, 0.07, 1.0),
        "accent": (0.80, 0.78, 0.72, 1.0),
        "tube": (0.50, 0.51, 0.52, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
        "fabric": (0.36, 0.27, 0.18, 1.0),
        "binding": (0.28, 0.20, 0.12, 1.0),
    },
    "olive_field": {
        "deck": (0.50, 0.51, 0.50, 1.0),
        "frame": (0.10, 0.10, 0.09, 1.0),
        "accent": (0.80, 0.80, 0.76, 1.0),
        "tube": (0.32, 0.38, 0.22, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
        "fabric": (0.26, 0.30, 0.18, 1.0),
        "binding": (0.20, 0.24, 0.14, 1.0),
    },
    "coyote_two_tone": {
        "deck": (0.72, 0.63, 0.46, 1.0),
        "frame": (0.20, 0.15, 0.10, 1.0),
        "accent": (0.78, 0.76, 0.70, 1.0),
        "tube": (0.55, 0.47, 0.34, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
        "fabric": (0.34, 0.28, 0.20, 1.0),
        "binding": (0.60, 0.50, 0.34, 1.0),
    },
    "graphite_orange": {
        "deck": (0.10, 0.10, 0.10, 1.0),
        "frame": (0.04, 0.04, 0.04, 1.0),
        "accent": (0.80, 0.80, 0.78, 1.0),
        "tube": (0.08, 0.08, 0.08, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
        "fabric": (0.09, 0.09, 0.09, 1.0),
        "binding": (0.95, 0.35, 0.06, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base geometry (parent A ~0.80 x 0.54, TOP_Z ~0.48). Scaled per-build.
# ---------------------------------------------------------------------------
_BASE_TABLE_X = 0.80
_BASE_TOP_Z = 0.48
_DECK_THICK = 0.024
_LEG_INSET_X = 0.075
_LEG_INSET_Y = 0.060
_LEG_R = 0.017
_SLAT_GAP = 0.006
_TELESCOPE_TRAVEL = 0.16


@dataclass(frozen=True)
class FoldingCampTableConfig:
    surface_construction: SurfaceConstruction = "roll_top_slats"
    support_style: SupportStyle = "straight_folding_legs"
    under_table_storage: UnderStorage = "none"
    top_extension: TopExtension = "none"
    palette_style: PaletteStyle = "gray_aluminum"
    slat_count: int = 9
    table_size_scale: float = 1.0
    table_aspect: float = 0.68
    table_height_scale: float = 1.0
    telescope_travel: float = _TELESCOPE_TRAVEL
    name: str = "folding_camp_table"


@dataclass(frozen=True)
class ResolvedFoldingCampTableConfig:
    surface_construction: SurfaceConstruction
    support_style: SupportStyle
    under_table_storage: UnderStorage
    top_extension: TopExtension
    palette_style: PaletteStyle
    slat_count: int
    table_x: float
    table_y: float
    top_z: float
    deck_thick: float
    leg_top_z: float
    leg_x: float
    leg_y: float
    leg_r: float
    leg_len: float
    slat_w: float
    slat_gap: float
    leg_fold_upper: float
    x_fold_upper: float
    telescope_travel: float
    storage_half_x: float
    storage_half_y: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> FoldingCampTableConfig:
    """Deterministic procedural sampling (seed 0 is not special, Contract 4)."""
    rng = random.Random(seed)
    return FoldingCampTableConfig(
        surface_construction=rng.choice(SURFACE_CONSTRUCTIONS),
        support_style=rng.choice(SUPPORT_STYLES),
        under_table_storage=rng.choice(UNDER_STORAGES),
        top_extension=rng.choice(TOP_EXTENSIONS),
        palette_style=rng.choice(PALETTE_STYLES),
        slat_count=rng.randint(6, 20),
        table_size_scale=round(rng.uniform(0.90, 1.30), 4),
        table_aspect=round(rng.uniform(0.62, 0.78), 4),
        table_height_scale=round(rng.uniform(0.85, 1.25), 4),
        telescope_travel=round(rng.uniform(0.10, 0.16), 4),
        name=f"seeded_folding_camp_table_{seed}",
    )


def resolve_config(
    config: FoldingCampTableConfig | None = None,
) -> ResolvedFoldingCampTableConfig:
    cfg = config or FoldingCampTableConfig()
    surface = _pick(cfg.surface_construction, SURFACE_CONSTRUCTIONS)
    support = _pick(cfg.support_style, SUPPORT_STYLES)
    storage = _pick(cfg.under_table_storage, UNDER_STORAGES)
    top_ext = _pick(cfg.top_extension, TOP_EXTENSIONS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    # Compatibility gate: x-cross leg tubes sweep the full table depth as they
    # fold, so a rear drop-leaf shares their swept volume — drop it for x-cross
    # (the leaf still realizes on the other three leg styles).
    if support == "x_cross_legs" and top_ext == "drop_leaf":
        top_ext = "none"

    size_scale = _clamp(cfg.table_size_scale, 0.90, 1.30)
    aspect = _clamp(cfg.table_aspect, 0.62, 0.78)
    height_scale = _clamp(cfg.table_height_scale, 0.85, 1.25)

    table_x = _BASE_TABLE_X * size_scale
    table_y = table_x * aspect
    top_z = _BASE_TOP_Z * height_scale
    leg_top_z = top_z - 0.055
    leg_x = table_x / 2.0 - _LEG_INSET_X
    leg_y = table_y / 2.0 - _LEG_INSET_Y
    leg_len = leg_top_z - 0.002

    slat_count = int(_clamp(cfg.slat_count, 6, 20))
    slat_gap = _SLAT_GAP
    slat_w = (table_x - (slat_count - 1) * slat_gap) / slat_count

    # Inequality: bound the inward REVOLUTE fold so left/right feet keep a >=40mm
    # tube gap at the sampled upper pose (foot travel L*sin(theta) short of the
    # half-span). Solved here, never left to fail in the builder.
    reach = max(0.05, leg_x - 0.07)
    leg_fold_upper = _clamp(math.asin(min(0.999, reach / leg_len)), 0.40, 0.50)
    # X-cross legs fold about X; keep a modest range so the crossed pair stays in
    # its declared crossing envelope.
    x_fold_upper = 0.50

    telescope_travel = _clamp(cfg.telescope_travel, 0.10, 0.16)

    # Storage lives in a central band that clears the corner legs (and the
    # x-cross tubes at |x|=leg_x) at every sampled pose.
    storage_half_x = max(0.10, leg_x - 0.055)
    storage_half_y = max(0.08, leg_y - 0.055)

    return ResolvedFoldingCampTableConfig(
        surface_construction=surface,
        support_style=support,
        under_table_storage=storage,
        top_extension=top_ext,
        palette_style=palette,
        slat_count=slat_count,
        table_x=table_x,
        table_y=table_y,
        top_z=top_z,
        deck_thick=_DECK_THICK,
        leg_top_z=leg_top_z,
        leg_x=leg_x,
        leg_y=leg_y,
        leg_r=_LEG_R,
        leg_len=leg_len,
        slat_w=slat_w,
        slat_gap=slat_gap,
        leg_fold_upper=leg_fold_upper,
        x_fold_upper=x_fold_upper,
        telescope_travel=telescope_travel,
        storage_half_x=storage_half_x,
        storage_half_y=storage_half_y,
        name=cfg.name or "folding_camp_table",
    )


def slot_choices_for_config(
    config: FoldingCampTableConfig | ResolvedFoldingCampTableConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedFoldingCampTableConfig)
        else resolve_config(config)
    )
    # slat multiplicity reported in coarse bands (spec §8): small / medium / large.
    if r.surface_construction == "roll_top_slats":
        band = "n_le8" if r.slat_count <= 8 else ("n_9_14" if r.slat_count <= 14 else "n_ge15")
    else:
        band = "n_a"
    return (
        ("surface_construction", r.surface_construction),
        ("support_style", r.support_style),
        ("under_table_storage", r.under_table_storage),
        ("top_extension", r.top_extension),
        ("slat_multiplicity", band),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Mesh helpers (built once per build, reused across the N-copy slat loop).
# ---------------------------------------------------------------------------
def _slat_mesh(slat_w: float, depth: float, name: str) -> object:
    return mesh_from_geometry(
        ExtrudeGeometry(
            rounded_rect_profile(slat_w, depth, radius=0.010, corner_segments=8),
            _DECK_THICK,
            center=True,
        ),
        name,
    )


def _diagonal_tube(dx: float, dy: float, dz: float, radius: float, name: str) -> object:
    return mesh_from_geometry(
        tube_from_spline_points(
            [(0.0, 0.0, 0.0), (dx, dy, dz)],
            radius=radius,
            samples_per_segment=8,
            radial_segments=14,
            cap_ends=True,
        ),
        name,
    )


# ---------------------------------------------------------------------------
# Shared perimeter frame + corner connectors + edge decoration (④). Emitted on
# the ``tabletop`` root for all three surface_construction modules.
# ---------------------------------------------------------------------------
def _emit_frame_and_decoration(tabletop, r: ResolvedFoldingCampTableConfig, mats) -> None:
    tx, ty, tz = r.table_x, r.table_y, r.top_z
    rail_z = tz - 0.012
    # Front / rear perimeter rails (black plastic).
    for y, name in ((-ty / 2.0 - 0.016, "front_rail"), (ty / 2.0 + 0.016, "rear_rail")):
        tabletop.visual(
            Box((tx + 0.030, 0.030, 0.034)),
            origin=Origin(xyz=(0.0, y, rail_z)),
            material=mats["frame"],
            name=name, material_class_id="plastic.opaque_generic",
        )
    for x, name in ((-tx / 2.0 - 0.016, "side_rail_0"), (tx / 2.0 + 0.016, "side_rail_1")):
        tabletop.visual(
            Box((0.030, ty + 0.026, 0.034)),
            origin=Origin(xyz=(x, 0.0, rail_z)),
            material=mats["frame"],
            name=name, material_class_id="plastic.opaque_generic",
        )
    # Underside cross rails tie the surface together (top reaches tz so they
    # embed into slats / solid panel / thin fabric alike).
    for y, tag in ((-0.16 * ty / 0.54, "front"), (0.16 * ty / 0.54, "rear")):
        tabletop.visual(
            Box((tx - 0.070, 0.022, 0.030)),
            origin=Origin(xyz=(0.0, y, tz - 0.015)),
            material=mats["frame"],
            name=f"underside_crossrail_{tag}", material_class_id="plastic.opaque_generic",
        )
    # Rounded corner connectors (④ decoration, ride-along).
    for idx, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        tabletop.visual(
            Sphere(radius=0.030),
            origin=Origin(xyz=(sx * (tx / 2.0 + 0.004), sy * (ty / 2.0 + 0.004), rail_z)),
            material=mats["frame"],
            name=f"corner_connector_{idx}", material_class_id="plastic.opaque_glossy_molded",
        )
    # Small edge logo mark (④).
    tabletop.visual(
        Box((0.085, 0.020, 0.0035)),
        origin=Origin(xyz=(-tx / 2.0 + 0.10, -ty / 2.0 - 0.020, tz + 0.006)),
        material=mats["accent"],
        name="small_edge_mark", material_class_id="metal.stainless_matte",
    )


def _emit_front_screw_row(
    tabletop, r: ResolvedFoldingCampTableConfig, mats, x_positions
) -> None:
    """Screw-head + oval-insert row along the front rail (④, host-derived)."""
    ty, tz = r.table_y, r.top_z
    for i, x in enumerate(x_positions):
        if i % 2 == 0:
            tabletop.visual(
                Box((0.042, 0.006, 0.014)),
                origin=Origin(xyz=(x, -ty / 2.0 - 0.033, tz - 0.006)),
                material=mats["frame"],
                name=f"front_oval_insert_{i}", material_class_id="plastic.opaque_generic",
            )
        for dx in (-0.020, 0.020):
            tabletop.visual(
                Cylinder(radius=0.006, length=0.003),
                origin=Origin(
                    xyz=(x + dx, -ty / 2.0 - 0.031, tz - 0.003),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=mats["accent"],
                name=f"front_screw_{i}_{0 if dx < 0 else 1}", material_class_id="metal.stainless_matte",
            )


# ---------------------------------------------------------------------------
# Slot A — surface_construction (③). All emit onto the tabletop root.
# ---------------------------------------------------------------------------
def _build_roll_top(tabletop, r: ResolvedFoldingCampTableConfig, mats) -> None:
    tx, ty, tz = r.table_x, r.table_y, r.top_z
    slat_mesh = _slat_mesh(r.slat_w, ty, "rounded_aluminum_slat")
    end_cap_mesh = mesh_from_geometry(
        ExtrudeGeometry(
            rounded_rect_profile(r.slat_w, 0.020, radius=0.006, corner_segments=6),
            0.012,
            center=True,
        ),
        "rounded_slat_end_cap",
    )
    x0 = -tx / 2.0 + r.slat_w / 2.0
    slat_xs = [x0 + i * (r.slat_w + r.slat_gap) for i in range(r.slat_count)]
    for i, x in enumerate(slat_xs):
        tabletop.visual(
            slat_mesh,
            origin=Origin(xyz=(x, 0.0, tz)),
            material=mats["deck"],
            name=f"slat_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"gray_aluminum", "olive_field", "coyote_two_tone", "graphite_orange"} else "wood.bamboo"),
        )
        for sy, suffix in ((-1, "front"), (1, "rear")):
            tabletop.visual(
                end_cap_mesh,
                origin=Origin(xyz=(x, sy * (ty / 2.0 + 0.006), tz - 0.003)),
                material=mats["frame"],
                name=f"{suffix}_cap_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
    # Dark gap strips between slats.
    for i in range(1, r.slat_count):
        gx = 0.5 * (slat_xs[i - 1] + slat_xs[i])
        tabletop.visual(
            Box((r.slat_gap * 0.65, ty + 0.012, 0.026)),
            origin=Origin(xyz=(gx, 0.0, tz + 0.0005)),
            material=mats["frame"],
            name=f"slat_gap_{i}", material_class_id="plastic.opaque_generic",
        )
    _emit_frame_and_decoration(tabletop, r, mats)
    _emit_front_screw_row(tabletop, r, mats, slat_xs)


def _build_solid_panel(tabletop, r: ResolvedFoldingCampTableConfig, mats) -> None:
    tx, ty, tz = r.table_x, r.table_y, r.top_z
    tabletop.visual(
        Box((tx, ty, r.deck_thick)),
        origin=Origin(xyz=(0.0, 0.0, tz)),
        material=mats["deck"],
        name="deck_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"gray_aluminum", "bamboo_wood", "olive_field", "coyote_two_tone"} else "plastic.opaque_glossy_molded"),
    )
    _emit_frame_and_decoration(tabletop, r, mats)
    span = tx - 0.10
    xs = [-span / 2.0 + i * span / 4.0 for i in range(5)]
    _emit_front_screw_row(tabletop, r, mats, xs)


def _build_fabric_mesh(tabletop, r: ResolvedFoldingCampTableConfig, mats) -> None:
    tx, ty, tz = r.table_x, r.table_y, r.top_z
    span_x = tx - 0.010
    span_y = ty - 0.010
    tabletop.visual(
        Box((span_x, span_y, 0.003)),
        origin=Origin(xyz=(0.0, 0.0, tz)),
        material=mats["fabric"],
        name="fabric_panel", material_class_id="fabric.open_mesh",
    )
    ew = 0.018
    for sy, name in ((-1, "front"), (1, "rear")):
        tabletop.visual(
            Box((span_x, ew, 0.005)),
            origin=Origin(xyz=(0.0, sy * (span_y / 2.0 - ew / 2.0), tz + 0.001)),
            material=mats["binding"],
            name=f"bound_edge_{name}", material_class_id="fabric.webbing",
        )
    for sx, name in ((-1, "left"), (1, "right")):
        tabletop.visual(
            Box((ew, span_y - 2.0 * ew, 0.005)),
            origin=Origin(xyz=(sx * (span_x / 2.0 - ew / 2.0), 0.0, tz + 0.001)),
            material=mats["binding"],
            name=f"bound_edge_{name}", material_class_id="fabric.webbing",
        )
    _emit_frame_and_decoration(tabletop, r, mats)


_SURFACE_BUILDERS = {
    "roll_top_slats": _build_roll_top,
    "solid_panel": _build_solid_panel,
    "fabric_mesh": _build_fabric_mesh,
}


# ---------------------------------------------------------------------------
# Slot B — support_style. Legs are REVOLUTE / PRISMATIC children of tabletop.
# ---------------------------------------------------------------------------
def _leg_positions(r: ResolvedFoldingCampTableConfig):
    return [
        (-r.leg_x, -r.leg_y),
        (r.leg_x, -r.leg_y),
        (r.leg_x, r.leg_y),
        (-r.leg_x, r.leg_y),
    ]


def _hinge_socket_box(r: ResolvedFoldingCampTableConfig) -> tuple[float, float]:
    """(center_z, height) for a hinge socket that spans from below the pin up to
    the deck surface (so it embeds into the thin fabric top as well as slats)."""
    socket_bot = r.leg_top_z - 0.020
    height = r.top_z - socket_bot
    return (socket_bot + height / 2.0, height)


def _emit_revolute_leg(
    model, tabletop, r, mats, i, x, y, *, splay: float, fold_out: bool
) -> None:
    """Straight (splay=0) or A-frame (splay>0) folding tubular leg."""
    # Hinge socket on the tabletop underside (fixed), reaching the deck surface.
    socket_cz, socket_h = _hinge_socket_box(r)
    tabletop.visual(
        Box((0.056, 0.052, socket_h)),
        origin=Origin(xyz=(x, y, socket_cz)),
        material=mats["frame"],
        name=f"hinge_socket_{i}", material_class_id="plastic.opaque_glossy_molded",
    )
    leg = model.part(f"leg_{i}")
    # Outward splay: the foot must land further from centre than the hinge.
    # Rotation about +Y by ``tilt`` sends the downward tube to foot x = -L*sin(tilt),
    # so an outward foot needs tilt<0 for x>0 legs and tilt>0 for x<0 legs.
    tilt = splay * (-1.0 if x > 0.0 else 1.0)
    st, ct = math.sin(tilt), math.cos(tilt)
    tube_len = r.leg_len - 0.022

    def along(dist: float) -> tuple[float, float, float]:
        # Point at ``dist`` down the (possibly tilted) leg axis.
        return (-dist * st, 0.0, -dist * ct)

    leg.visual(
        Cylinder(radius=0.011, length=0.058),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["accent"],
        name="hinge_pin", material_class_id="metal.stainless_matte",
    )
    cx, _, cz = along(tube_len / 2.0 + 0.003)
    leg.visual(
        Cylinder(radius=r.leg_r, length=tube_len),
        origin=Origin(xyz=(cx, 0.0, cz), rpy=(0.0, tilt, 0.0)),
        material=mats["tube"],
        name="straight_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"bamboo_wood", "olive_field", "coyote_two_tone", "graphite_orange"} else "metal.aluminum_bare"),
    )
    ccx, _, ccz = along(0.055)
    leg.visual(
        Cylinder(radius=0.023, length=0.060),
        origin=Origin(xyz=(ccx, 0.0, ccz), rpy=(0.0, tilt, 0.0)),
        material=mats["frame"],
        name="upper_collar", material_class_id="plastic.opaque_glossy_molded",
    )
    fx, _, fz = along(r.leg_len - 0.003)
    leg.visual(
        Cylinder(radius=0.020, length=0.036),
        origin=Origin(xyz=(fx, 0.0, fz), rpy=(0.0, tilt, 0.0)),
        material=mats["rubber"],
        name="rubber_foot", material_class_id="rubber.smooth_plain",
    )
    # Decorative diagonal brace stub on the leg (moves with it, always clear).
    bx, _, bz = along(r.leg_len * 0.55)
    inward = -1.0 if x > 0.0 else 1.0
    leg.visual(
        _diagonal_tube(inward * 0.10, 0.0, 0.05, 0.007, f"brace_stub_{i}"),
        origin=Origin(xyz=(bx, 0.0, bz)),
        material=mats["accent"],
        name="brace_stub", material_class_id="metal.stainless_matte",
    )
    leg.inertial = Inertial.from_geometry(
        Cylinder(radius=r.leg_r, length=r.leg_len),
        mass=0.5,
        origin=Origin(xyz=(0.0, 0.0, -r.leg_len / 2.0)),
    )
    # Straight legs fold inward-and-up (feet converge, bounded by leg_fold_upper).
    # Splayed A-frame feet start outboard; folding inward would first drop them to
    # vertical, so they fold OUTWARD-and-up instead (monotonic rise, feet diverge).
    axis_y = 1.0 if x > 0.0 else -1.0
    if fold_out:
        axis_y = -axis_y
    model.articulation(
        f"tabletop_to_leg_{i}",
        ArticulationType.REVOLUTE,
        parent=tabletop,
        child=leg,
        origin=Origin(xyz=(x, y, r.leg_top_z)),
        axis=(0.0, axis_y, 0.0),
        motion_limits=MotionLimits(effort=16.0, velocity=2.2, lower=0.0, upper=r.leg_fold_upper),
    )


def _build_straight_legs(model, tabletop, r, mats) -> list[str]:
    for i, (x, y) in enumerate(_leg_positions(r)):
        _emit_revolute_leg(model, tabletop, r, mats, i, x, y, splay=0.0, fold_out=False)
    return [f"leg_{i}" for i in range(4)]


def _build_splayed_legs(model, tabletop, r, mats) -> list[str]:
    for i, (x, y) in enumerate(_leg_positions(r)):
        _emit_revolute_leg(
            model, tabletop, r, mats, i, x, y, splay=math.radians(13.0), fold_out=True
        )
    return [f"leg_{i}" for i in range(4)]


def _build_telescoping_legs(model, tabletop, r, mats) -> list[str]:
    tz = r.top_z
    # Sleeve top reaches the deck surface so it embeds into the thin fabric top too.
    sleeve_top = tz
    sleeve_len = min(0.34, tz * 0.66)
    joint_z = sleeve_top - sleeve_len + 0.06
    for i, (x, y) in enumerate(_leg_positions(r)):
        # Fixed upper sleeve + collars + clamp knob on the tabletop.
        tabletop.visual(
            Cylinder(radius=0.018, length=sleeve_len),
            origin=Origin(xyz=(x, y, sleeve_top - sleeve_len / 2.0)),
            material=mats["tube"],
            name=f"leg_sleeve_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"bamboo_wood", "olive_field", "coyote_two_tone", "graphite_orange"} else "metal.aluminum_bare"),
        )
        tabletop.visual(
            Cylinder(radius=0.026, length=0.040),
            origin=Origin(xyz=(x, y, sleeve_top - sleeve_len + 0.020)),
            material=mats["frame"],
            name=f"lower_collar_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        tabletop.visual(
            Cylinder(radius=0.025, length=0.036),
            origin=Origin(xyz=(x, y, sleeve_top - 0.018)),
            material=mats["frame"],
            name=f"upper_collar_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        knob_side = 1.0 if y > 0.0 else -1.0
        tabletop.visual(
            Box((0.042, 0.075, 0.020)),
            origin=Origin(xyz=(x, y + knob_side * 0.045, joint_z + 0.03)),
            material=mats["frame"],
            name=f"leg_clamp_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        # Telescoping inner tube (moving child).
        leg = model.part(f"lower_leg_{i}")
        inner_top = 0.06
        inner_bot = -(joint_z + 0.02)
        inner_len = inner_top - inner_bot
        leg.visual(
            Cylinder(radius=0.012, length=inner_len),
            origin=Origin(xyz=(0.0, 0.0, (inner_top + inner_bot) / 2.0)),
            material=mats["tube"],
            name=f"inner_tube_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"bamboo_wood", "olive_field", "coyote_two_tone", "graphite_orange"} else "metal.aluminum_bare"),
        )
        leg.visual(
            Cylinder(radius=0.017, length=0.052),
            origin=Origin(xyz=(0.0, 0.0, 0.03)),
            material=mats["frame"],
            name=f"height_lock_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        leg.visual(
            Box((0.038, 0.055, 0.020)),
            origin=Origin(xyz=(0.0, knob_side * 0.026, 0.03)),
            material=mats["frame"],
            name=f"thumb_knob_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        leg.visual(
            Cylinder(radius=0.030, length=0.012),
            origin=Origin(xyz=(0.0, 0.0, inner_bot + 0.006)),
            material=mats["rubber"],
            name=f"foot_pad_{i}", material_class_id="rubber.smooth_plain",
        )
        leg.inertial = Inertial.from_geometry(
            Cylinder(radius=0.012, length=inner_len),
            mass=0.4,
            origin=Origin(xyz=(0.0, 0.0, (inner_top + inner_bot) / 2.0)),
        )
        model.articulation(
            f"table_to_lower_leg_{i}",
            ArticulationType.PRISMATIC,
            parent=tabletop,
            child=leg,
            origin=Origin(xyz=(x, y, joint_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=70.0, velocity=0.18, lower=0.0, upper=r.telescope_travel
            ),
        )
    return [f"lower_leg_{i}" for i in range(4)]


def _build_x_cross_legs(model, tabletop, r, mats) -> list[str]:
    positions = _leg_positions(r)
    spread_y = min(2.0 * r.leg_y, r.table_y - 0.10)
    drop = r.leg_top_z
    socket_cz, socket_h = _hinge_socket_box(r)
    for i, (px, py) in enumerate(positions):
        tabletop.visual(
            Box((0.056, 0.052, socket_h)),
            origin=Origin(xyz=(px, py, socket_cz)),
            material=mats["frame"],
            name=f"hinge_socket_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        y_sign = 1.0 if py < 0.0 else -1.0
        dy = y_sign * spread_y
        dz = -drop
        leg = model.part(f"leg_{i}")
        # Hinge pin along the fold axis (X).
        leg.visual(
            Cylinder(radius=0.011, length=0.058),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["accent"],
            name="hinge_pin", material_class_id="metal.stainless_matte",
        )
        leg.visual(
            _diagonal_tube(0.0, dy, dz, r.leg_r, f"xleg_tube_{i}"),
            origin=Origin(),
            material=mats["tube"],
            name="xleg_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"bamboo_wood", "olive_field", "coyote_two_tone", "graphite_orange"} else "metal.aluminum_bare"),
        )
        length = math.hypot(dy, dz)
        ua = 0.055 / length
        leg.visual(
            Cylinder(radius=0.023, length=0.054),
            origin=Origin(
                xyz=(0.0, dy * ua, dz * ua),
                rpy=(math.atan2(-dz, dy), 0.0, 0.0),
            ),
            material=mats["frame"],
            name="upper_collar", material_class_id="plastic.opaque_glossy_molded",
        )
        leg.visual(
            Cylinder(radius=0.020, length=0.030),
            origin=Origin(xyz=(0.0, dy, dz)),
            material=mats["rubber"],
            name="rubber_foot", material_class_id="rubber.smooth_plain",
        )
        # Central pivot bolt at the pair crossing (y == y_sign*leg_y).
        cross_t = r.leg_y / spread_y
        leg.visual(
            Cylinder(radius=0.012, length=0.030),
            origin=Origin(
                xyz=(0.0, y_sign * r.leg_y, -cross_t * drop),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["accent"],
            name="cross_pivot", material_class_id="metal.stainless_matte",
        )
        leg.inertial = Inertial.from_geometry(
            Box((0.05, spread_y, drop)),
            mass=0.5,
            origin=Origin(xyz=(0.0, dy / 2.0, dz / 2.0)),
        )
        axis_x = 1.0 if py < 0.0 else -1.0
        model.articulation(
            f"tabletop_to_leg_{i}",
            ArticulationType.REVOLUTE,
            parent=tabletop,
            child=leg,
            origin=Origin(xyz=(px, py, r.leg_top_z)),
            axis=(axis_x, 0.0, 0.0),
            motion_limits=MotionLimits(effort=16.0, velocity=2.2, lower=0.0, upper=r.x_fold_upper),
        )
    return [f"leg_{i}" for i in range(4)]


_SUPPORT_BUILDERS = {
    "straight_folding_legs": _build_straight_legs,
    "telescoping_legs": _build_telescoping_legs,
    "splayed_aframe_legs": _build_splayed_legs,
    "x_cross_legs": _build_x_cross_legs,
}


# ---------------------------------------------------------------------------
# Slot C — under_table_storage (root visuals, central band clears the legs).
# ---------------------------------------------------------------------------
def _build_fabric_hammock(tabletop, r: ResolvedFoldingCampTableConfig, mats) -> None:
    sx, sy = r.storage_half_x, r.storage_half_y
    hang_z = r.top_z - 0.13
    wall_top = hang_z + 0.075
    # Hub: the pocket floor. Everything else overlaps it or overlaps a piece that
    # does, so the whole hammock is one connected island reaching the deck.
    tabletop.visual(
        Box((2.0 * sx, 2.0 * sy, 0.020)),
        origin=Origin(xyz=(0.0, 0.0, hang_z)),
        material=mats["fabric"],
        name="pocket_bottom", material_class_id="fabric.canvas",
    )
    # Perforated mesh side walls; bottom edge embedded into the pocket floor.
    mesh_panel = PerforatedPanelGeometry(
        (2.0 * sx, 0.075),
        0.003,
        hole_diameter=0.006,
        pitch=0.014,
        frame=0.010,
        center=True,
    )
    for sgn, name in ((-1, "front"), (1, "rear")):
        tabletop.visual(
            mesh_from_geometry(mesh_panel, f"{name}_mesh_panel"),
            origin=Origin(
                xyz=(0.0, sgn * sy, hang_z + 0.028),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["fabric"],
            name=f"{name}_mesh_panel", material_class_id="fabric.open_mesh",
        )
    for sgn, name in ((-1, "left"), (1, "right")):
        tabletop.visual(
            Box((0.018, 2.0 * sy, 0.075)),
            origin=Origin(xyz=(sgn * sx, 0.0, hang_z + 0.028)),
            material=mats["fabric"],
            name=f"pocket_end_{name}", material_class_id="fabric.canvas",
        )
    # Orange/accent bound top edges, overlapping the mesh walls.
    for sgn, name in ((-1, "front"), (1, "rear")):
        tabletop.visual(
            Box((2.0 * sx + 0.02, 0.016, 0.020)),
            origin=Origin(xyz=(0.0, sgn * sy, wall_top - 0.010)),
            material=mats["binding"],
            name=f"{name}_binding", material_class_id="fabric.webbing",
        )
    # Corner hanger straps bridge the pocket floor up into the deck surface
    # (reaching z=top_z so they embed into slats / solid panel / thin fabric alike).
    strap_top = r.top_z
    strap_bot = hang_z - 0.006
    for cx in (-1, 1):
        for cy in (-1, 1):
            tabletop.visual(
                Box((0.024, 0.024, strap_top - strap_bot)),
                origin=Origin(
                    xyz=(cx * (sx - 0.014), cy * (sy - 0.014), (strap_top + strap_bot) / 2.0)
                ),
                material=mats["binding"],
                name=f"hanger_{0 if cx < 0 else 1}_{0 if cy < 0 else 1}", material_class_id="fabric.webbing",
            )


def _build_rigid_shelf(tabletop, r: ResolvedFoldingCampTableConfig, mats) -> None:
    sx, sy = r.storage_half_x, r.storage_half_y
    shelf_z = r.top_z * 0.42
    n = 5
    slat_w = (2.0 * sy) / (n + (n - 1) * 0.28)
    gap = slat_w * 0.28
    pitch = slat_w + gap
    y0 = -sy + slat_w / 2.0
    for i in range(n):
        tabletop.visual(
            Box((2.0 * sx, slat_w, 0.014)),
            origin=Origin(xyz=(0.0, y0 + i * pitch, shelf_z)),
            material=mats["fabric"],
            name=f"shelf_slat_{i}", material_class_id="fabric.webbing",
        )
    for idx, x in enumerate((-sx, sx)):
        tabletop.visual(
            Box((0.026, 2.0 * sy + 0.02, 0.020)),
            origin=Origin(xyz=(x, 0.0, shelf_z)),
            material=mats["frame"],
            name=f"shelf_end_rail_{idx}", material_class_id="plastic.opaque_generic",
        )
    # Corner brackets bridge the shelf up to the deck underside (support).
    for cx in (-1, 1):
        for cy in (-1, 1):
            top = r.top_z
            tabletop.visual(
                Cylinder(radius=0.008, length=top - shelf_z),
                origin=Origin(xyz=(cx * (sx - 0.01), cy * (sy - 0.01), (shelf_z + top) / 2.0)),
                material=mats["frame"],
                name=f"shelf_bracket_{0 if cx < 0 else 1}_{0 if cy < 0 else 1}", material_class_id="plastic.opaque_glossy_molded",
            )


_STORAGE_BUILDERS = {
    "fabric_hammock": _build_fabric_hammock,
    "rigid_shelf": _build_rigid_shelf,
}


# ---------------------------------------------------------------------------
# Slot D — top_extension (drop_leaf: REVOLUTE child at the rear edge).
# ---------------------------------------------------------------------------
def _build_drop_leaf(model, tabletop, r: ResolvedFoldingCampTableConfig, mats) -> None:
    tx, ty, tz = r.table_x, r.table_y, r.top_z
    hinge_y = ty / 2.0 + 0.030
    leaf_x = tx - 0.08
    leaf_depth = 0.22
    barrel_xs = [-leaf_x * 0.35, -leaf_x * 0.12, leaf_x * 0.12, leaf_x * 0.35]
    for idx, bx in enumerate(barrel_xs):
        tabletop.visual(
            Cylinder(radius=0.010, length=0.050),
            origin=Origin(xyz=(bx, hinge_y, tz), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["accent"],
            name=f"leaf_hinge_barrel_{idx}", material_class_id="metal.stainless_matte",
        )
    for bx in (-leaf_x * 0.28, leaf_x * 0.28):
        tabletop.visual(
            Box((0.022, 0.16, 0.014)),
            origin=Origin(xyz=(bx, hinge_y + 0.070, tz - 0.028)),
            material=mats["frame"],
            name=f"leaf_support_bracket_{'l' if bx < 0 else 'r'}", material_class_id="plastic.opaque_glossy_molded",
        )
    drop_leaf = model.part("drop_leaf")
    knuckle_xs = [-leaf_x * 0.22, 0.0, leaf_x * 0.22]
    for idx, kx in enumerate(knuckle_xs):
        drop_leaf.visual(
            Cylinder(radius=0.009, length=0.040),
            origin=Origin(xyz=(kx, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["accent"],
            name=f"leaf_knuckle_{idx}", material_class_id="metal.stainless_matte",
        )
    drop_leaf.visual(
        Box((leaf_x + 0.02, 0.024, r.deck_thick + 0.004)),
        origin=Origin(xyz=(0.0, 0.014, 0.0)),
        material=mats["frame"],
        name="leaf_hinge_strip", material_class_id="plastic.opaque_generic",
    )
    n_leaf = 4
    slat_d = (leaf_depth - (n_leaf - 1) * 0.006) / n_leaf
    leaf_slat_mesh = mesh_from_geometry(
        ExtrudeGeometry(
            rounded_rect_profile(leaf_x, slat_d, radius=0.005, corner_segments=6),
            r.deck_thick,
            center=True,
        ),
        "drop_leaf_slat",
    )
    y_start = 0.030
    for i in range(n_leaf):
        y = y_start + i * (slat_d + 0.006) + slat_d / 2.0
        drop_leaf.visual(
            leaf_slat_mesh,
            origin=Origin(xyz=(0.0, y, 0.0)),
            material=mats["deck"],
            name=f"leaf_slat_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"gray_aluminum", "olive_field", "coyote_two_tone", "graphite_orange"} else "wood.bamboo"),
        )
    far_y = y_start + n_leaf * slat_d + (n_leaf - 1) * 0.006
    drop_leaf.visual(
        Box((leaf_x + 0.030, 0.026, 0.030)),
        origin=Origin(xyz=(0.0, far_y + 0.013, -0.003)),
        material=mats["frame"],
        name="leaf_outer_rail", material_class_id="plastic.opaque_generic",
    )
    for sx, name in ((-leaf_x / 2.0 - 0.013, "l"), (leaf_x / 2.0 + 0.013, "r")):
        drop_leaf.visual(
            Box((0.026, far_y + 0.010, 0.030)),
            origin=Origin(xyz=(sx, far_y / 2.0, -0.003)),
            material=mats["frame"],
            name=f"leaf_side_rail_{name}", material_class_id="plastic.opaque_generic",
        )
    drop_leaf.inertial = Inertial.from_geometry(
        Box((leaf_x, leaf_depth, 0.03)),
        mass=0.6,
        origin=Origin(xyz=(0.0, y_start + leaf_depth / 2.0, 0.0)),
    )
    model.articulation(
        "tabletop_to_drop_leaf",
        ArticulationType.REVOLUTE,
        parent=tabletop,
        child=drop_leaf,
        origin=Origin(xyz=(0.0, hinge_y, tz)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=1.45),
    )


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------
def build_folding_camp_table(
    config: FoldingCampTableConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    mats = {
        role: model.material(f"fct_{role}_{r.palette_style}", rgba=rgba)
        for role, rgba in pal.items()
    }

    tabletop = model.part("tabletop")
    _SURFACE_BUILDERS[r.surface_construction](tabletop, r, mats)

    tabletop.inertial = Inertial.from_geometry(
        Box((r.table_x, r.table_y, 0.05)),
        mass=3.0,
        origin=Origin(xyz=(0.0, 0.0, r.top_z)),
    )

    _SUPPORT_BUILDERS[r.support_style](model, tabletop, r, mats)

    if r.under_table_storage != "none":
        _STORAGE_BUILDERS[r.under_table_storage](tabletop, r, mats)

    if r.top_extension == "drop_leaf":
        _build_drop_leaf(model, tabletop, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_folding_camp_table(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_folding_camp_table(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC
# ---------------------------------------------------------------------------
def _declare_leg_captures(ctx, model, r) -> None:
    """Element-scoped captured-pin / sleeve overlaps for the chosen legs."""
    tabletop = model.get_part("tabletop")
    support = r.support_style
    if support in ("straight_folding_legs", "splayed_aframe_legs"):
        for i in range(4):
            leg = model.get_part(f"leg_{i}")
            ctx.allow_overlap(
                tabletop, leg, elem_a=f"hinge_socket_{i}", elem_b="hinge_pin",
                reason="Folding-leg hinge pin captured inside the molded socket.",
            )
            ctx.allow_overlap(
                tabletop, leg, elem_a=f"hinge_socket_{i}", elem_b="straight_tube",
                reason="Leg tube has a short hidden insertion into the hinge socket.",
            )
            ctx.allow_overlap(
                tabletop, leg, elem_a=f"hinge_socket_{i}", elem_b="upper_collar",
                reason="Upper collar seats where the tube emerges from the socket.",
            )
    elif support == "telescoping_legs":
        # The concentric telescoping clamp hardware (fixed sleeve/collars/clamp on
        # the frame, sliding inner tube / height-lock / thumb knob on the leg) all
        # nests at the sleeve mouth and legitimately interpenetrates.
        for i in range(4):
            leg = model.get_part(f"lower_leg_{i}")
            for fixed in (f"leg_sleeve_{i}", f"lower_collar_{i}", f"upper_collar_{i}", f"leg_clamp_{i}"):
                for moving in (f"inner_tube_{i}", f"height_lock_{i}", f"thumb_knob_{i}"):
                    ctx.allow_overlap(
                        tabletop, leg, elem_a=fixed, elem_b=moving,
                        reason="Concentric telescoping clamp hardware nests at the sleeve mouth.",
                    )
    elif support == "x_cross_legs":
        for i in range(4):
            leg = model.get_part(f"leg_{i}")
            ctx.allow_overlap(
                tabletop, leg, elem_a=f"hinge_socket_{i}", elem_b="hinge_pin",
                reason="X-leg hinge pin captured inside the molded socket.",
            )
            ctx.allow_overlap(
                tabletop, leg, elem_a=f"hinge_socket_{i}", elem_b="xleg_tube",
                reason="X-leg tube begins inside the hinge socket at the pivot.",
            )
            ctx.allow_overlap(
                tabletop, leg, elem_a=f"hinge_socket_{i}", elem_b="upper_collar",
                reason="Upper collar seats where the X-leg tube emerges from the socket.",
            )
        # Each short-end pair crosses and shares a central pivot bolt; through the
        # whole fold the bypassing members and their collars/feet interpenetrate.
        pair_elems = ("xleg_tube", "cross_pivot", "upper_collar", "rubber_foot")
        for a, b in ((0, 3), (1, 2)):
            leg_a = model.get_part(f"leg_{a}")
            leg_b = model.get_part(f"leg_{b}")
            for ea in pair_elems:
                for eb in pair_elems:
                    ctx.allow_overlap(
                        leg_a, leg_b, elem_a=ea, elem_b=eb,
                        reason="Crossed X-leg pair bypasses through a shared central pivot bolt.",
                    )


def _declare_drop_leaf_captures(ctx, model) -> None:
    tabletop = model.get_part("tabletop")
    drop_leaf = model.get_part("drop_leaf")
    ctx.allow_overlap(
        tabletop, drop_leaf,
        reason="Interleaved drop-leaf hinge barrels/knuckles + strip form the captured continuous hinge at the rear edge.",
    )


def run_folding_camp_table_tests(
    object_model: ArticulatedObject,
    config: FoldingCampTableConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}

    # ---- captured / crossing overlaps (declared before geometric gates) ----
    _declare_leg_captures(ctx, object_model, r)
    if r.top_extension == "drop_leaf":
        _declare_drop_leaf_captures(ctx, object_model)

    # ---- baseline geometric / connectivity gates ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    # Rule 5: every non-FIXED joint must clear at every sampled pose (the declared
    # captured-pin / crossing allow_overlaps above are honored at each pose).
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    # ---- structural expectations ----
    tabletop = object_model.get_part("tabletop")
    ctx.check("tabletop present", "tabletop" in part_names)
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # Surface identity.
    if r.surface_construction == "roll_top_slats":
        ctx.check(
            "roll_top slats present",
            all(tabletop.get_visual(f"slat_{i}") is not None for i in range(r.slat_count)),
            details=f"slat_count={r.slat_count}",
        )
    elif r.surface_construction == "solid_panel":
        ctx.check("solid deck panel present", tabletop.get_visual("deck_panel") is not None)
    else:
        ctx.check("fabric panel present", tabletop.get_visual("fabric_panel") is not None)

    # Table footprint realistic.
    aabb = ctx.part_world_aabb(tabletop)
    if aabb is not None:
        (mnx, mny, _), (mxx, mxy, _) = aabb
        width = float(mxx - mnx)
        depth = float(mxy - mny)
        ctx.check("table width realistic", 0.60 <= width <= 1.30, details=f"w={width:.3f}")
        ctx.check("table depth realistic", 0.40 <= depth <= 1.10, details=f"d={depth:.3f}")

    # ---- support mechanism motion ----
    if r.support_style in ("straight_folding_legs", "splayed_aframe_legs", "x_cross_legs"):
        leg0 = object_model.get_part("leg_0")
        joint = object_model.get_articulation("tabletop_to_leg_0")
        rest = ctx.part_element_world_aabb(leg0, elem="rubber_foot")
        if rest is not None:
            ctx.check(
                "leg reaches ground when open",
                float(rest[0][2]) < 0.030,
                details=f"foot_min_z={rest[0][2]:.4f}",
            )
        with ctx.pose({joint: joint.motion_limits.upper}):
            folded = ctx.part_element_world_aabb(leg0, elem="rubber_foot")
        if rest is not None and folded is not None:
            ctx.check(
                "leg foot rises when folded",
                float(folded[0][2]) > float(rest[0][2]) + 0.030,
                details=f"rest={rest[0][2]:.4f}, folded={folded[0][2]:.4f}",
            )
    else:  # telescoping
        leg0 = object_model.get_part("lower_leg_0")
        joint = object_model.get_articulation("table_to_lower_leg_0")
        rest = ctx.part_world_position(leg0)
        with ctx.pose({joint: joint.motion_limits.upper}):
            high = ctx.part_world_position(leg0)
        if rest is not None and high is not None:
            ctx.check(
                "telescoping leg retracts upward",
                high[2] > rest[2] + 0.08,
                details=f"rest={rest[2]:.4f}, retracted={high[2]:.4f}",
            )

    # ---- drop-leaf motion ----
    if r.top_extension == "drop_leaf":
        drop_leaf = object_model.get_part("drop_leaf")
        leaf_joint = object_model.get_articulation("tabletop_to_drop_leaf")
        deployed = ctx.part_world_aabb(drop_leaf)
        with ctx.pose({leaf_joint: 1.30}):
            folded = ctx.part_world_aabb(drop_leaf)
        if deployed is not None and folded is not None:
            ctx.check(
                "drop leaf folds downward",
                float(folded[0][2]) < float(deployed[0][2]) - 0.05,
                details=f"deployed_min_z={deployed[0][2]:.4f}, folded_min_z={folded[0][2]:.4f}",
            )

    return ctx.report()


__all__ = (
    "FoldingCampTableConfig",
    "ResolvedFoldingCampTableConfig",
    "build_folding_camp_table",
    "build_seeded_folding_camp_table",
    "config_from_seed",
    "resolve_config",
    "run_folding_camp_table_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
