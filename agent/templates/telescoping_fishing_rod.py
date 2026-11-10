# SPDX-License-Identifier: Apache-2.0

"""Telescoping fishing rod — modular template.

A rear grounded ``handle`` (grip + reel seat[Slot B] + fixed outer blank tube +
reel body[Slot A]) carries a serial chain of concentric ``section_i`` telescoping
tubes (PRISMATIC +Z, ``stage_count`` of them) and a mounted reel whose spool /
crank / bail spin (REVOLUTE) off the handle.  Line guides[Slot C] ride the top of
the blank and every section.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/telescoping_fishing_rod.md`` and
the ``picture/0611/telescoping_fishing_rod`` 5-star pool (2 origins + 10 forks),
all synced under ``data/records/``.

Structure (pattern = ``mixed``).  Four discrete axes vary one layer each:

  * ``reel_type`` (3, ③ Primary Form Family): spinning_reel / baitcasting_reel /
    spincast_reel — the reel body form + rotary child set.
  * ``reel_seat`` (3, ②/④): fixed_hood_seat / sliding_ring_seat / screw_lock_seat
    — non-moving handle visuals on the reel-seat region.
  * ``guide_topology`` (3, ④/①): wire_ring_guides / bent_wire_guides /
    roller_tip_guides — non-moving guide hardware folded into each section.
  * ``stage_count`` (multiplicity, ①): N∈[3,8] telescoping section parts.

Tube shells are hollow open-bore ``LatheGeometry.from_shell_profiles`` (never
downgraded to Cylinder); guides are ``TorusGeometry`` / ``tube_from_spline_points``;
reel bodies are ``CapsuleGeometry`` / ``LatheGeometry`` / boxes.  Telescoping and
reel joints are captured geometry: they omit ``MatingContract`` (grandfathered) and
their concentric-nest / pivot-capture overlaps are declared element-scoped in
``run_telescoping_fishing_rod_tests`` (mirroring both source records' run_tests).
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
    CapsuleGeometry,
    Cylinder,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

ReelType = Literal["spinning_reel", "baitcasting_reel", "spincast_reel"]
ReelSeat = Literal["fixed_hood_seat", "sliding_ring_seat", "screw_lock_seat"]
GuideTopology = Literal["wire_ring_guides", "bent_wire_guides", "roller_tip_guides"]
PaletteStyle = Literal[
    "carbon_graphite",
    "black_gold",
    "spincast_red",
    "cobalt_blue",
    "olive_bronze",
    "ice_silver",
]

REEL_TYPES: tuple[ReelType, ...] = ("spinning_reel", "baitcasting_reel", "spincast_reel")
REEL_SEATS: tuple[ReelSeat, ...] = (
    "fixed_hood_seat",
    "sliding_ring_seat",
    "screw_lock_seat",
)
GUIDE_TOPOLOGIES: tuple[GuideTopology, ...] = (
    "wire_ring_guides",
    "bent_wire_guides",
    "roller_tip_guides",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "carbon_graphite",
    "black_gold",
    "spincast_red",
    "cobalt_blue",
    "olive_bronze",
    "ice_silver",
)

# stage_count multiplicity: number of telescoping section parts.  Product domain
# [3, 8]; weighted small (3-5 common, 6-8 rare).  N>=9 pushes the tip radius
# sub-mm and is excluded (see spec §8).
STAGE_COUNTS: tuple[int, ...] = (3, 4, 5, 6, 7, 8)
STAGE_WEIGHTS: tuple[float, ...] = (0.26, 0.26, 0.22, 0.13, 0.08, 0.05)

# Palette keys driving every ``.visual(material=)``:
#   blank      carbon composite tube shells
#   grip       EVA / foam grip + butt cap
#   dark_metal graphite reel body / collars / feet
#   metal      bright steel (spool lip, bail wire, tip, bright hardware)
#   accent     anodized / copper trim + guide rings + ferrules
#   line       line winding / spool line pack
# carbon_graphite == origin 001; black_gold == origin 002; spincast_red == fork.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "carbon_graphite": {
        "blank": (0.055, 0.062, 0.066, 1.0),
        "grip": (0.035, 0.035, 0.038, 1.0),
        "dark_metal": (0.105, 0.115, 0.125, 1.0),
        "metal": (0.80, 0.82, 0.82, 1.0),
        "accent": (0.69, 0.51, 0.20, 1.0),
        "line": (0.78, 0.54, 0.12, 1.0),
    },
    "black_gold": {
        "blank": (0.030, 0.040, 0.060, 1.0),
        "grip": (0.025, 0.028, 0.035, 1.0),
        "dark_metal": (0.080, 0.095, 0.120, 1.0),
        "metal": (0.72, 0.77, 0.83, 1.0),
        "accent": (0.96, 0.57, 0.055, 1.0),
        "line": (0.14, 0.15, 0.17, 1.0),
    },
    "spincast_red": {
        "blank": (0.050, 0.052, 0.055, 1.0),
        "grip": (0.045, 0.045, 0.048, 1.0),
        "dark_metal": (0.12, 0.13, 0.14, 1.0),
        "metal": (0.82, 0.83, 0.84, 1.0),
        "accent": (0.44, 0.06, 0.05, 1.0),
        "line": (0.62, 0.30, 0.10, 1.0),
    },
    "cobalt_blue": {
        "blank": (0.045, 0.055, 0.075, 1.0),
        "grip": (0.030, 0.032, 0.040, 1.0),
        "dark_metal": (0.10, 0.12, 0.16, 1.0),
        "metal": (0.74, 0.78, 0.82, 1.0),
        "accent": (0.10, 0.28, 0.62, 1.0),
        "line": (0.20, 0.32, 0.56, 1.0),
    },
    "olive_bronze": {
        "blank": (0.10, 0.11, 0.075, 1.0),
        "grip": (0.14, 0.15, 0.10, 1.0),
        "dark_metal": (0.12, 0.12, 0.09, 1.0),
        "metal": (0.72, 0.70, 0.58, 1.0),
        "accent": (0.55, 0.40, 0.16, 1.0),
        "line": (0.42, 0.34, 0.14, 1.0),
    },
    "ice_silver": {
        "blank": (0.34, 0.36, 0.40, 1.0),
        "grip": (0.16, 0.17, 0.19, 1.0),
        "dark_metal": (0.30, 0.32, 0.35, 1.0),
        "metal": (0.86, 0.88, 0.90, 1.0),
        "accent": (0.55, 0.66, 0.78, 1.0),
        "line": (0.70, 0.76, 0.82, 1.0),
    },
}

# Nominal (scale == 1) continuous ranges.
ROD_LEN_RANGE = (0.88, 1.15)
TAPER_SHRINK_RANGE = (0.76, 0.84)
TRAVEL_SCALE_RANGE = (0.85, 1.15)
REEL_SCALE_RANGE = (0.90, 1.12)

# Fixed layout constants (meters), rod axis = +Z.
_BLANK_R0 = 0.0110  # outer blank outer radius
_BORE_RATIO = 0.82  # tube inner radius = outer * ratio
_BLANK_FRONT = 0.60  # blank front z in handle frame
_BLANK_REAR = 0.24
_L1 = 0.32  # section_1 nominal length
_L_SHRINK = 0.94  # per-stage length shrink
_INSERT_FRAC = 0.60  # home nesting depth as a fraction of child length
_TRAVEL_FRAC = 0.42  # nominal extension travel as a fraction of child length
_Z_REEL = 0.055  # reel-seat / reel center z
_REEL_DROP = 0.100  # reel body offset below rod axis (-Y)

_RX = (math.pi / 2.0, 0.0, 0.0)  # rotate a z-cylinder onto +Y


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TelescopingFishingRodConfig:
    reel_type: ReelType | None = None
    reel_seat: ReelSeat | None = None
    guide_topology: GuideTopology | None = None
    stage_count: int | None = None
    palette_style: PaletteStyle = "carbon_graphite"
    rod_len_scale: float = 1.0
    taper_shrink: float = 0.80
    travel_scale: float = 1.0
    reel_scale: float = 1.0
    name: str = "telescoping_fishing_rod"


@dataclass(frozen=True)
class ResolvedTelescopingFishingRodConfig:
    reel_type: ReelType
    reel_seat: ReelSeat
    guide_topology: GuideTopology
    stage_count: int
    palette_style: PaletteStyle
    rl: float  # rod_len_scale
    ts: float  # taper_shrink
    tv: float  # travel_scale
    rs: float  # reel_scale
    # Derived per-section geometry (index 0..stage_count-1):
    seg_lengths: tuple[float, ...]
    seg_outer: tuple[float, ...]  # outer radius of each section
    seg_bore: tuple[float, ...]  # inner (bore) radius of each section
    seg_wall: tuple[float, ...]
    seg_home_z: tuple[float, ...]  # joint origin z (parent frame) at q=0
    seg_travel: tuple[float, ...]  # prismatic upper limit
    blank_bore: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


def config_from_seed(seed: int) -> TelescopingFishingRodConfig:
    rng = random.Random(seed)
    return TelescopingFishingRodConfig(
        reel_type=rng.choice(REEL_TYPES),
        reel_seat=rng.choice(REEL_SEATS),
        guide_topology=rng.choice(GUIDE_TOPOLOGIES),
        stage_count=rng.choices(STAGE_COUNTS, weights=STAGE_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        rod_len_scale=round(rng.uniform(*ROD_LEN_RANGE), 4),
        taper_shrink=round(rng.uniform(*TAPER_SHRINK_RANGE), 4),
        travel_scale=round(rng.uniform(*TRAVEL_SCALE_RANGE), 4),
        reel_scale=round(rng.uniform(*REEL_SCALE_RANGE), 4),
        name=f"seeded_telescoping_fishing_rod_{seed}",
    )


def resolve_config(
    config: TelescopingFishingRodConfig | None = None,
) -> ResolvedTelescopingFishingRodConfig:
    cfg = config or TelescopingFishingRodConfig()
    n = int(cfg.stage_count if cfg.stage_count is not None else 4)
    n = max(3, min(8, n))
    rl = _clamp(cfg.rod_len_scale, *ROD_LEN_RANGE)
    ts = _clamp(cfg.taper_shrink, *TAPER_SHRINK_RANGE)
    tv = _clamp(cfg.travel_scale, *TRAVEL_SCALE_RANGE)
    rs = _clamp(cfg.reel_scale, *REEL_SCALE_RANGE)

    blank_bore = _BLANK_R0 * _BORE_RATIO

    seg_lengths: list[float] = []
    seg_outer: list[float] = []
    seg_bore: list[float] = []
    seg_wall: list[float] = []
    seg_home_z: list[float] = []
    seg_travel: list[float] = []

    # equation: child outer = taper_shrink * parent outer; bore = outer*ratio.
    parent_outer = _BLANK_R0
    parent_front = _BLANK_FRONT  # z of the front of the current parent (handle frame for i=0)
    for i in range(n):
        outer = parent_outer * ts
        # tip radius floor so the innermost stage stays renderable / non-degenerate.
        outer = max(outer, 0.0016)
        bore = outer * _BORE_RATIO
        wall = max(outer - bore, 0.0005)
        length = _L1 * (_L_SHRINK ** i) * rl
        insert = _INSERT_FRAC * length
        # inequality: extension travel keeps retained insertion > 0.
        travel = _clamp(_TRAVEL_FRAC * length * tv, 0.05, insert - 0.10 * length)
        # Joint origin z in the PARENT frame: child rear (local z=0) sits ``insert``
        # behind the parent front, so at q=0 the child is nested by ``insert``.
        home_z = parent_front - insert
        seg_lengths.append(length)
        seg_outer.append(outer)
        seg_bore.append(bore)
        seg_wall.append(wall)
        seg_home_z.append(home_z)
        seg_travel.append(travel)
        # Next parent is this section; its front (local) is at z=length.
        parent_outer = outer
        parent_front = length

    return ResolvedTelescopingFishingRodConfig(
        reel_type=_pick(cfg.reel_type, REEL_TYPES),
        reel_seat=_pick(cfg.reel_seat, REEL_SEATS),
        guide_topology=_pick(cfg.guide_topology, GUIDE_TOPOLOGIES),
        stage_count=n,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        rl=rl,
        ts=ts,
        tv=tv,
        rs=rs,
        seg_lengths=tuple(seg_lengths),
        seg_outer=tuple(seg_outer),
        seg_bore=tuple(seg_bore),
        seg_wall=tuple(seg_wall),
        seg_home_z=tuple(seg_home_z),
        seg_travel=tuple(seg_travel),
        blank_bore=blank_bore,
        name=cfg.name or "telescoping_fishing_rod",
    )


def slot_choices_for_config(
    config: TelescopingFishingRodConfig | ResolvedTelescopingFishingRodConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedTelescopingFishingRodConfig)
        else resolve_config(config)
    )
    return (
        ("reel_type", r.reel_type),
        ("reel_seat", r.reel_seat),
        ("guide_topology", r.guide_topology),
        ("stage_count", str(r.stage_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Hero geometry helpers
# ---------------------------------------------------------------------------
def _tube_shell(z0: float, z1: float, outer0: float, outer1: float, wall: float, name: str):
    """A tapered, open-bore rod-blank tube with annular end faces. (origin 001
    L41-59) — LatheGeometry hero mesh, never downgraded."""
    return mesh_from_geometry(
        LatheGeometry.from_shell_profiles(
            [(outer0, z0), (outer1, z1)],
            [
                (max(outer0 - wall, 0.0006), z0),
                (max(outer1 - wall, 0.0006), z1),
            ],
            segments=36,
            start_cap="flat",
            end_cap="flat",
            lip_samples=3,
        ),
        name,
    )


def _add_guide(part, r, mats, *, index: int, z: float, blank_radius: float, is_tip: bool) -> None:
    """Line guide folded into the host tube as visuals (Rule 1, non-moving).  Its
    foot is derived from the host tube surface radius at ``z`` (Rule 4), so it hugs
    the blank across taper/scale.  Guides hang to -Y (origin 001 L62-99).  Every
    piece is authored to overlap the tube (embed) and its neighbour so the guide
    stays one connected support island."""
    topo = r.guide_topology
    br = blank_radius
    emb = 0.0018  # embed depth into the host tube surface
    ring_radius = max(0.007, br * 1.7)
    wire_radius = max(0.0013, ring_radius * 0.14)

    if topo == "roller_tip_guides" and is_tip:
        # Grooved roller sheave on a transverse axle + two support struts brazed
        # to the reinforced tip. (roller fork L62-160)
        wheel_r = ring_radius * 0.85
        cy = -(br + wheel_r)  # sheave center; struts bridge tube->sheave
        part.visual(
            Cylinder(radius=wheel_r * 0.72, length=0.0052),
            origin=Origin(xyz=(0.0, cy, z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["dark_metal"],
            name=f"guide_ring_{index}", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            mesh_from_geometry(
                TorusGeometry(radius=wheel_r * 0.60, tube=max(0.0014, wheel_r * 0.20),
                              radial_segments=10, tubular_segments=20),
                f"roller_groove_{index}",
            ),
            origin=Origin(xyz=(0.0, cy, z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["accent"],
            name=f"guide_groove_{index}", material_class_id=("metal.paint_coated" if r.palette_style in {"carbon_graphite", "black_gold", "spincast_red", "cobalt_blue", "ice_silver"} else "metal.bronze_cast"),
        )
        # Central support post on the tube axis (always within the tube footprint,
        # even for a sub-mm tip) spanning from inside the tube down to the sheave.
        post_top = -(br - emb)
        post_bot = cy  # sheave center
        part.visual(
            Box((0.006, post_top - post_bot, 0.008)),
            origin=Origin(xyz=(0.0, (post_top + post_bot) * 0.5, z)),
            material=mats["accent"],
            name=f"guide_yoke_{index}_a", material_class_id=("metal.paint_coated" if r.palette_style in {"carbon_graphite", "black_gold", "spincast_red", "cobalt_blue", "ice_silver"} else "metal.bronze_cast"),
        )
        return

    if topo == "bent_wire_guides":
        # One continuous bent guide wire eye whose legs are rooted inside the tube.
        # (origin 002 L74-96)
        center_y = -(br + ring_radius * 0.55)
        pts = [(0.0, -(br - emb), z)]
        for a_deg in (250, 215, 180, 145, 110, 75):
            a = math.radians(a_deg)
            pts.append((0.0, center_y + ring_radius * math.cos(a), z + ring_radius * math.sin(a)))
        pts.append((0.0, -(br - emb), z + 0.002))
        part.visual(
            mesh_from_geometry(
                tube_from_spline_points(pts, radius=wire_radius, samples_per_segment=5,
                                        radial_segments=10, cap_ends=True),
                f"bent_guide_wire_{index}",
            ),
            material=mats["metal"],
            name=f"guide_ring_{index}", material_class_id="metal.chrome_polished",
        )
        part.visual(
            Box((0.009, 0.012, 0.004)),
            origin=Origin(xyz=(0.0, -(br - emb) - 0.004, z)),
            material=mats["dark_metal"],
            name=f"guide_foot_{index}", material_class_id="metal.blackened_gunmetal",
        )
        return

    # wire_ring_guides (origin 001 L62-99): torus ring on a foot post.  The ring is
    # placed so its top embeds the tube, and a foot post bridges tube->ring center.
    y_ring = -(br + ring_radius + wire_radius - emb - 0.001)  # ring top embeds the tube
    post_top = -(br - emb)
    post_len = post_top - y_ring  # positive
    part.visual(
        mesh_from_geometry(
            TorusGeometry(radius=ring_radius, tube=wire_radius, radial_segments=12, tubular_segments=24),
            f"wire_ring_{index}",
        ),
        origin=Origin(xyz=(0.0, y_ring, z)),
        material=mats["accent"],
        name=f"guide_ring_{index}", material_class_id=("metal.paint_coated" if r.palette_style in {"carbon_graphite", "black_gold", "spincast_red", "cobalt_blue", "ice_silver"} else "metal.bronze_cast"),
    )
    part.visual(
        Box((0.006, post_len, 0.006)),
        origin=Origin(xyz=(0.0, post_top - post_len * 0.5, z)),
        material=mats["dark_metal"],
        name=f"guide_foot_{index}", material_class_id="metal.blackened_gunmetal",
    )


# ---------------------------------------------------------------------------
# Handle: grip + reel seat[Slot B] + outer blank + reel body[Slot A]
# ---------------------------------------------------------------------------
def _build_reel_seat(handle, r, mats) -> None:
    """Reel-seat hardware on the grip (z ~ _Z_REEL), non-moving handle visuals."""
    seat = r.reel_seat
    z = _Z_REEL
    if seat == "sliding_ring_seat":
        handle.visual(Cylinder(radius=0.0140, length=0.16), origin=Origin(xyz=(0.0, 0.0, z)),
                      material=mats["dark_metal"], name="reel_seat_core", material_class_id="metal.blackened_gunmetal")
        for zr, nm in ((z - 0.055, "rear"), (z + 0.055, "front")):
            handle.visual(Cylinder(radius=0.0168, length=0.020), origin=Origin(xyz=(0.0, 0.0, zr)),
                          material=mats["accent"], name=f"sliding_ring_{nm}", material_class_id=("metal.paint_coated" if r.palette_style in {"carbon_graphite", "black_gold", "spincast_red", "cobalt_blue", "ice_silver"} else "metal.bronze_cast"))
        handle.visual(Cylinder(radius=0.0174, length=0.005), origin=Origin(xyz=(0.0, 0.0, z + 0.066)),
                      material=mats["metal"], name="ring_trim", material_class_id="metal.chrome_polished")
    elif seat == "screw_lock_seat":
        handle.visual(Cylinder(radius=0.0150, length=0.16), origin=Origin(xyz=(0.0, 0.0, z)),
                      material=mats["dark_metal"], name="reel_seat_core", material_class_id="metal.blackened_gunmetal")
        handle.visual(Cylinder(radius=0.0180, length=0.026), origin=Origin(xyz=(0.0, 0.0, z - 0.050)),
                      material=mats["dark_metal"], name="fixed_hood", material_class_id="metal.blackened_gunmetal")
        handle.visual(Cylinder(radius=0.0178, length=0.030), origin=Origin(xyz=(0.0, 0.0, z + 0.048)),
                      material=mats["metal"], name="locking_nut", material_class_id="metal.chrome_polished")
        for k in range(5):
            handle.visual(Cylinder(radius=0.0162, length=0.004), origin=Origin(xyz=(0.0, 0.0, z + 0.006 + k * 0.008)),
                          material=mats["accent"], name=f"thread_crest_{k}", material_class_id=("metal.paint_coated" if r.palette_style in {"carbon_graphite", "black_gold", "spincast_red", "cobalt_blue", "ice_silver"} else "metal.bronze_cast"))
    else:  # fixed_hood_seat (origin default)
        handle.visual(Cylinder(radius=0.0150, length=0.17), origin=Origin(xyz=(0.0, 0.0, z)),
                      material=mats["metal"], name="reel_seat_core", material_class_id="metal.chrome_polished")
        handle.visual(Cylinder(radius=0.0182, length=0.028), origin=Origin(xyz=(0.0, 0.0, z - 0.052)),
                      material=mats["dark_metal"], name="rear_hood", material_class_id="metal.blackened_gunmetal")
        handle.visual(Cylinder(radius=0.0176, length=0.026), origin=Origin(xyz=(0.0, 0.0, z + 0.052)),
                      material=mats["accent"], name="front_hood", material_class_id=("metal.paint_coated" if r.palette_style in {"carbon_graphite", "black_gold", "spincast_red", "cobalt_blue", "ice_silver"} else "metal.bronze_cast"))


def _build_handle(model, r, mats):
    """Grounded root handle: butt cap, rear grip, reel seat, foregrip, fixed outer
    blank tube, blank guide, and the reel body[Slot A] as non-moving visuals."""
    handle = model.part("handle")
    # Grip + butt cap (foam).
    handle.visual(Cylinder(radius=0.0245, length=0.030), origin=Origin(xyz=(0.0, 0.0, -0.276)),
                  material=mats["grip"], name="butt_cap", material_class_id="fabric.flexible_foam")
    handle.visual(Cylinder(radius=0.0215, length=0.230), origin=Origin(xyz=(0.0, 0.0, -0.155)),
                  material=mats["grip"], name="rear_grip", material_class_id="fabric.flexible_foam")
    handle.visual(Cylinder(radius=0.0235, length=0.016), origin=Origin(xyz=(0.0, 0.0, -0.032)),
                  material=mats["accent"], name="rear_grip_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"carbon_graphite", "black_gold", "spincast_red", "cobalt_blue", "ice_silver"} else "metal.bronze_cast"))
    _build_reel_seat(handle, r, mats)
    handle.visual(Cylinder(radius=0.0200, length=0.100), origin=Origin(xyz=(0.0, 0.0, 0.180)),
                  material=mats["grip"], name="foregrip", material_class_id="fabric.flexible_foam")
    handle.visual(Cylinder(radius=0.0160, length=0.016), origin=Origin(xyz=(0.0, 0.0, 0.232)),
                  material=mats["accent"], name="lower_blank_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"carbon_graphite", "black_gold", "spincast_red", "cobalt_blue", "ice_silver"} else "metal.bronze_cast"))

    # Fixed outer blank tube (hero lathe shell), folded into the handle.
    handle.visual(
        _tube_shell(_BLANK_REAR, _BLANK_FRONT, _BLANK_R0, _BLANK_R0 * 0.97,
                    _BLANK_R0 - r.blank_bore, "outer_blank_shell"),
        material=mats["blank"], name="outer_blank", material_class_id="fabric.carbon_weave",
    )
    handle.visual(
        _tube_shell(_BLANK_FRONT - 0.016, _BLANK_FRONT, _BLANK_R0 * 1.06, _BLANK_R0 * 1.06, 0.0032,
                    "outer_socket_collar"),
        material=mats["dark_metal"], name="outer_socket_collar", material_class_id="metal.blackened_gunmetal",
    )
    _add_guide(handle, r, mats, index=0, z=_BLANK_FRONT - 0.05, blank_radius=_BLANK_R0, is_tip=False)

    _build_reel_body(handle, r, mats)
    return handle


def _build_reel_body(handle, r, mats) -> None:
    """Reel body (fixed load path) folded into the handle as non-moving visuals.
    Hangs at -Y below the reel seat.  Form varies per reel_type (Slot A, ③).
    Body center = (0, yb, z); crank mounts on a Y-offset plane below the body so
    its orbit clears; spool mounts on the +Z front face."""
    rs = r.rs
    z = _Z_REEL
    yb = -_REEL_DROP * rs  # reel body center y
    # Common foot + stem bridging reel seat underside to the body (support path,
    # all one handle part).
    handle.visual(Box((0.022 * rs, 0.030 * rs, 0.090 * rs)), origin=Origin(xyz=(0.0, -0.022 * rs, z)),
                  material=mats["dark_metal"], name="reel_foot", material_class_id="metal.blackened_gunmetal")
    handle.visual(Box((0.016 * rs, 0.070 * rs, 0.022 * rs)), origin=Origin(xyz=(0.0, yb + 0.030 * rs, z)),
                  material=mats["dark_metal"], name="reel_stem", material_class_id="metal.blackened_gunmetal")

    if r.reel_type == "baitcasting_reel":
        # Low-profile bridge frame with round side plates. (baitcasting fork L160-214)
        handle.visual(Box((0.055 * rs, 0.060 * rs, 0.024 * rs)), origin=Origin(xyz=(0.0, yb, z)),
                      material=mats["dark_metal"], name="reel_body", material_class_id="metal.blackened_gunmetal")
        for sx, lbl in ((-1.0, "a"), (1.0, "b")):
            handle.visual(Cylinder(radius=0.030 * rs, length=0.008 * rs),
                          origin=Origin(xyz=(sx * 0.028 * rs, yb, z), rpy=(0.0, math.pi / 2.0, 0.0)),
                          material=mats["metal"] if lbl == "a" else mats["dark_metal"], name=f"frame_side_{lbl}", material_class_id="metal.blackened_gunmetal")
        handle.visual(Box((0.056 * rs, 0.014 * rs, 0.008 * rs)), origin=Origin(xyz=(0.0, yb + 0.030 * rs, z + 0.006 * rs)),
                      material=mats["accent"], name="levelwind_rail", material_class_id=("metal.paint_coated" if r.palette_style in {"carbon_graphite", "black_gold", "spincast_red", "cobalt_blue", "ice_silver"} else "metal.bronze_cast"))
    elif r.reel_type == "spincast_reel":
        # Closed-face reel: a solid rounded body + a solid conical closed-face
        # cover on the +Z front (the spincast identity). (spincast fork L282-311)
        handle.visual(
            mesh_from_geometry(
                CapsuleGeometry(radius=0.038 * rs, length=0.026 * rs, radial_segments=20, height_segments=6),
                "spincast_body",
            ),
            origin=Origin(xyz=(0.0, yb, z - 0.010 * rs)),
            material=mats["dark_metal"], name="reel_body", material_class_id="metal.blackened_gunmetal",
        )
        handle.visual(
            mesh_from_geometry(
                LatheGeometry(
                    [(rr * rs, zz * rs) for rr, zz in
                     ((0.0, 0.0), (0.036, 0.004), (0.038, 0.020), (0.030, 0.036), (0.014, 0.048), (0.0, 0.052))],
                    segments=24,
                ),
                "spincast_cover",
            ),
            origin=Origin(xyz=(0.0, yb, z + 0.014 * rs)),
            material=mats["accent"], name="cover_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"carbon_graphite", "black_gold", "spincast_red", "cobalt_blue", "ice_silver"} else "metal.bronze_cast"),
        )
        handle.visual(Cylinder(radius=0.010 * rs, length=0.014 * rs),
                      origin=Origin(xyz=(0.0, yb, z + 0.060 * rs)),
                      material=mats["metal"], name="nose_aperture", material_class_id="metal.chrome_polished")
    else:  # spinning_reel (origin 001 L307-344)
        handle.visual(
            mesh_from_geometry(
                CapsuleGeometry(radius=0.032 * rs, length=0.050 * rs, radial_segments=22, height_segments=6),
                "reel_capsule",
            ),
            origin=Origin(xyz=(0.0, yb, z - 0.010 * rs)),
            material=mats["dark_metal"], name="reel_body", material_class_id="metal.blackened_gunmetal",
        )
        handle.visual(Cylinder(radius=0.026 * rs, length=0.030 * rs), origin=Origin(xyz=(0.0, yb, z + 0.048 * rs)),
                      material=mats["metal"], name="rotor_nose", material_class_id="metal.chrome_polished")


# ---------------------------------------------------------------------------
# Reel moving parts (parent = handle)
# ---------------------------------------------------------------------------
def _build_crank(model, r, mats, *, yb, z, body_half_x):
    """Side crank shared by all reel types.  Rotation axis +X, mounted just off
    the reel body's -X face: the shaft reaches +X into the body (captured drive),
    while the arm + knob orbit in the Y-Z plane a safe margin outside the -X face
    so the whole orbit clears the body."""
    rs = r.rs
    x_j = -(body_half_x + 0.008) * rs  # rotation center just off the -X face
    crank = model.part("crank")
    _RY = (0.0, math.pi / 2.0, 0.0)  # rotate a z-cylinder onto +X
    crank.visual(Cylinder(radius=0.006 * rs, length=0.034 * rs), origin=Origin(xyz=(0.004 * rs, 0.0, 0.0), rpy=_RY),
                 material=mats["metal"], name="crank_shaft", material_class_id="metal.chrome_polished")
    crank.visual(Box((0.008 * rs, 0.008 * rs, 0.048 * rs)), origin=Origin(xyz=(-0.010 * rs, 0.0, -0.024 * rs)),
                 material=mats["accent"], name="crank_arm", material_class_id=("metal.paint_coated" if r.palette_style in {"carbon_graphite", "black_gold", "spincast_red", "cobalt_blue", "ice_silver"} else "metal.bronze_cast"))
    crank.visual(Cylinder(radius=0.010 * rs, length=0.030 * rs), origin=Origin(xyz=(-0.010 * rs, 0.0, -0.048 * rs), rpy=_RY),
                 material=mats["grip"], name="crank_knob", material_class_id="fabric.flexible_foam")
    joint = (crank, "crank_turn", ArticulationType.REVOLUTE, (x_j, yb, z), (1.0, 0.0, 0.0),
             MotionLimits(lower=-math.pi, upper=math.pi, effort=4.0, velocity=9.0))
    return joint


def _build_reel_parts(model, r, mats):
    """Build spool + crank (+ bail for spinning/baitcasting).  Returns list of
    (part, joint_name, type, origin_xyz, axis, limits)."""
    rs = r.rs
    z = _Z_REEL
    yb = -_REEL_DROP * rs
    joints = []
    spool = model.part("spool")

    if r.reel_type == "baitcasting_reel":
        # Transverse spool between the frame side plates (axis +X).
        spool.visual(Cylinder(radius=0.005 * rs, length=0.052 * rs),
                     origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                     material=mats["metal"], name="spool_axle", material_class_id="metal.chrome_polished")
        spool.visual(Cylinder(radius=0.018 * rs, length=0.038 * rs),
                     origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                     material=mats["line"], name="line_pack", material_class_id="fabric.thread_yarn")
        for sx in (-1.0, 1.0):
            spool.visual(Cylinder(radius=0.023 * rs, length=0.004 * rs),
                         origin=Origin(xyz=(sx * 0.021 * rs, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                         material=mats["dark_metal"], name=f"spool_flange_{'a' if sx < 0 else 'b'}", material_class_id="metal.blackened_gunmetal")
        joints.append((spool, "spool_spin", ArticulationType.REVOLUTE, (0.0, yb, z), (1.0, 0.0, 0.0),
                       MotionLimits(lower=-math.pi, upper=math.pi, effort=2.0, velocity=10.0)))
        joints.append(_build_crank(model, r, mats, yb=yb, z=z, body_half_x=0.034))
        # Thumb bar (bail-equivalent) hinging on +Y across the frame top.
        bail = model.part("bail")
        bail.visual(Box((0.048 * rs, 0.006 * rs, 0.008 * rs)), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                    material=mats["grip"], name="thumb_bar", material_class_id="fabric.flexible_foam")
        joints.append((bail, "bail_flip", ArticulationType.REVOLUTE, (0.0, yb + 0.030 * rs, z - 0.014 * rs),
                       (0.0, 1.0, 0.0), MotionLimits(lower=-0.22, upper=0.20, effort=1.0, velocity=4.0)))
        return joints

    if r.reel_type == "spincast_reel":
        # Enclosed spool (axis +Z) inside the dome; no bail (closed face).
        spool.visual(Cylinder(radius=0.026 * rs, length=0.030 * rs), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                     material=mats["line"], name="line_pack", material_class_id="fabric.thread_yarn")
        spool.visual(Cylinder(radius=0.030 * rs, length=0.008 * rs), origin=Origin(xyz=(0.0, 0.0, 0.012 * rs)),
                     material=mats["dark_metal"], name="spool_flange", material_class_id="metal.blackened_gunmetal")
        joints.append((spool, "spool_spin", ArticulationType.REVOLUTE, (0.0, yb, z - 0.010 * rs), (0.0, 0.0, 1.0),
                       MotionLimits(lower=-math.pi, upper=math.pi, effort=2.0, velocity=10.0)))
        joints.append(_build_crank(model, r, mats, yb=yb, z=z, body_half_x=0.040))
        return joints

    # spinning_reel (origin 001 L346-433): spool on the +Z front face, bail over it.
    spool.visual(Cylinder(radius=0.028 * rs, length=0.024 * rs), origin=Origin(xyz=(0.0, 0.0, 0.006 * rs)),
                 material=mats["dark_metal"], name="spool_skirt", material_class_id="metal.blackened_gunmetal")
    spool.visual(Cylinder(radius=0.024 * rs, length=0.018 * rs), origin=Origin(xyz=(0.0, 0.0, 0.022 * rs)),
                 material=mats["line"], name="line_winding", material_class_id="fabric.thread_yarn")
    spool.visual(Cylinder(radius=0.029 * rs, length=0.005 * rs), origin=Origin(xyz=(0.0, 0.0, 0.033 * rs)),
                 material=mats["metal"], name="spool_lip", material_class_id="metal.chrome_polished")
    spool.visual(Cylinder(radius=0.012 * rs, length=0.012 * rs), origin=Origin(xyz=(0.0, 0.0, 0.037 * rs)),
                 material=mats["dark_metal"], name="drag_cap", material_class_id="metal.blackened_gunmetal")
    joints.append((spool, "spool_spin", ArticulationType.REVOLUTE, (0.0, yb, z + 0.056 * rs), (0.0, 0.0, 1.0),
                   MotionLimits(lower=-math.pi, upper=math.pi, effort=2.5, velocity=18.0)))
    joints.append(_build_crank(model, r, mats, yb=yb, z=z, body_half_x=0.034))
    bail = model.part("bail")
    bail.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [(-0.030 * rs, 0.0, 0.0), (-0.028 * rs, 0.0, 0.024 * rs),
                 (0.0, 0.0, 0.038 * rs), (0.028 * rs, 0.0, 0.024 * rs),
                 (0.030 * rs, 0.0, 0.0)],
                radius=0.0022 * rs, samples_per_segment=10, radial_segments=10, cap_ends=True,
            ),
            "bail_wire",
        ),
        material=mats["metal"], name="bail_wire", material_class_id="metal.chrome_polished",
    )
    joints.append((bail, "bail_flip", ArticulationType.REVOLUTE, (0.0, yb, z + 0.052 * rs), (1.0, 0.0, 0.0),
                   MotionLimits(lower=-0.18, upper=1.45, effort=1.2, velocity=5.0)))
    return joints


# ---------------------------------------------------------------------------
# Telescoping sections
# ---------------------------------------------------------------------------
def _build_section(model, r, mats, *, index: int):
    """One telescoping section part built in its own local frame (rear at z=0)."""
    length = r.seg_lengths[index]
    outer = r.seg_outer[index]
    wall = r.seg_wall[index]
    is_tip = index == r.stage_count - 1
    section = model.part(f"section_{index + 1}")
    outer1 = outer * 0.94
    section.visual(
        _tube_shell(0.0, length, outer, outer1, wall, f"section_shell_{index + 1}"),
        material=mats["blank"], name="section_shell", material_class_id="fabric.carbon_weave",
    )
    # Front trim ferrule (accent).
    section.visual(
        _tube_shell(length - 0.014, length, outer1 * 1.10, outer1 * 1.10, max(outer1 * 0.4, 0.0006),
                    f"section_ferrule_{index + 1}"),
        material=mats["accent"] if index % 2 == 0 else mats["metal"], name="front_ferrule", material_class_id=("metal.paint_coated" if r.palette_style in {"carbon_graphite", "black_gold", "spincast_red", "cobalt_blue", "ice_silver"} else "metal.bronze_cast"),
    )
    # Rear guide bushing that rides (and lightly overlaps) the parent bore so the
    # nested stage always keeps a real support contact with its parent, at every
    # taper.  The overlap is a declared captured allowance (concentric sleeve).
    parent_bore = r.blank_bore if index == 0 else r.seg_bore[index - 1]
    section.visual(
        Cylinder(radius=parent_bore + 0.0004, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.007)),
        material=mats["dark_metal"], name="rear_bushing", material_class_id="metal.blackened_gunmetal",
    )
    # Guide near the front of this section (staggered along z when collapsed).
    _add_guide(section, r, mats, index=index + 1, z=length - 0.03, blank_radius=outer1, is_tip=is_tip)
    if is_tip:
        section.visual(Cylinder(radius=max(outer1 * 0.9, 0.0016), length=0.010),
                       origin=Origin(xyz=(0.0, 0.0, length + 0.004)),
                       material=mats["metal"], name="tip_end_cap", material_class_id="metal.chrome_polished")
    return section


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_telescoping_fishing_rod(
    config: TelescopingFishingRodConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"tfr_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    handle = _build_handle(model, r, mats)

    # Telescoping prismatic chain.
    parent = handle
    sections = []
    for i in range(r.stage_count):
        section = _build_section(model, r, mats, index=i)
        model.articulation(
            f"stage_{i + 1}",
            ArticulationType.PRISMATIC,
            parent=parent,
            child=section,
            origin=Origin(xyz=(0.0, 0.0, r.seg_home_z[i])),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(lower=0.0, upper=r.seg_travel[i], effort=40.0 - 3.0 * i, velocity=0.30),
            meta={"mechanism": "telescoping_section"},
        )
        sections.append(section)
        parent = section

    # Reel rotary children (parallel off the handle).
    for part, jname, jtype, jxyz, jaxis, jlim in _build_reel_parts(model, r, mats):
        model.articulation(jname, jtype, parent=handle, child=part, origin=Origin(xyz=jxyz), axis=jaxis,
                           motion_limits=jlim, meta={"mechanism": "reel"})

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_telescoping_fishing_rod(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_telescoping_fishing_rod(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _declare_captured_overlaps(ctx, model, r) -> None:
    """Concentric telescoping tubes + reel pivots are captured geometry — declare
    their intentional overlaps element-scoped (mirroring both origins' run_tests)."""
    handle = model.get_part("handle")
    # Concentric telescoping tubes all nest/slide within one another (and inside
    # the handle's outer blank) — a captured sleeve stack.  Declare every mutual
    # pair (handle + all sections) intended-overlap.
    tube_parts = [handle] + [model.get_part(f"section_{i + 1}") for i in range(r.stage_count)]
    for a in range(len(tube_parts)):
        for b in range(a + 1, len(tube_parts)):
            ctx.allow_overlap(tube_parts[a], tube_parts[b],
                              reason="Concentric telescoping tubes nest/slide within one another (captured sleeve stack).")

    # Reel captures: spool/crank/bail run inside/against the reel body region.
    spool = model.get_part("spool")
    crank = model.get_part("crank")
    ctx.allow_overlap(spool, handle,
                      reason="The spool is captured/centered inside the reel rotor body.")
    # crank drive shaft is captured in the reel body (+ side plates for
    # baitcasting) and couples to the spool axle; arm/knob are geometrically clear.
    body_elems = ["reel_body"]
    if r.reel_type == "baitcasting_reel":
        body_elems += ["frame_side_a", "frame_side_b"]
    for be in body_elems:
        ctx.allow_overlap(crank, handle, elem_a="crank_shaft", elem_b=be,
                          reason="The crank drive shaft is captured inside the reel body for support.")
    ctx.allow_overlap(crank, spool,
                      reason="The crank drive shaft couples to the spool axle inside the reel.")
    if r.reel_type in ("spinning_reel", "baitcasting_reel"):
        bail = model.get_part("bail")
        ctx.allow_overlap(bail, handle,
                          reason="The bail/thumb bar is captured on the rotor pivot region.")
        ctx.allow_overlap(bail, spool,
                          reason="The bail wire arcs over the spool front in the rest pose.")


def run_telescoping_fishing_rod_tests(
    object_model: ArticulatedObject,
    config: TelescopingFishingRodConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    _declare_captured_overlaps(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    expected = {"handle", "spool", "crank"} | {f"section_{i + 1}" for i in range(r.stage_count)}
    ctx.check("handle + telescoping sections + reel present", expected <= part_names,
              details=str(sorted(part_names)))
    ctx.check("at least 3 telescoping stages", r.stage_count >= 3, details=f"stage_count={r.stage_count}")

    roots = object_model.root_parts()
    ctx.check("single grounded root handle", len(roots) == 1 and roots[0].name == "handle",
              details=f"roots={[p.name for p in roots]}")

    # ---- Joint topology: each stage is a constrained prismatic +Z. ----
    for i in range(r.stage_count):
        j = object_model.get_articulation(f"stage_{i + 1}")
        ok = (
            j.articulation_type == ArticulationType.PRISMATIC
            and abs(j.axis[2]) > 0.99
            and j.motion_limits is not None
            and j.motion_limits.lower == 0.0
            and j.motion_limits.upper > 0.02
        )
        ctx.check(f"stage_{i + 1} is a constrained prismatic +Z", ok,
                  details=f"type={j.articulation_type} axis={tuple(j.axis)} lim={j.motion_limits}")

    spool_j = object_model.get_articulation("spool_spin")
    crank_j = object_model.get_articulation("crank_turn")
    ctx.check("spool + crank are revolute", spool_j.articulation_type == ArticulationType.REVOLUTE
              and crank_j.articulation_type == ArticulationType.REVOLUTE)
    has_bail = any(a.name == "bail_flip" for a in object_model.articulations)
    ctx.check("bail present iff not spincast", has_bail == (r.reel_type != "spincast_reel"),
              details=f"reel={r.reel_type} has_bail={has_bail}")

    # ---- Rule 5: telescoping extends and stays inserted; reel parts move. ----
    tip = object_model.get_part(f"section_{r.stage_count}")
    rest_tip = ctx.part_world_position(tip)
    extend_pose = {
        object_model.get_articulation(f"stage_{i + 1}"): object_model.get_articulation(
            f"stage_{i + 1}"
        ).motion_limits.upper
        for i in range(r.stage_count)
    }
    with ctx.pose(extend_pose):
        ext_tip = ctx.part_world_position(tip)
    if rest_tip is not None and ext_tip is not None:
        ctx.check("telescoping extension lengthens the rod toward +Z",
                  ext_tip[2] > rest_tip[2] + 0.05,
                  details=f"rest={rest_tip} extended={ext_tip}")

    # Spool is rotationally symmetric (aabb invariant under spin) — just verify
    # the joint poses cleanly.
    spool = object_model.get_part("spool")
    with ctx.pose({spool_j: math.pi / 2.0}):
        ctx.check("spool spins without error", ctx.part_world_aabb(spool) is not None)

    # Crank knob is off-axis, so the crank_knob element aabb must move.
    crank = object_model.get_part("crank")
    knob0 = ctx.part_element_world_aabb(crank, elem="crank_knob")
    with ctx.pose({crank_j: math.pi / 2.0}):
        knob1 = ctx.part_element_world_aabb(crank, elem="crank_knob")
    if knob0 is not None and knob1 is not None:
        moved = max(math.dist(knob0[i], knob1[i]) for i in (0, 1))
        ctx.check("crank knob orbits", moved > 0.005 * r.rs, details=f"knob corner moved {moved:.5f}")

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    ctx.check("slot_choices recorded",
              tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
              details=str(object_model.meta.get("slot_choices")))

    return ctx.report()


__all__ = (
    "TelescopingFishingRodConfig",
    "ResolvedTelescopingFishingRodConfig",
    "build_telescoping_fishing_rod",
    "build_seeded_telescoping_fishing_rod",
    "config_from_seed",
    "resolve_config",
    "run_telescoping_fishing_rod_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
