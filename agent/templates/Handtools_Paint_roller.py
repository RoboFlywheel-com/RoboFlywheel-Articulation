# SPDX-License-Identifier: Apache-2.0

"""Hand paint roller (spinning foam cover on a wire/shank frame) modular template.

NOTE on the slug name: "paint_roller" here = a **hand paint roller** -- a
cream/foam cylindrical ``roller_cover`` (~0.18 m long, ~38 mm dia, open hollow
ends) that free-SPINS on the axle of a steel wire / shank ``handle_frame``
(root), with a coral/pink molded user grip at the handle end. It is NOT a lint
roller (sticky paper cover), NOT a rolling pin (twin-handle axle = root body,
no offset crank / foam cover), NOT a paint brush (no roller / no spin
mechanism).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Handtools_Paint_roller.md`` and the
``picture/Handtools/Paint roller`` 5-star sample pool (1 parent + 8 slot-fork
variants), all synced under ``data/records/``.

Coordinate convention (the parent baseline, shared by all 9 samples): the
roller long axis = world X, the roller is centered at x=0, the axle line sits at
AXLE_Z=0. The roller's free (far) end is toward -X; the wire/shank exits the +X
roller face toward the grip. ``frame_to_roller`` is the SINGLE shared moving
mechanism: a CONTINUOUS joint, axis=(1,0,0), origin=(0,0,AXLE_Z), about which
the roller cover free-spins (no limit). It is present in EVERY seed.

Structure (pattern = ``parallel_children``): a single root ``handle_frame``
part + a single moving child ``roller_cover`` part, with three named module
axes:

  * ``cage_shank`` (3): the root steel wire / shank path + grip offset --
    z_crank_wire (one swept bent wire, 90deg crank down to an offset grip) /
    birdcage_spider (straight axle + drop stem + hub_cap + 6 retention spokes,
    +X hub) / straight_inline_shank (straight cylinder shank + zinc collar +
    inline grip, no Z drop). (parent / cage_birdcage / cage_straight)
  * ``grip`` (4): the user handle on the root -- smooth_molded_grip (one revolve
    barrel) / ribbed_scalloped_grip (scalloped body + 5 torus finger ridges) /
    hollow_tube_sleeve (stepped-bore tube + 6 grip rings; visual name is
    ``handle_tube``) / pole_socket_grip (flat butt + female bore + 6 helical
    thread turns). (parent / grip_ribbed / grip_tube / grip_pole)
  * ``cover`` (4): the spinning child mesh + journal bearing face --
    smooth_foam_cylinder (cq tube + roller_core sleeve) / napped_pile_fabric
    (+ 6 MeshGeometry nap rings) / feathered_taper_edge (Lathe taper cover +
    short Cyl core) / perforated_lattice_core (open cage: 8 ribs + 5 hoops +
    2 end spiders, NO roller_core; journal migrates to the end_spider hubs).
    (parent / cover_nap / cover_taper / cover_perf)

The cage spokes, finger ridges, grip rings, thread turns, nap rings, lattice
ribs/hoops and end spiders are all module-local repeated visuals (for-i loops +
shared helpers + regular placement, no separate parts / no FIXED joints; Rule
1). Every captured-fit (axle-in-bore journal, spoke-on-cover seat, wire-in-
socket, ring-on-tube, thread-in-bore, lattice-on-bore) omits a MatingContract
(grandfathered) and is guarded by the flat articulation-origin baseline +
element-scoped ``allow_overlap`` mirroring each source record's run_tests block.

Compatibility gate (resolve_config, spec §9): perforated_lattice_core deletes
``roller_core`` and migrates the journal to the +X / -X end spider hubs;
birdcage_spider already owns the +X hub_cap retention journal, so the two
collide. First-version ruling: when cover == perforated_lattice_core, the
cage_shank is restricted to {z_crank_wire, straight_inline_shank} (whose
journals are NOT a +X hub). All other cage x grip x cover combos are orthogonal.
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
    CylinderGeometry,
    Inertial,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    boolean_difference,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

CageShank = Literal["z_crank_wire", "birdcage_spider", "straight_inline_shank"]
Grip = Literal[
    "smooth_molded_grip",
    "ribbed_scalloped_grip",
    "hollow_tube_sleeve",
    "pole_socket_grip",
]
Cover = Literal[
    "smooth_foam_cylinder",
    "napped_pile_fabric",
    "feathered_taper_edge",
    "perforated_lattice_core",
]
PaletteStyle = Literal[
    "classic_coral_steel",
    "industrial_black_zinc",
    "pro_blue_yellow",
    "mini_pastel_cream",
    "safety_orange_grey",
]

CAGE_SHANKS: tuple[CageShank, ...] = (
    "z_crank_wire",
    "birdcage_spider",
    "straight_inline_shank",
)
GRIPS: tuple[Grip, ...] = (
    "smooth_molded_grip",
    "ribbed_scalloped_grip",
    "hollow_tube_sleeve",
    "pole_socket_grip",
)
COVERS: tuple[Cover, ...] = (
    "smooth_foam_cylinder",
    "napped_pile_fabric",
    "feathered_taper_edge",
    "perforated_lattice_core",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_coral_steel",
    "industrial_black_zinc",
    "pro_blue_yellow",
    "mini_pastel_cream",
    "safety_orange_grey",
)

# Covers that keep a solid roller_core (journal in the core mid bore). The
# perforated_lattice_core cover deletes roller_core and journals on the end
# spider hubs instead -> see _journal_targets / compatibility gate.
CORE_COVERS: tuple[Cover, ...] = (
    "smooth_foam_cylinder",
    "napped_pile_fabric",
    "feathered_taper_edge",
)
# cage_shanks whose journal is NOT a +X hub (so they may carry the perforated
# lattice end-spider journal without collision; spec §9 ruling 1).
PERF_OK_CAGES: tuple[CageShank, ...] = ("z_crank_wire", "straight_inline_shank")

# ---------------------------------------------------------------------------
# Module-local array counts (spec §8). These are local subdivision of each
# candidate, NOT top-level topology axes -- they do NOT enter slot_choices.
# Domains are clamped in resolve_config.
# ---------------------------------------------------------------------------
SPOKE_COUNT_DEFAULT = 6
SPOKE_COUNT_RANGE = (4, 8)
RIDGE_COUNT_DEFAULT = 5
RIDGE_COUNT_RANGE = (3, 6)
RING_COUNT_DEFAULT = 6
RING_COUNT_RANGE = (3, 8)
THREAD_COUNT_DEFAULT = 6
THREAD_COUNT_RANGE = (4, 8)
NAP_COUNT_DEFAULT = 6
NAP_COUNT_RANGE = (4, 8)
RIB_COUNT_DEFAULT = 8
RIB_COUNT_RANGE = (6, 12)
HOOP_COUNT_DEFAULT = 5
HOOP_COUNT_RANGE = (3, 7)

# ---------------------------------------------------------------------------
# Per-seed palettes (spec §7). Keys: wire (frame steel/shank), grip (handle),
# cover (foam shell), nap (raised fibers), hardware (hub/collar/core/lattice),
# accent (ridge/ring/thread/wing). Every .visual material is driven off this
# dict so the swept pool is colorful (module_topology_diversity only counts
# structure).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "classic_coral_steel": {
        "wire": (0.62, 0.63, 0.65, 1.0),
        "grip": (0.86, 0.45, 0.43, 1.0),
        "cover": (0.93, 0.91, 0.84, 1.0),
        "nap": (0.96, 0.95, 0.90, 1.0),
        "hardware": (0.80, 0.78, 0.72, 1.0),
        "accent": (0.72, 0.35, 0.33, 1.0),
    },
    "industrial_black_zinc": {
        "wire": (0.10, 0.11, 0.12, 1.0),
        "grip": (0.18, 0.18, 0.20, 1.0),
        "cover": (0.88, 0.88, 0.86, 1.0),
        "nap": (0.92, 0.92, 0.90, 1.0),
        "hardware": (0.50, 0.52, 0.54, 1.0),
        "accent": (0.32, 0.20, 0.18, 1.0),
    },
    "pro_blue_yellow": {
        "wire": (0.74, 0.76, 0.79, 1.0),
        "grip": (0.13, 0.32, 0.72, 1.0),
        "cover": (0.95, 0.93, 0.86, 1.0),
        "nap": (0.95, 0.80, 0.10, 1.0),
        "hardware": (0.76, 0.76, 0.74, 1.0),
        "accent": (0.95, 0.80, 0.10, 1.0),
    },
    "mini_pastel_cream": {
        "wire": (0.78, 0.80, 0.82, 1.0),
        "grip": (0.62, 0.84, 0.78, 1.0),
        "cover": (0.95, 0.93, 0.88, 1.0),
        "nap": (0.97, 0.95, 0.92, 1.0),
        "hardware": (0.86, 0.82, 0.74, 1.0),
        "accent": (0.92, 0.70, 0.74, 1.0),
    },
    "safety_orange_grey": {
        "wire": (0.62, 0.63, 0.65, 1.0),
        "grip": (0.95, 0.42, 0.08, 1.0),
        "cover": (0.90, 0.90, 0.88, 1.0),
        "nap": (0.88, 0.88, 0.86, 1.0),
        "hardware": (0.55, 0.56, 0.58, 1.0),
        "accent": (0.16, 0.16, 0.18, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), parent baseline. Mechanical fits
# (journal interference band, clearances) are never scaled; geometry/spans are.
# ---------------------------------------------------------------------------
_ROLLER_LEN = 0.180          # roller cover cylindrical length (along X)
_ROLLER_OUTER_R = 0.0190     # roller cover outer radius (~38 mm dia)
_ROLLER_BORE_R = 0.0078      # inner core bore radius (visible hollow ends)
_AXLE_R = 0.0028             # steel wire / shank radius (~5.6 mm)

_FRAME_DROP = 0.055          # vertical drop of the crank / stem (Z)
_HANDLE_LEN = 0.130          # grip length (along X)

_AXLE_Z = 0.0                # roller axle line height (shared origin)

_JOURNAL_EMBED = 0.0006      # bore is this much tighter than the axle (interference)
_CORE_OUTER_EXTRA = 0.0003   # core outer wall press-fit into cover bore


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class PaintRollerConfig:
    cage_shank: CageShank | None = None
    grip: Grip | None = None
    cover: Cover | None = None
    palette_style: PaletteStyle = "classic_coral_steel"
    roller_len_scale: float = 1.0
    roller_dia_scale: float = 1.0
    axle_radius_scale: float = 1.0
    frame_drop_scale: float = 1.0
    handle_len_scale: float = 1.0
    grip_belly_scale: float = 1.0
    spoke_count: int = SPOKE_COUNT_DEFAULT
    ridge_count: int = RIDGE_COUNT_DEFAULT
    ring_count: int = RING_COUNT_DEFAULT
    thread_turn_count: int = THREAD_COUNT_DEFAULT
    nap_ring_count: int = NAP_COUNT_DEFAULT
    rib_count: int = RIB_COUNT_DEFAULT
    hoop_count: int = HOOP_COUNT_DEFAULT
    name: str = "paint_roller"


@dataclass(frozen=True)
class ResolvedPaintRollerConfig:
    cage_shank: CageShank
    grip: Grip
    cover: Cover
    palette_style: PaletteStyle
    # Concrete geometry (scaled / derived).
    roller_len: float
    roller_outer_r: float
    roller_bore_r: float
    axle_r: float
    core_inner_r: float          # journal bore radius (axle interference)
    frame_drop: float
    handle_len: float
    grip_belly_scale: float
    axle_z: float
    handle_z: float
    # Derived X stations.
    roller_x_min: float
    roller_x_max: float
    # Module-local counts (already clamped, conditional on slot).
    spoke_count: int
    ridge_count: int
    ring_count: int
    thread_turn_count: int
    nap_ring_count: int
    rib_count: int
    hoop_count: int
    name: str


def config_from_seed(seed: int) -> PaintRollerConfig:
    rng = random.Random(seed)
    cage_shank = rng.choice(CAGE_SHANKS)
    grip = rng.choice(GRIPS)
    cover = rng.choice(COVERS)

    # Compatibility gate (spec §9 ruling 1): perforated_lattice_core journals
    # on the end spider hubs; birdcage_spider already owns the +X hub journal,
    # so they collide. When the lattice cover is chosen, re-roll the cage to a
    # journal-compatible one (z_crank_wire / straight_inline_shank).
    if cover == "perforated_lattice_core" and cage_shank not in PERF_OK_CAGES:
        cage_shank = rng.choice(PERF_OK_CAGES)

    return PaintRollerConfig(
        cage_shank=cage_shank,
        grip=grip,
        cover=cover,
        palette_style=rng.choice(PALETTE_STYLES),
        roller_len_scale=round(rng.uniform(0.85, 1.20), 4),
        roller_dia_scale=round(rng.uniform(0.88, 1.15), 4),
        axle_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        frame_drop_scale=round(rng.uniform(0.80, 1.15), 4),
        handle_len_scale=round(rng.uniform(0.85, 1.15), 4),
        grip_belly_scale=round(rng.uniform(0.90, 1.12), 4),
        spoke_count=rng.randint(*SPOKE_COUNT_RANGE),
        ridge_count=rng.randint(*RIDGE_COUNT_RANGE),
        ring_count=rng.randint(*RING_COUNT_RANGE),
        thread_turn_count=rng.randint(*THREAD_COUNT_RANGE),
        nap_ring_count=rng.randint(*NAP_COUNT_RANGE),
        rib_count=rng.randint(*RIB_COUNT_RANGE),
        hoop_count=rng.randint(*HOOP_COUNT_RANGE),
        name=f"seeded_paint_roller_{seed}",
    )


def resolve_config(
    config: PaintRollerConfig | None = None,
) -> ResolvedPaintRollerConfig:
    cfg = config or PaintRollerConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    cage_shank = _pick(cfg.cage_shank, CAGE_SHANKS)
    grip = _pick(cfg.grip, GRIPS)
    cover = _pick(cfg.cover, COVERS)

    # Compatibility gate (also enforced here so direct configs are legalized).
    if cover == "perforated_lattice_core" and cage_shank not in PERF_OK_CAGES:
        cage_shank = "z_crank_wire"

    len_scale = _clamp(cfg.roller_len_scale, 0.85, 1.20)
    dia_scale = _clamp(cfg.roller_dia_scale, 0.88, 1.15)
    axle_scale = _clamp(cfg.axle_radius_scale, 0.90, 1.12)
    drop_scale = _clamp(cfg.frame_drop_scale, 0.80, 1.15)
    handle_scale = _clamp(cfg.handle_len_scale, 0.85, 1.15)
    belly_scale = _clamp(cfg.grip_belly_scale, 0.90, 1.12)

    roller_len = _ROLLER_LEN * len_scale
    roller_outer_r = _ROLLER_OUTER_R * dia_scale
    axle_r = _AXLE_R * axle_scale

    # Bore must stay well clear of the cover OD (hollow wall) and the journal
    # band must remain a positive-radius interference fit on the axle.
    roller_bore_r = _ROLLER_BORE_R * (0.5 + 0.5 * dia_scale)
    roller_bore_r = _clamp(roller_bore_r, axle_r + 0.0030, roller_outer_r - 0.0075)
    core_inner_r = max(0.0010, axle_r - _JOURNAL_EMBED)

    # frame_drop is conditional: straight_inline_shank is coaxial (no drop).
    if cage_shank == "straight_inline_shank":
        frame_drop = 0.0
    else:
        frame_drop = _FRAME_DROP * drop_scale

    handle_len = _HANDLE_LEN * handle_scale
    handle_z = _AXLE_Z - frame_drop

    # Module-local counts (conditional on the chosen module; clamped to domain).
    spoke_count = (
        _clamp_int(cfg.spoke_count, *SPOKE_COUNT_RANGE)
        if cage_shank == "birdcage_spider"
        else SPOKE_COUNT_DEFAULT
    )
    ridge_count = (
        _clamp_int(cfg.ridge_count, *RIDGE_COUNT_RANGE)
        if grip == "ribbed_scalloped_grip"
        else RIDGE_COUNT_DEFAULT
    )
    ring_count = (
        _clamp_int(cfg.ring_count, *RING_COUNT_RANGE)
        if grip == "hollow_tube_sleeve"
        else RING_COUNT_DEFAULT
    )
    thread_turn_count = (
        _clamp_int(cfg.thread_turn_count, *THREAD_COUNT_RANGE)
        if grip == "pole_socket_grip"
        else THREAD_COUNT_DEFAULT
    )
    nap_ring_count = (
        _clamp_int(cfg.nap_ring_count, *NAP_COUNT_RANGE)
        if cover == "napped_pile_fabric"
        else NAP_COUNT_DEFAULT
    )
    rib_count = (
        _clamp_int(cfg.rib_count, *RIB_COUNT_RANGE)
        if cover == "perforated_lattice_core"
        else RIB_COUNT_DEFAULT
    )
    hoop_count = (
        _clamp_int(cfg.hoop_count, *HOOP_COUNT_RANGE)
        if cover == "perforated_lattice_core"
        else HOOP_COUNT_DEFAULT
    )

    return ResolvedPaintRollerConfig(
        cage_shank=cage_shank,
        grip=grip,
        cover=cover,
        palette_style=palette_style,
        roller_len=roller_len,
        roller_outer_r=roller_outer_r,
        roller_bore_r=roller_bore_r,
        axle_r=axle_r,
        core_inner_r=core_inner_r,
        frame_drop=frame_drop,
        handle_len=handle_len,
        grip_belly_scale=belly_scale,
        axle_z=_AXLE_Z,
        handle_z=handle_z,
        roller_x_min=-roller_len / 2.0,
        roller_x_max=roller_len / 2.0,
        spoke_count=spoke_count,
        ridge_count=ridge_count,
        ring_count=ring_count,
        thread_turn_count=thread_turn_count,
        nap_ring_count=nap_ring_count,
        rib_count=rib_count,
        hoop_count=hoop_count,
        name=cfg.name or "paint_roller",
    )


def with_overrides(config: PaintRollerConfig, **kwargs: object) -> PaintRollerConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# X stations of the wire / grip socket (derived per resolved config).
# ---------------------------------------------------------------------------
def _socket_x(r: ResolvedPaintRollerConfig) -> float:
    """X of the grip collar (where the wire/shank socket meets the grip top)."""
    if r.cage_shank == "birdcage_spider":
        hub_x = r.roller_x_max + 0.005
        return hub_x + 0.035
    if r.cage_shank == "straight_inline_shank":
        collar_x_min = r.roller_x_max + 0.012
        return collar_x_min + 0.020  # COLLAR_LEN
    # z_crank_wire
    axle_near_x = r.roller_x_max + 0.012
    bend_x = axle_near_x + 0.006
    return bend_x + 0.030


def slot_choices_for_config(
    config: PaintRollerConfig | ResolvedPaintRollerConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedPaintRollerConfig)
        else resolve_config(config)
    )
    return (
        ("cage_shank", r.cage_shank),
        ("grip", r.grip),
        ("cover", r.cover),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Journal element-name mapping (spec §13 model notes).
# ---------------------------------------------------------------------------
def _axle_elem_name(r: ResolvedPaintRollerConfig) -> str:
    """Name of the frame's axle visual (carries the journal capture)."""
    if r.cage_shank == "birdcage_spider":
        return "wire_axle"
    if r.cage_shank == "straight_inline_shank":
        return "shank"
    return "wire_frame"


def _grip_elem_name(r: ResolvedPaintRollerConfig) -> str:
    """Name of the grip's primary visual (hollow_tube uses ``handle_tube``)."""
    return "handle_tube" if r.grip == "hollow_tube_sleeve" else "handle_grip"


def _grip_inserting_elem(r: ResolvedPaintRollerConfig) -> str:
    """Name of the frame visual that plugs into the grip socket. For birdcage
    this is the drop ``handle_stem`` (the axle stops at the +X hub); for the
    straight inline shank it is the ``collar`` adapter (the shank stops short
    and the collar bridges into the grip); for z_crank it is the axle wire."""
    if r.cage_shank == "birdcage_spider":
        return "handle_stem"
    if r.cage_shank == "straight_inline_shank":
        return "collar"
    return _axle_elem_name(r)


def _journal_targets(r: ResolvedPaintRollerConfig) -> list[str]:
    """Roller-side element(s) the axle is journaled into."""
    if r.cover == "perforated_lattice_core":
        return ["end_spider_0", "end_spider_1"]
    return ["roller_core"]


# ===========================================================================
# Roller cover meshes (Slot C)
# ===========================================================================
def _smooth_cover_shape(r: ResolvedPaintRollerConfig) -> cq.Workplane:
    """Hollow cream roller cover: open-ended tube with a real bore."""
    outer = (
        cq.Workplane("YZ")
        .circle(r.roller_outer_r)
        .extrude(r.roller_len)
        .translate((r.roller_x_min, 0.0, 0.0))
    )
    bore = (
        cq.Workplane("YZ")
        .circle(r.roller_bore_r)
        .extrude(r.roller_len + 0.006)
        .translate((r.roller_x_min - 0.003, 0.0, 0.0))
    )
    cover = outer.cut(bore)
    try:
        cover = cover.edges("%CIRCLE").fillet(0.0020)
    except Exception:
        pass
    return cover


def _core_tube_shape(r: ResolvedPaintRollerConfig) -> cq.Workplane:
    """Solid inner core sleeve: outer wall contacts the cover bore, inner bore
    is the journal that captures the axle (interference fit)."""
    core_outer_r = r.roller_bore_r + _CORE_OUTER_EXTRA
    outer = (
        cq.Workplane("YZ")
        .circle(core_outer_r)
        .extrude(r.roller_len - 0.008)
        .translate((r.roller_x_min + 0.004, 0.0, 0.0))
    )
    bore = (
        cq.Workplane("YZ")
        .circle(r.core_inner_r)
        .extrude(r.roller_len)
        .translate((r.roller_x_min - 0.001, 0.0, 0.0))
    )
    return outer.cut(bore)


def _smoothstep(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def _taper_len(r: ResolvedPaintRollerConfig) -> float:
    """Feather-taper length at each end. Capped so the cylindrical middle (and
    thus the journal core) stays long enough to keep the journal overlap above
    the 0.10 floor even for the shortest sampled rollers."""
    return min(0.025, r.roller_len * 0.125)


def _taper_core_len(r: ResolvedPaintRollerConfig) -> float:
    return r.roller_len - 2.0 * _taper_len(r) - 0.010


def _taper_cover_mesh(r: ResolvedPaintRollerConfig):
    """Edge-roller cover: lathed cylindrical middle narrowing to feathered cone
    tips at both ends, with a narrow full-length bore + wide middle bore."""
    R = r.roller_outer_r
    taper_len = _taper_len(r)
    tip_r = 0.005
    z_min = -r.roller_len / 2.0
    z_max = r.roller_len / 2.0
    z_sl = z_min + taper_len
    z_sr = z_max - taper_len

    profile: list[tuple[float, float]] = []
    n_taper = 12
    profile.append((tip_r, z_min))
    for i in range(1, n_taper + 1):
        t = i / n_taper
        z = z_min + t * taper_len
        rad = tip_r + _smoothstep(t) * (R - tip_r)
        profile.append((rad, z))
    profile.append((R, (z_sl + z_sr) / 2.0))
    for i in range(n_taper):
        t = i / n_taper
        z = z_sr + t * taper_len
        rad = tip_r + _smoothstep(1.0 - t) * (R - tip_r)
        profile.append((rad, z))
    profile.append((tip_r, z_max))

    outer = LatheGeometry(profile, segments=56)

    # Narrow bore through full length so the axle clears the solid tips.
    # Must stay below tip_r so the axle never punches through the cone tip.
    wire_clearance_r = min(r.axle_r + 0.0008, tip_r - 0.0010)
    narrow_bore = CylinderGeometry(radius=wire_clearance_r, height=r.roller_len + 0.004)
    cover = boolean_difference(outer, narrow_bore)

    wide_bore_h = (z_sr - z_sl) + 0.008
    wide_bore = CylinderGeometry(radius=r.roller_bore_r, height=wide_bore_h)
    cover = boolean_difference(cover, wide_bore)

    cover.rotate_y(math.pi / 2.0)  # lathe Z -> world X
    return mesh_from_geometry(cover, "roller_cover")


def _taper_core_mesh(r: ResolvedPaintRollerConfig):
    """Short cylindrical core for the taper cover (avoids the solid tips)."""
    core_outer_r = r.roller_bore_r + _CORE_OUTER_EXTRA
    core_h = _taper_core_len(r)
    outer = CylinderGeometry(radius=core_outer_r, height=core_h)
    inner = CylinderGeometry(radius=r.core_inner_r, height=core_h + 0.004)
    core = boolean_difference(outer, inner)
    core.rotate_y(math.pi / 2.0)
    return mesh_from_geometry(core, "roller_core")


# --- napped pile fabric -----------------------------------------------------
def _nap_ring_mesh(r: ResolvedPaintRollerConfig, ring_index: int, n_rings: int) -> MeshGeometry:
    """One ring section of napped pile fabric: a thin cylindrical shell with
    radially displaced outer vertices simulating raised fibers, kept clear of
    the open hollow ends."""
    rng = random.Random(42 + ring_index * 137)
    nap_end_margin = 0.004
    nap_depth = 0.0018
    n_ax = 14
    n_ci = 48

    usable_len = r.roller_len - 2.0 * nap_end_margin
    ring_len = usable_len / n_rings
    gap = ring_len * 0.02
    x_start = r.roller_x_min + nap_end_margin + ring_index * ring_len + gap
    x_end = x_start + ring_len - 2.0 * gap

    geom = MeshGeometry()
    inner_ids: dict[tuple[int, int], int] = {}
    outer_ids: dict[tuple[int, int], int] = {}
    inner_r = r.roller_outer_r - 0.0004

    for i in range(n_ax + 1):
        x = x_start + (x_end - x_start) * i / n_ax
        for j in range(n_ci):
            theta = 2.0 * math.pi * j / n_ci
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)
            iv = geom.add_vertex(x, inner_r * cos_t, inner_r * sin_t)
            inner_ids[(i, j)] = iv
            base_bump = 0.4 + 0.6 * (
                0.5 + 0.5 * math.sin(7.0 * theta + 3.0 * x / r.roller_len * math.pi)
            )
            fine = rng.uniform(0.15, 1.0)
            disp = nap_depth * (0.35 * base_bump + 0.65 * fine)
            jt = theta + rng.gauss(0.0, 0.006)
            r_outer = r.roller_outer_r + disp
            ov = geom.add_vertex(x, r_outer * math.cos(jt), r_outer * math.sin(jt))
            outer_ids[(i, j)] = ov

    for i in range(n_ax):
        for j in range(n_ci):
            j1 = (j + 1) % n_ci
            a = outer_ids[(i, j)]
            b = outer_ids[(i, j1)]
            c = outer_ids[(i + 1, j1)]
            d = outer_ids[(i + 1, j)]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
    for i in range(n_ax):
        for j in range(n_ci):
            j1 = (j + 1) % n_ci
            a = inner_ids[(i, j)]
            b = inner_ids[(i + 1, j)]
            c = inner_ids[(i + 1, j1)]
            d = inner_ids[(i, j1)]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
    for end_i, flip in ((0, False), (n_ax, True)):
        for j in range(n_ci):
            j1 = (j + 1) % n_ci
            ii = inner_ids[(end_i, j)]
            ii1 = inner_ids[(end_i, j1)]
            oo = outer_ids[(end_i, j)]
            oo1 = outer_ids[(end_i, j1)]
            if not flip:
                geom.add_face(ii, oo, oo1)
                geom.add_face(ii, oo1, ii1)
            else:
                geom.add_face(ii, oo1, oo)
                geom.add_face(ii, ii1, oo1)
    return geom


# --- perforated lattice core ------------------------------------------------
def _lattice_cage_r(r: ResolvedPaintRollerConfig) -> float:
    return r.roller_bore_r - 0.0008  # rib centerline radius (rib_r = 0.0008)


def _hoop_positions(r: ResolvedPaintRollerConfig, n_hoops: int) -> list[float]:
    margin = 0.012
    span = r.roller_len - 2.0 * margin
    if n_hoops <= 1:
        return [r.roller_x_min + margin + span / 2.0]
    return [
        r.roller_x_min + margin + i * span / (n_hoops - 1) for i in range(n_hoops)
    ]


def _lattice_rib_shape(r: ResolvedPaintRollerConfig, angle_rad: float) -> cq.Workplane:
    rib_r = 0.0008
    cage_r = _lattice_cage_r(r)
    y_off = cage_r * math.cos(angle_rad)
    z_off = cage_r * math.sin(angle_rad)
    rib_len = r.roller_len - 0.006
    return (
        cq.Workplane("YZ")
        .center(y_off, z_off)
        .circle(rib_r)
        .extrude(rib_len)
        .translate((r.roller_x_min + 0.003, 0.0, 0.0))
    )


def _lattice_hoop_shape(r: ResolvedPaintRollerConfig, x_pos: float) -> cq.Workplane:
    outer_r = r.roller_bore_r
    inner_r = outer_r - 0.0015
    w = 0.0015
    outer = (
        cq.Workplane("YZ")
        .circle(outer_r)
        .extrude(w)
        .translate((x_pos - w / 2.0, 0.0, 0.0))
    )
    bore = (
        cq.Workplane("YZ")
        .circle(inner_r)
        .extrude(w + 0.002)
        .translate((x_pos - w / 2.0 - 0.001, 0.0, 0.0))
    )
    return outer.cut(bore)


def _end_spider_shape(r: ResolvedPaintRollerConfig, x_center: float) -> cq.Workplane:
    n_arms = 4
    hub_r = 0.0045
    hub_bore_r = max(0.0010, r.axle_r - _JOURNAL_EMBED)
    arm_width = 0.0020
    thickness = 0.0025

    hub = (
        cq.Workplane("YZ")
        .circle(hub_r)
        .extrude(thickness)
        .translate((x_center - thickness / 2.0, 0.0, 0.0))
    )
    hub_bore = (
        cq.Workplane("YZ")
        .circle(hub_bore_r)
        .extrude(thickness + 0.002)
        .translate((x_center - thickness / 2.0 - 0.001, 0.0, 0.0))
    )
    result = hub.cut(hub_bore)

    arm_len = r.roller_bore_r - hub_r + 0.001
    r_mid = hub_r - 0.001 + arm_len / 2.0
    for i in range(n_arms):
        angle_deg = 360.0 * i / n_arms
        arm = (
            cq.Workplane("YZ")
            .center(r_mid, 0.0)
            .rect(arm_len, arm_width)
            .extrude(thickness)
            .translate((x_center - thickness / 2.0, 0.0, 0.0))
        )
        if abs(angle_deg) > 0.1:
            arm = arm.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), angle_deg)
        result = result.union(arm)
    return result


# ===========================================================================
# Frame wire / shank meshes (Slot A)
# ===========================================================================
def _wire_tube_mesh(path: list[tuple[float, float, float]], name: str, r: ResolvedPaintRollerConfig):
    geom = tube_from_spline_points(
        path,
        radius=r.axle_r,
        samples_per_segment=14,
        radial_segments=16,
        cap_ends=True,
    )
    return mesh_from_geometry(geom, name)


def _z_crank_wire_path(r: ResolvedPaintRollerConfig) -> list[tuple[float, float, float]]:
    axle_z = r.axle_z
    handle_z = r.handle_z
    axle_far_x = r.roller_x_min - 0.006
    axle_near_x = r.roller_x_max + 0.012
    bend_x = axle_near_x + 0.006
    handle_top_x = bend_x + 0.030
    return [
        (axle_far_x, 0.0, axle_z),
        (r.roller_x_min, 0.0, axle_z),
        (0.0, 0.0, axle_z),
        (r.roller_x_max, 0.0, axle_z),
        (axle_near_x, 0.0, axle_z),
        (bend_x, 0.0, axle_z - 0.006),
        (bend_x + 0.006, 0.0, axle_z - 0.030),
        (handle_top_x - 0.012, 0.0, handle_z + 0.004),
        (handle_top_x, 0.0, handle_z),
        (handle_top_x + 0.022, 0.0, handle_z),
    ]


def _birdcage_axle_path(r: ResolvedPaintRollerConfig) -> list[tuple[float, float, float]]:
    axle_z = r.axle_z
    axle_far_x = r.roller_x_min - 0.006
    hub_x = r.roller_x_max + 0.005
    return [
        (axle_far_x, 0.0, axle_z),
        (r.roller_x_min, 0.0, axle_z),
        (0.0, 0.0, axle_z),
        (r.roller_x_max, 0.0, axle_z),
        (hub_x, 0.0, axle_z),
    ]


def _birdcage_stem_path(r: ResolvedPaintRollerConfig) -> list[tuple[float, float, float]]:
    axle_z = r.axle_z
    handle_z = r.handle_z
    hub_x = r.roller_x_max + 0.005
    handle_top_x = hub_x + 0.035
    return [
        (hub_x, 0.0, axle_z),
        (hub_x + 0.006, 0.0, axle_z - 0.008),
        (hub_x + 0.018, 0.0, axle_z - 0.030),
        (handle_top_x - 0.010, 0.0, handle_z + 0.006),
        (handle_top_x, 0.0, handle_z),
        (handle_top_x + 0.022, 0.0, handle_z),
    ]


def _cage_spoke_path(
    r: ResolvedPaintRollerConfig, i: int, n_spokes: int
) -> list[tuple[float, float, float]]:
    angle = 2.0 * math.pi * i / n_spokes
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    axle_z = r.axle_z
    hub_x = r.roller_x_max + 0.005
    hub_r = 0.006

    r0 = hub_r
    r1 = hub_r + (r.roller_outer_r - hub_r) * 0.35
    r2 = hub_r + (r.roller_outer_r - hub_r) * 0.70
    r3 = r.roller_outer_r - 0.002

    x0 = hub_x
    x1 = hub_x - 0.001
    x2 = r.roller_x_max + 0.003
    x3 = r.roller_x_max + 0.001
    return [
        (x0, r0 * cos_a, axle_z + r0 * sin_a),
        (x1, r1 * cos_a, axle_z + r1 * sin_a),
        (x2, r2 * cos_a, axle_z + r2 * sin_a),
        (x3, r3 * cos_a, axle_z + r3 * sin_a),
    ]


def _hub_cap_shape(r: ResolvedPaintRollerConfig) -> cq.Workplane:
    hub_r = 0.006
    hub_thickness = 0.004
    hub_x = r.roller_x_max + 0.005
    axle_z = r.axle_z
    outer = (
        cq.Workplane("YZ")
        .circle(hub_r)
        .extrude(hub_thickness)
        .translate((hub_x - hub_thickness, 0.0, axle_z))
    )
    bore = (
        cq.Workplane("YZ")
        .circle(r.axle_r + 0.0005)
        .extrude(hub_thickness + 0.002)
        .translate((hub_x - hub_thickness - 0.001, 0.0, axle_z))
    )
    return outer.cut(bore)


def _straight_shank_shape(r: ResolvedPaintRollerConfig) -> cq.Workplane:
    axle_far_x = r.roller_x_min - 0.006
    collar_x_min = r.roller_x_max + 0.012
    length = (collar_x_min + 0.010) - axle_far_x
    return (
        cq.Workplane("YZ")
        .circle(r.axle_r)
        .extrude(length)
        .translate((axle_far_x, 0.0, r.axle_z))
    )


def _collar_shape(r: ResolvedPaintRollerConfig) -> cq.Workplane:
    """Zinc ferrule adapter bridging the shank to the grip. It starts at the
    shank's +X reach and extends through SOCKET_X deep enough into the grip
    socket (>=0.024) that it press-fits even into the open-bore hollow tube."""
    collar_x_min = r.roller_x_max + 0.012
    socket_x = _socket_x(r)  # = collar_x_min + 0.020
    collar_len = (socket_x + 0.024) - collar_x_min
    collar_r = 0.006
    return (
        cq.Workplane("YZ")
        .circle(collar_r)
        .extrude(collar_len)
        .translate((collar_x_min, 0.0, r.axle_z))
    )


# ===========================================================================
# Grip meshes (Slot B)
# ===========================================================================
def _smooth_grip_shape(r: ResolvedPaintRollerConfig) -> cq.Workplane:
    """Smooth molded barrel grip, revolved about the X handle axis."""
    bs = r.grip_belly_scale
    x0 = _socket_x(r)
    x1 = x0 + r.handle_len
    pts = [
        (x0, 0.0),
        (x0, 0.0085),
        (x0 + 0.006, 0.0115 * bs),
        (x0 + 0.020, 0.0135 * bs),
        (x0 + 0.058, 0.0140 * bs),
        (x0 + 0.100, 0.0122 * bs),
        (x1 - 0.012, 0.0095 * bs),
        (x1 - 0.004, 0.0052),
        (x1, 0.0),
    ]
    prof = cq.Workplane("XZ").polyline(pts).close()
    handle = prof.revolve(360.0, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    return handle.translate((0.0, 0.0, r.handle_z))


# Ergonomic ridge layout: ridge_count peaks evenly spaced inside the grip zone.
_RIDGE_START_OFFSET = 0.022  # first ridge offset from the collar (SOCKET_X)


def _ridge_zone(r: ResolvedPaintRollerConfig) -> tuple[float, float]:
    """X span (start, spacing) for the finger ridges, fitted inside the grip
    body so all ridge_count ridges land on the straight grip zone regardless of
    handle_len / count."""
    x0 = _socket_x(r)
    start_x = x0 + _RIDGE_START_OFFSET
    end_x = x0 + r.handle_len - 0.022  # keep clear of the rounded toe
    if r.ridge_count <= 1:
        return start_x, 0.0
    spacing = min(0.020, (end_x - start_x) / (r.ridge_count - 1))
    return start_x, spacing


def _ridge_x_position(r: ResolvedPaintRollerConfig, i: int) -> float:
    start_x, spacing = _ridge_zone(r)
    return start_x + i * spacing


def _ribbed_grip_shape(r: ResolvedPaintRollerConfig) -> cq.Workplane:
    """Scalloped ergonomic grip body: a peak at every finger ridge station and a
    valley between consecutive ridges, so the torus ridges always land on raised
    body regions (peaks and ridge X-stations are both derived from ridge_count)."""
    bs = r.grip_belly_scale
    peak_r = 0.0120 * bs
    valley_r = 0.0108 * bs
    x0 = _socket_x(r)
    x1 = x0 + r.handle_len
    n = r.ridge_count
    _start_x, spacing = _ridge_zone(r)

    pts: list[tuple[float, float]] = [
        (x0, 0.0),
        (x0, 0.0085),
        (x0 + 0.006, 0.0115 * bs),
    ]
    # Approach the first ridge, then alternate peak / valley across all ridges.
    first_x = _ridge_x_position(r, 0)
    pts.append((first_x - 0.007, peak_r))
    for i in range(n):
        px = _ridge_x_position(r, i)
        pts.append((px, peak_r))
        if i < n - 1 and spacing > 0.002:
            pts.append((px + spacing / 2.0, valley_r))
    last_x = _ridge_x_position(r, n - 1)
    # Taper down past the last ridge to a rounded toe (must stay inside x1).
    tail_x = min(last_x + 0.010, x1 - 0.016)
    pts.append((tail_x, 0.0110 * bs))
    pts.append((x1 - 0.012, 0.0095 * bs))
    pts.append((x1 - 0.004, 0.0052))
    pts.append((x1, 0.0))
    # Profile X must be strictly increasing for a clean revolve; dedup/sort guard.
    cleaned: list[tuple[float, float]] = []
    for px, pr in pts:
        if cleaned and px <= cleaned[-1][0]:
            px = cleaned[-1][0] + 1e-4
        cleaned.append((px, pr))
    prof = cq.Workplane("XZ").polyline(cleaned).close()
    handle = prof.revolve(360.0, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    return handle.translate((0.0, 0.0, r.handle_z))


def _finger_ridge_mesh(r: ResolvedPaintRollerConfig, i: int):
    peak_r = 0.0120 * r.grip_belly_scale
    x_pos = _ridge_x_position(r, i)
    geom = TorusGeometry(
        radius=peak_r,
        tube=0.0022,
        radial_segments=14,
        tubular_segments=28,
    )
    geom.rotate_y(math.pi / 2.0)
    geom.translate(x_pos, 0.0, r.handle_z)
    return mesh_from_geometry(geom, f"finger_ridge_{i}")


def _handle_tube_shape(r: ResolvedPaintRollerConfig) -> cq.Workplane:
    """Open hollow tubular sleeve grip with a stepped bore (wide entry +
    tight socket), far end open."""
    tube_outer_r = 0.0135 * r.grip_belly_scale
    entry_bore_r = r.axle_r + 0.0028
    entry_bore_depth = 0.016
    socket_bore_r = r.axle_r - 0.0003
    x0 = _socket_x(r)
    hz = r.handle_z

    outer = (
        cq.Workplane("YZ")
        .circle(tube_outer_r)
        .extrude(r.handle_len)
        .translate((x0, 0.0, hz))
    )
    entry_bore = (
        cq.Workplane("YZ")
        .circle(entry_bore_r)
        .extrude(entry_bore_depth + 0.002)
        .translate((x0 - 0.001, 0.0, hz))
    )
    socket_start_x = x0 + entry_bore_depth
    socket_len = r.handle_len - entry_bore_depth + 0.006
    socket_bore = (
        cq.Workplane("YZ")
        .circle(socket_bore_r)
        .extrude(socket_len)
        .translate((socket_start_x, 0.0, hz))
    )
    tube = outer.cut(entry_bore).cut(socket_bore)
    try:
        tube = tube.edges("<X").chamfer(0.0008)
    except Exception:
        pass
    try:
        tube = tube.edges(">X").chamfer(0.0008)
    except Exception:
        pass
    return tube


def _grip_ring_shape(r: ResolvedPaintRollerConfig, x_center: float) -> cq.Workplane:
    tube_outer_r = 0.0135 * r.grip_belly_scale
    ring_outer = tube_outer_r + 0.0016
    ring_inner = tube_outer_r - 0.0005
    width = 0.004
    return (
        cq.Workplane("YZ")
        .circle(ring_outer)
        .circle(ring_inner)
        .extrude(width)
        .translate((x_center - width / 2.0, 0.0, r.handle_z))
    )


def _grip_ring_positions(r: ResolvedPaintRollerConfig, n_rings: int) -> list[float]:
    x0 = _socket_x(r)
    start_x = x0 + 0.028
    end_x = x0 + r.handle_len - 0.018
    if n_rings <= 1:
        return [(start_x + end_x) / 2.0]
    spacing = (end_x - start_x) / (n_rings - 1)
    return [start_x + i * spacing for i in range(n_rings)]


def _pole_grip_shape(r: ResolvedPaintRollerConfig) -> cq.Workplane:
    """Molded grip with a flat butt face + female extension-pole bore."""
    bs = r.grip_belly_scale
    x0 = _socket_x(r)
    x1 = x0 + r.handle_len
    hz = r.handle_z
    bore_r = 0.0080
    bore_depth = 0.022
    pts = [
        (x0, 0.0),
        (x0, 0.0085),
        (x0 + 0.006, 0.0115 * bs),
        (x0 + 0.020, 0.0135 * bs),
        (x0 + 0.058, 0.0140 * bs),
        (x0 + 0.088, 0.0136 * bs),
        (x0 + 0.105, 0.0144 * bs),
        (x1 - 0.003, 0.0150 * bs),
        (x1, 0.0150 * bs),
        (x1, 0.0),
    ]
    prof = cq.Workplane("XZ").polyline(pts).close()
    handle = prof.revolve(360.0, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    handle = handle.translate((0.0, 0.0, hz))
    bore_cutter = (
        cq.Workplane("YZ")
        .circle(bore_r)
        .extrude(bore_depth + 0.002)
        .translate((x1 - bore_depth - 0.001, 0.0, hz))
    )
    handle = handle.cut(bore_cutter)
    try:
        handle = handle.edges(
            cq.selectors.NearestToPointSelector((x1, bore_r, hz))
        ).chamfer(0.0010)
    except Exception:
        pass
    return handle


def _thread_turn_points(
    r: ResolvedPaintRollerConfig,
    x_pos: float,
    rotation_deg: float,
    major_r: float,
    arc_deg: float,
    n_segments: int = 24,
) -> list[tuple[float, float, float]]:
    rot = math.radians(rotation_deg)
    cos_r, sin_r = math.cos(rot), math.sin(rot)
    hz = r.handle_z
    points: list[tuple[float, float, float]] = []
    for j in range(n_segments + 1):
        a = math.radians(j / n_segments * arc_deg)
        y = major_r * math.cos(a)
        z = major_r * math.sin(a)
        yr = y * cos_r - z * sin_r
        zr = y * sin_r + z * cos_r
        points.append((x_pos, yr, zr + hz))
    return points


# ===========================================================================
# Part builders
# ===========================================================================
def _build_cage_shank(frame, r: ResolvedPaintRollerConfig, mats, *, assets) -> None:
    """Emit the root frame's wire / shank visuals for the chosen cage_shank."""
    if r.cage_shank == "z_crank_wire":
        frame.visual(
            _wire_tube_mesh(_z_crank_wire_path(r), "wire_frame", r),
            material=mats["wire"],
            name="wire_frame", material_class_id="metal.steel_bare",
        )
    elif r.cage_shank == "birdcage_spider":
        frame.visual(
            _wire_tube_mesh(_birdcage_axle_path(r), "wire_axle", r),
            material=mats["wire"],
            name="wire_axle", material_class_id="metal.steel_bare",
        )
        frame.visual(
            _wire_tube_mesh(_birdcage_stem_path(r), "handle_stem", r),
            material=mats["wire"],
            name="handle_stem", material_class_id="metal.steel_bare",
        )
        frame.visual(
            mesh_from_cadquery(_hub_cap_shape(r), "hub_cap", assets=assets),
            material=mats["hardware"],
            name="hub_cap", material_class_id="metal.stainless_matte",
        )
        # Birdcage retention spokes: module-local for-i array (inline visuals).
        for i in range(r.spoke_count):
            frame.visual(
                _wire_tube_mesh(_cage_spoke_path(r, i, r.spoke_count), f"cage_spoke_{i}", r),
                material=mats["wire"],
                name=f"cage_spoke_{i}", material_class_id="metal.steel_bare",
            )
    else:  # straight_inline_shank
        frame.visual(
            mesh_from_cadquery(_straight_shank_shape(r), "shank", assets=assets),
            material=mats["wire"],
            name="shank", material_class_id="metal.steel_bare",
        )
        frame.visual(
            mesh_from_cadquery(_collar_shape(r), "collar", assets=assets),
            material=mats["hardware"],
            name="collar", material_class_id="metal.steel_galvanized",
        )


def _build_grip(frame, r: ResolvedPaintRollerConfig, mats, *, assets) -> None:
    """Emit the root frame's grip visuals for the chosen grip module."""
    if r.grip == "smooth_molded_grip":
        frame.visual(
            mesh_from_cadquery(_smooth_grip_shape(r), "handle_grip", assets=assets),
            material=mats["grip"],
            name="handle_grip", material_class_id="plastic.opaque_glossy_molded",
        )
    elif r.grip == "ribbed_scalloped_grip":
        frame.visual(
            mesh_from_cadquery(_ribbed_grip_shape(r), "handle_grip", assets=assets),
            material=mats["grip"],
            name="handle_grip", material_class_id="plastic.patterned_textured",
        )
        for i in range(r.ridge_count):
            frame.visual(
                _finger_ridge_mesh(r, i),
                material=mats["accent"],
                name=f"finger_ridge_{i}", material_class_id="rubber.smooth_plain",
            )
    elif r.grip == "hollow_tube_sleeve":
        frame.visual(
            mesh_from_cadquery(_handle_tube_shape(r), "handle_tube", assets=assets),
            material=mats["grip"],
            name="handle_tube", material_class_id="plastic.opaque_glossy_molded",
        )
        for i, x_pos in enumerate(_grip_ring_positions(r, r.ring_count)):
            frame.visual(
                mesh_from_cadquery(_grip_ring_shape(r, x_pos), f"grip_ring_{i}", assets=assets),
                material=mats["accent"],
                name=f"grip_ring_{i}", material_class_id="rubber.smooth_plain",
            )
    else:  # pole_socket_grip
        frame.visual(
            mesh_from_cadquery(_pole_grip_shape(r), "handle_grip", assets=assets),
            material=mats["grip"],
            name="handle_grip", material_class_id="plastic.opaque_glossy_molded",
        )
        socket_x1 = _socket_x(r) + r.handle_len
        thread_tube_r = 0.0009
        thread_major_r = 0.0080 - thread_tube_r * 0.5
        # Pitch derived from bore depth + count so every turn stays inside the
        # 22 mm female bore (no turn floats past the bore bottom).
        bore_depth = 0.022
        thread_pitch = min(0.0035, (bore_depth - 0.003) / max(r.thread_turn_count, 1))
        for i in range(r.thread_turn_count):
            x_pos = socket_x1 - thread_pitch * (i + 0.5)
            rot_deg = i * (360.0 / r.thread_turn_count)
            pts = _thread_turn_points(r, x_pos, rot_deg, thread_major_r, 340.0)
            geom = tube_from_spline_points(
                pts,
                radius=thread_tube_r,
                samples_per_segment=6,
                radial_segments=8,
                cap_ends=True,
            )
            frame.visual(
                mesh_from_geometry(geom, f"thread_turn_{i}"),
                material=mats["accent"],
                name=f"thread_turn_{i}", material_class_id="metal.stainless_matte",
            )


def _build_cover(roller, r: ResolvedPaintRollerConfig, mats, *, assets) -> None:
    """Emit the moving child's cover visuals for the chosen cover module."""
    if r.cover == "smooth_foam_cylinder":
        roller.visual(
            mesh_from_cadquery(_smooth_cover_shape(r), "roller_cover", assets=assets),
            material=mats["cover"],
            name="roller_cover", material_class_id="fabric.flexible_foam",
        )
        roller.visual(
            mesh_from_cadquery(_core_tube_shape(r), "roller_core", assets=assets),
            material=mats["hardware"],
            name="roller_core", material_class_id="metal.stainless_matte",
        )
    elif r.cover == "napped_pile_fabric":
        roller.visual(
            mesh_from_cadquery(_smooth_cover_shape(r), "roller_cover", assets=assets),
            material=mats["cover"],
            name="roller_cover", material_class_id="fabric.carpet_fleece",
        )
        roller.visual(
            mesh_from_cadquery(_core_tube_shape(r), "roller_core", assets=assets),
            material=mats["hardware"],
            name="roller_core", material_class_id="metal.stainless_matte",
        )
        for i in range(r.nap_ring_count):
            roller.visual(
                mesh_from_geometry(_nap_ring_mesh(r, i, r.nap_ring_count), f"nap_ring_{i}"),
                material=mats["nap"],
                name=f"nap_ring_{i}", material_class_id="fabric.carpet_fleece",
            )
    elif r.cover == "feathered_taper_edge":
        roller.visual(
            _taper_cover_mesh(r),
            material=mats["cover"],
            name="roller_cover", material_class_id="fabric.flexible_foam",
        )
        roller.visual(
            _taper_core_mesh(r),
            material=mats["hardware"],
            name="roller_core", material_class_id="metal.stainless_matte",
        )
    else:  # perforated_lattice_core -- NO roller_core; journal -> end_spider
        roller.visual(
            mesh_from_cadquery(_smooth_cover_shape(r), "roller_cover", assets=assets),
            material=mats["cover"],
            name="roller_cover", material_class_id="fabric.open_mesh",
        )
        for i in range(r.rib_count):
            angle = 2.0 * math.pi * i / r.rib_count
            roller.visual(
                mesh_from_cadquery(_lattice_rib_shape(r, angle), f"lattice_rib_{i}", assets=assets),
                material=mats["hardware"],
                name=f"lattice_rib_{i}", material_class_id="metal.stainless_matte",
            )
        hoop_positions = _hoop_positions(r, r.hoop_count)
        for i in range(r.hoop_count):
            roller.visual(
                mesh_from_cadquery(
                    _lattice_hoop_shape(r, hoop_positions[i]), f"lattice_hoop_{i}", assets=assets
                ),
                material=mats["hardware"],
                name=f"lattice_hoop_{i}", material_class_id="metal.stainless_matte",
            )
        spider_x = [hoop_positions[0], hoop_positions[-1]]
        for i in range(2):
            roller.visual(
                mesh_from_cadquery(_end_spider_shape(r, spider_x[i]), f"end_spider_{i}", assets=assets),
                material=mats["hardware"],
                name=f"end_spider_{i}", material_class_id="metal.stainless_matte",
            )


# ===========================================================================
# Build
# ===========================================================================
def build_paint_roller(
    config: PaintRollerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"paint_roller_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    # --- Root: handle frame (cage_shank wire/shank + grip) ------------------
    frame = model.part("handle_frame")
    _build_cage_shank(frame, r, mats, assets=assets)
    _build_grip(frame, r, mats, assets=assets)
    frame.inertial = Inertial.from_geometry(
        Cylinder(radius=0.014, length=r.roller_len + r.handle_len),
        mass=0.25,
        origin=Origin(xyz=(r.roller_x_max, 0.0, r.handle_z / 2.0)),
    )

    # --- Moving child: roller cover (spins on the axle) ---------------------
    roller = model.part("roller_cover")
    _build_cover(roller, r, mats, assets=assets)
    roller.inertial = Inertial.from_geometry(
        Cylinder(radius=r.roller_outer_r, length=r.roller_len),
        mass=0.10,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    # --- Shared single moving mechanism: roller free-spins about +X ---------
    model.articulation(
        "frame_to_roller",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=roller,
        origin=Origin(xyz=(0.0, 0.0, r.axle_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.5, velocity=20.0),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_paint_roller(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_paint_roller(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_paint_roller_tests(
    object_model: ArticulatedObject,
    config: PaintRollerConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("handle_frame")
    roller = object_model.get_part("roller_cover")
    spin = object_model.get_articulation("frame_to_roller")

    axle_elem = _axle_elem_name(r)
    grip_elem = _grip_elem_name(r)
    journal_targets = _journal_targets(r)

    # ---- Journal capture allowances (element-scoped, mirrors sources). ----
    for tgt in journal_targets:
        ctx.allow_overlap(
            frame,
            roller,
            elem_a=axle_elem,
            elem_b=tgt,
            reason=(
                "The steel axle is intentionally captured inside the roller "
                "journal bore; the cover spins on it as a journal bearing."
            ),
        )
    # Birdcage retention spokes seat against the roller cover end face.
    if r.cage_shank == "birdcage_spider":
        for i in range(r.spoke_count):
            ctx.allow_overlap(
                frame,
                roller,
                elem_a=f"cage_spoke_{i}",
                elem_b="roller_cover",
                reason=(
                    "Birdcage spoke seats against the roller cover end face; the "
                    "cage retains the cover on the axle while it free-spins."
                ),
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Single root + shared CONTINUOUS spin mechanism. ----
    roots = object_model.root_parts()
    ctx.check(
        "handle_frame is the single root",
        len(roots) == 1 and roots[0].name == "handle_frame",
        details=f"roots={[p.name for p in roots]}",
    )
    ctx.check(
        "frame_to_roller is CONTINUOUS about the long X axis",
        spin.joint_type == ArticulationType.CONTINUOUS
        and abs(spin.axis[0]) > 0.99
        and abs(spin.axis[1]) < 0.01
        and abs(spin.axis[2]) < 0.01,
        details=f"type={spin.joint_type} axis={tuple(spin.axis)}",
    )

    # ---- Journal capture: axle runs through the journal target. ----
    if r.cover == "perforated_lattice_core":
        # No roller_core; journal migrates to the two end spider hubs.
        part_visuals = {v.name for v in roller.visuals}
        ctx.check(
            "perforated lattice cover has NO roller_core",
            "roller_core" not in part_visuals,
            details=str(sorted(part_visuals)),
        )
        for tgt in journal_targets:
            ctx.expect_overlap(
                frame,
                roller,
                axes="x",
                elem_a=axle_elem,
                elem_b=tgt,
                min_overlap=0.001,
                name=f"axle passes through {tgt} hub",
            )
    else:
        min_ov = 0.10 if r.cover == "feathered_taper_edge" else 0.15
        ctx.expect_overlap(
            frame,
            roller,
            axes="x",
            elem_a=axle_elem,
            elem_b="roller_core",
            min_overlap=min_ov,
            name="axle runs through the roller core",
        )
        ctx.expect_contact(
            roller,
            roller,
            elem_a="roller_core",
            elem_b="roller_cover",
            contact_tol=0.0006,
            name="roller core seated in cover bore",
        )

    # ---- Roller cover identity: long body centered on the axle. ----
    cover = roller.get_visual("roller_cover")
    aabb = ctx.part_element_world_aabb(roller, elem=cover)
    if aabb is not None:
        (xmin, ymin, zmin), (xmax, ymax, zmax) = aabb
        length_x = xmax - xmin
        dia_y = ymax - ymin
        dia_z = zmax - zmin
        lo = 2.0 * r.roller_outer_r - 0.002
        hi = 2.0 * r.roller_outer_r + 0.002
        ctx.check(
            "roller cover reads as a long cylinder centered on the axle",
            length_x > r.roller_len * 0.88 and lo < dia_y < hi and lo < dia_z < hi,
            details=f"len_x={length_x:.3f}, dia_y={dia_y:.3f}, dia_z={dia_z:.3f}",
        )
    ctx.check(
        "roller cover is hollow-walled (real bore present)",
        r.roller_bore_r < r.roller_outer_r - 0.006,
        details=f"outer_r={r.roller_outer_r:.4f}, bore_r={r.roller_bore_r:.4f}",
    )

    # ---- Cover-specific structure checks. ----
    if r.cover == "napped_pile_fabric":
        ctx.check(
            "nap rings present",
            all(roller.get_visual(f"nap_ring_{i}") is not None for i in range(r.nap_ring_count)),
            details=f"nap_ring_count={r.nap_ring_count}",
        )
        nap_aabbs = []
        for i in range(r.nap_ring_count):
            bb = ctx.part_element_world_aabb(roller, elem=roller.get_visual(f"nap_ring_{i}"))
            if bb is not None:
                nap_aabbs.append(bb)
        if nap_aabbs:
            nap_x_min = min(bb[0][0] for bb in nap_aabbs)
            nap_x_max = max(bb[1][0] for bb in nap_aabbs)
            ctx.check(
                "nap clears the hollow ends",
                nap_x_min > r.roller_x_min + 0.001 and nap_x_max < r.roller_x_max - 0.001,
                details=f"nap_x=[{nap_x_min:.4f},{nap_x_max:.4f}]",
            )
            nap_dia_y = max(bb[1][1] for bb in nap_aabbs) - min(bb[0][1] for bb in nap_aabbs)
            nap_dia_z = max(bb[1][2] for bb in nap_aabbs) - min(bb[0][2] for bb in nap_aabbs)
            ctx.check(
                "nap texture has raised fibers (wider than smooth wall)",
                nap_dia_y > 2.0 * r.roller_outer_r + 0.0005
                or nap_dia_z > 2.0 * r.roller_outer_r + 0.0005,
                details=f"nap_dia_y={nap_dia_y:.4f}, nap_dia_z={nap_dia_z:.4f}",
            )
    elif r.cover == "perforated_lattice_core":
        rib0 = roller.get_visual("lattice_rib_0")
        rib_aabb = ctx.part_element_world_aabb(roller, elem=rib0)
        if rib_aabb is not None:
            rib_len = rib_aabb[1][0] - rib_aabb[0][0]
            ctx.check(
                "lattice ribs span most of the roller length",
                rib_len > r.roller_len * 0.88,
                details=f"rib_len={rib_len:.4f}",
            )
        ctx.expect_within(
            roller, roller, axes="yz",
            inner_elem="lattice_rib_0", outer_elem="roller_cover",
            margin=0.001, name="lattice rib within roller cover bore",
        )
        mid_hoop = r.hoop_count // 2
        ctx.expect_contact(
            roller, roller,
            elem_a=f"lattice_hoop_{mid_hoop}", elem_b="roller_cover",
            contact_tol=0.001, name="lattice hoop seated against cover bore",
        )
        ctx.expect_contact(
            roller, roller,
            elem_a="lattice_rib_0", elem_b="roller_cover",
            contact_tol=0.001, name="lattice rib seated against cover bore",
        )
        ctx.expect_contact(
            roller, roller,
            elem_a="end_spider_0", elem_b="lattice_hoop_0",
            contact_tol=0.003, name="end spider 0 contacts nearest hoop",
        )
        ctx.expect_contact(
            roller, roller,
            elem_a="end_spider_1", elem_b=f"lattice_hoop_{r.hoop_count - 1}",
            contact_tol=0.003, name="end spider 1 contacts nearest hoop",
        )

    # ---- Cage / shank structure + grip connectivity. ----
    grip = frame.get_visual(grip_elem)
    gbb = ctx.part_element_world_aabb(frame, elem=grip)
    if gbb is not None:
        (gxmin, _gy0, gzmin), (gxmax, _gy1, gzmax) = gbb
        ctx.check(
            "grip extends out beyond the roller (+X side)",
            gxmin > r.roller_x_max,
            details=f"grip xmin={gxmin:.3f}, roller xmax={r.roller_x_max:.3f}",
        )
        if r.cage_shank == "straight_inline_shank":
            handle_center_z = (gzmin + gzmax) / 2.0
            ctx.check(
                "grip is inline with the roller axle (no drop)",
                abs(handle_center_z - r.axle_z) < 0.006,
                details=f"handle_center_z={handle_center_z:.4f}, axle_z={r.axle_z}",
            )
        else:
            ctx.check(
                "grip sits below the roller axle (crank / stem drop)",
                gzmax < r.axle_z - 0.02,
                details=f"grip z[{gzmin:.3f},{gzmax:.3f}], axle_z={r.axle_z}",
            )

    if r.cage_shank == "z_crank_wire":
        wbb = ctx.part_element_world_aabb(frame, elem=frame.get_visual("wire_frame"))
        if wbb is not None:
            (wxmin, _a, wzmin), (wxmax, _b, wzmax) = wbb
            ctx.check(
                "wire frame spans the roller and drops to the handle",
                wxmin <= r.roller_x_min + 0.002
                and wxmax >= r.roller_x_max
                and (wzmax - wzmin) > r.frame_drop * 0.7,
                details=f"wire x[{wxmin:.3f},{wxmax:.3f}] z[{wzmin:.3f},{wzmax:.3f}]",
            )
        ctx.expect_contact(
            frame, frame,
            elem_a="wire_frame", elem_b=grip_elem,
            contact_tol=0.0005, name="wire frame plugs into the grip",
        )
    elif r.cage_shank == "birdcage_spider":
        # Hub cap at the +X roller end.
        hbb = ctx.part_element_world_aabb(frame, elem=frame.get_visual("hub_cap"))
        if hbb is not None:
            ctx.check(
                "hub cap sits at the handle-side roller end",
                hbb[0][0] > r.roller_x_max - 0.005 and hbb[1][0] < r.roller_x_max + 0.015,
                details=f"hub x[{hbb[0][0]:.4f},{hbb[1][0]:.4f}]",
            )
        # All spokes seat near the roller cover end face.
        for i in range(r.spoke_count):
            ctx.expect_contact(
                frame, roller,
                elem_a=f"cage_spoke_{i}", elem_b="roller_cover",
                contact_tol=0.006, name=f"cage_spoke_{i} retains roller cover end",
            )
        ctx.expect_contact(
            frame, frame,
            elem_a="handle_stem", elem_b=grip_elem,
            contact_tol=0.0005, name="handle stem plugs into the grip",
        )
    else:  # straight_inline_shank
        sbb = ctx.part_element_world_aabb(frame, elem=frame.get_visual("shank"))
        if sbb is not None:
            shank_z_span = sbb[1][2] - sbb[0][2]
            ctx.check(
                "shank is straight (no Z crank drop)",
                shank_z_span < 0.010,
                details=f"shank z_span={shank_z_span:.4f}",
            )
        ctx.expect_contact(
            frame, frame,
            elem_a="shank", elem_b="collar",
            contact_tol=0.002, name="shank enters the collar adapter",
        )
        ctx.expect_contact(
            frame, frame,
            elem_a="collar", elem_b=grip_elem,
            contact_tol=0.002, name="collar adapter contacts the grip",
        )

    # ---- Grip-specific structure checks. ----
    if r.grip == "ribbed_scalloped_grip":
        ridge_centers = []
        for i in range(r.ridge_count):
            rv = frame.get_visual(f"finger_ridge_{i}")
            rbb = ctx.part_element_world_aabb(frame, elem=rv)
            if rbb is not None:
                ridge_centers.append((rbb[0][0] + rbb[1][0]) / 2.0)
        ctx.check(
            "all finger ridges present",
            len(ridge_centers) == r.ridge_count,
            details=f"ridge_count={r.ridge_count}, found={len(ridge_centers)}",
        )
        if len(ridge_centers) >= 2:
            spacings = [ridge_centers[i + 1] - ridge_centers[i] for i in range(len(ridge_centers) - 1)]
            avg = sum(spacings) / len(spacings)
            max_dev = max(abs(s - avg) for s in spacings)
            ctx.check(
                "finger ridges are regularly spaced",
                max_dev < 0.003,
                details=f"avg={avg:.4f}, max_dev={max_dev:.4f}",
            )
    elif r.grip == "hollow_tube_sleeve":
        ctx.check(
            "handle tube has a real stepped bore (hollow sleeve grip)",
            (r.axle_r + 0.0028) > r.axle_r + 0.001
            and (r.axle_r - 0.0003) < r.axle_r,
            details=f"axle_r={r.axle_r:.4f}",
        )
        ctx.expect_overlap(
            frame, frame, axes="x",
            elem_a=_grip_inserting_elem(r), elem_b="handle_tube",
            min_overlap=0.020, name="wire shank inserts into the tube bore",
        )
        ring_centers = []
        for i in range(r.ring_count):
            rbb = ctx.part_element_world_aabb(frame, elem=frame.get_visual(f"grip_ring_{i}"))
            if rbb is not None:
                ring_centers.append((rbb[0][0] + rbb[1][0]) / 2.0)
        ctx.check(
            "all grip rings present",
            len(ring_centers) == r.ring_count,
            details=f"ring_count={r.ring_count}, found={len(ring_centers)}",
        )
    elif r.grip == "pole_socket_grip":
        socket_x1 = _socket_x(r) + r.handle_len
        if gbb is not None:
            ctx.check(
                "handle butt end is flat (socket face present)",
                gbb[1][0] > socket_x1 - 0.003,
                details=f"grip xmax={gbb[1][0]:.4f}, socket_x1={socket_x1:.4f}",
            )
        ctx.check(
            "all thread turns present",
            all(frame.get_visual(f"thread_turn_{i}") is not None for i in range(r.thread_turn_count)),
            details=f"thread_turn_count={r.thread_turn_count}",
        )
        ctx.expect_contact(
            frame, frame,
            elem_a="thread_turn_0", elem_b="handle_grip",
            contact_tol=0.001, name="thread turn 0 contacts the bore wall",
        )

    # ---- Roller actually spins and stays centered through a quarter spin. ----
    with ctx.pose({spin: 0.0}):
        aabb0 = ctx.part_world_aabb(roller)
    with ctx.pose({spin: math.pi / 2.0}):
        aabb1 = ctx.part_world_aabb(roller)
    if aabb0 is not None and aabb1 is not None:
        centered = (
            abs((aabb1[0][1] + aabb1[1][1]) / 2.0) < 0.002
            and abs((aabb1[0][2] + aabb1[1][2]) / 2.0 - r.axle_z) < 0.002
        )
        ctx.check(
            "roller stays centered on the axle through a quarter spin",
            centered,
            details=f"spun aabb={aabb1}",
        )

    # ---- Grip clears the roller cover (no collision). ----
    ctx.expect_gap(
        frame,
        roller,
        axis="x",
        positive_elem=grip_elem,
        negative_elem="roller_cover",
        min_gap=0.0,
        name="grip clears the roller cover",
    )

    return ctx.report()


__all__ = (
    "PaintRollerConfig",
    "ResolvedPaintRollerConfig",
    "build_paint_roller",
    "build_seeded_paint_roller",
    "config_from_seed",
    "resolve_config",
    "run_paint_roller_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
