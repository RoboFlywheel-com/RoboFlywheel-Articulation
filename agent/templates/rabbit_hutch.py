# SPDX-License-Identifier: Apache-2.0

"""Pet_Animal related / Rabbit hutch procedural template (modular).

Spec: articraft_template_authoring/specs_modular_v1/rabbit_hutch.md

A raised outdoor rabbit hutch: an enclosed sheltered compartment with wire-mesh
ventilated fronts, opening human-access doors, a slide-out cleaning tray, raised
on legs or rolling casters. Structural spine is the parallel-children
``hutch_frame`` root part carrying every fixed ``.visual(...)``; every access
member (doors, roof lid, drop ramp, tray, casters, latch hasps, guillotine
pop-hole) is a moving child parented to it.

Slots (pattern = mixed, parallel_children + multiplicity):
  * Slot A body_form (③/①): wheeled_hutch_run / grid_cabinet / aframe_ark
  * Slot B mobility (①/②): swivel_casters / fixed_legs
  * Slot C front_access (②): drop_ramp / guillotine_pop_hole (gated off grid)
  * Multiplicity n_tiers (grid_cabinet): N in {1,2,3}

Rules:
  Rule 1 — non-articulating detail (plank seams, wood grain, face screws, hinge
    leaves, latch plates, wire mesh, roof caps, ramp cleats, pop trim) is a host
    ``.visual(...)``; NO FIXED-jointed decoration parts. No FIXED articulation.
  Rule 2 — every moving child is a captured hinge/pin/rail; ``MatingContract``
    cannot express it, so joints are grandfathered (omit ``mating=``) and kept
    honest with element-scoped ``allow_overlap`` + ``expect_contact``.
  Rule 3 — structure derives from the declared 5-star sources (A/B/aframe/slide).
  Rule 5 — ``fail_if_parts_overlap_in_sampled_poses`` + one targeted ``ctx.pose``
    per mechanism family.
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

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
BodyForm = Literal["wheeled_hutch_run", "grid_cabinet", "aframe_ark"]
Mobility = Literal["swivel_casters", "fixed_legs"]
FrontAccess = Literal["drop_ramp", "guillotine_pop_hole"]
Palette = Literal["white_grey", "natural_pine", "warm_timber", "slate_grey"]

BODY_FORMS: tuple[BodyForm, ...] = ("wheeled_hutch_run", "grid_cabinet", "aframe_ark")
MOBILITIES: tuple[Mobility, ...] = ("swivel_casters", "fixed_legs")
PALETTES_ORDER: tuple[Palette, ...] = ("white_grey", "natural_pine", "warm_timber", "slate_grey")

# Which front-access members each body form may host (compatibility matrix — §9).
ALLOWED_ACCESS: dict[BodyForm, tuple[FrontAccess, ...]] = {
    "wheeled_hutch_run": ("drop_ramp", "guillotine_pop_hole"),
    # Enclosed grid has no compartment↔run divider, so its rabbit-exit pop-hole
    # goes in the side wall (a front drop ramp would foul the slide-out tray).
    "grid_cabinet": ("guillotine_pop_hole",),
    "aframe_ark": ("drop_ramp", "guillotine_pop_hole"),
}

# 4 colorways. Keys: wood / trim / mesh / black / tray / clear / ramp.
PALETTES: dict[Palette, dict[str, tuple[float, float, float, float]]] = {
    "white_grey": {
        "wood": (0.86, 0.84, 0.78, 1.0), "trim": (0.55, 0.56, 0.54, 1.0),
        "mesh": (0.10, 0.11, 0.10, 1.0), "black": (0.02, 0.02, 0.018, 1.0),
        "tray": (0.035, 0.035, 0.032, 1.0), "clear": (0.62, 0.72, 0.78, 0.38),
        "ramp": (0.72, 0.67, 0.58, 1.0),
    },
    "natural_pine": {
        "wood": (0.72, 0.43, 0.18, 1.0), "trim": (0.42, 0.24, 0.11, 1.0),
        "mesh": (0.06, 0.055, 0.05, 1.0), "black": (0.01, 0.01, 0.008, 1.0),
        "tray": (0.54, 0.56, 0.53, 1.0), "clear": (0.60, 0.70, 0.75, 0.38),
        "ramp": (0.60, 0.45, 0.25, 1.0),
    },
    "warm_timber": {
        "wood": (0.62, 0.45, 0.28, 1.0), "trim": (0.42, 0.30, 0.18, 1.0),
        "mesh": (0.10, 0.11, 0.10, 1.0), "black": (0.02, 0.02, 0.018, 1.0),
        "tray": (0.035, 0.035, 0.032, 1.0), "clear": (0.62, 0.72, 0.78, 0.38),
        "ramp": (0.72, 0.67, 0.58, 1.0),
    },
    "slate_grey": {
        "wood": (0.60, 0.62, 0.64, 1.0), "trim": (0.32, 0.34, 0.36, 1.0),
        "mesh": (0.08, 0.08, 0.09, 1.0), "black": (0.02, 0.02, 0.02, 1.0),
        "tray": (0.40, 0.42, 0.44, 1.0), "clear": (0.60, 0.70, 0.78, 0.38),
        "ramp": (0.65, 0.66, 0.60, 1.0),
    },
}

CASTER_CLEARANCE = 0.11  # frame leg bottom height when rolling on casters


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class RabbitHutchConfig:
    body_form: BodyForm | None = None
    mobility: Mobility | None = None
    front_access: FrontAccess | None = None
    n_tiers: int = 3
    palette: Palette = "white_grey"
    door_swing: float = 1.35
    tray_travel: float = 0.32
    roof_overhang_scale: float = 1.0
    name: str = "rabbit_hutch"


@dataclass(frozen=True)
class ResolvedRabbitHutchConfig:
    body_form: BodyForm
    mobility: Mobility
    front_access: FrontAccess
    n_tiers: int
    palette: Palette
    door_swing: float
    tray_travel: float
    roof_overhang_scale: float
    name: str

    @property
    def leg_bottom_z(self) -> float:
        return CASTER_CLEARANCE if self.mobility == "swivel_casters" else 0.0


def config_from_seed(seed: int) -> RabbitHutchConfig:
    """Deterministic procedural sampling over the full slot domain (seed 0 is
    not special). front_access is drawn from the chosen form's allowed set; the
    n_tiers multiplicity is gated to the grid cabinet."""
    rng = random.Random(seed)
    mobility = rng.choice(MOBILITIES)
    form = rng.choice(BODY_FORMS)
    access = rng.choice(ALLOWED_ACCESS[form])
    # Weighted tier count: tall 3-tier grid is the canonical B image.
    n_tiers = rng.choices((1, 2, 3), weights=(1, 2, 3))[0]
    return RabbitHutchConfig(
        body_form=form,
        mobility=mobility,
        front_access=access,
        n_tiers=n_tiers,
        palette=rng.choice(PALETTES_ORDER),
        door_swing=round(rng.uniform(1.20, 1.50), 4),
        tray_travel=round(rng.uniform(0.28, 0.34), 4),
        roof_overhang_scale=round(rng.uniform(0.90, 1.15), 4),
        name=f"seeded_rabbit_hutch_{seed}",
    )


def resolve_config(config: RabbitHutchConfig | None = None) -> ResolvedRabbitHutchConfig:
    cfg = config or RabbitHutchConfig()
    form = _pick(cfg.body_form, BODY_FORMS)
    mobility = _pick(cfg.mobility, MOBILITIES)
    allowed = ALLOWED_ACCESS[form]
    access = cfg.front_access if cfg.front_access in allowed else allowed[0]
    n_tiers = int(cfg.n_tiers) if cfg.n_tiers in (1, 2, 3) else 1
    if form != "grid_cabinet":
        n_tiers = 1
    return ResolvedRabbitHutchConfig(
        body_form=form,
        mobility=mobility,
        front_access=access,
        n_tiers=n_tiers,
        palette=_pick(cfg.palette, PALETTES_ORDER),
        door_swing=_clamp(cfg.door_swing, 1.20, 1.50),
        tray_travel=_clamp(cfg.tray_travel, 0.28, 0.34),
        roof_overhang_scale=_clamp(cfg.roof_overhang_scale, 0.90, 1.15),
        name=cfg.name or "rabbit_hutch",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedRabbitHutchConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("mobility", r.mobility),
        ("front_access", r.front_access),
        ("n_tiers", f"n{r.n_tiers}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Geometry helpers
# ===========================================================================
def _box(part, name, size, xyz, material, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.softwood_pine")


def _cyl(part, name, radius, length, xyz, material, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.blackened_gunmetal",
    )


def _front_mesh(part, prefix, x0, x1, z0, z1, y, mesh, *, wire=0.006, depth=0.010) -> None:
    """Square wire grid in an XZ panel at fixed Y (Origin A helper)."""
    width = x1 - x0
    height = z1 - z0
    cols = max(3, int(width / 0.095))
    rows = max(3, int(height / 0.085))
    for i in range(cols + 1):
        x = x0 + width * i / cols
        _box(part, f"{prefix}_v_{i}", (wire, depth, height + wire), (x, y, (z0 + z1) / 2), mesh)
    for j in range(rows + 1):
        z = z0 + height * j / rows
        _box(part, f"{prefix}_h_{j}", (width + wire, depth, wire), ((x0 + x1) / 2, y, z), mesh)


def _side_mesh(part, prefix, y0, y1, z0, z1, x, mesh, *, wire=0.006, depth=0.010) -> None:
    """Square wire grid in a YZ panel at fixed X (Origin A helper)."""
    panel_depth = y1 - y0
    height = z1 - z0
    cols = max(3, int(panel_depth / 0.095))
    rows = max(3, int(height / 0.085))
    for i in range(cols + 1):
        y = y0 + panel_depth * i / cols
        _box(part, f"{prefix}_v_{i}", (depth, wire, height + wire), (x, y, (z0 + z1) / 2), mesh)
    for j in range(rows + 1):
        z = z0 + height * j / rows
        _box(part, f"{prefix}_h_{j}", (depth, panel_depth + wire, wire), (x, (y0 + y1) / 2, z), mesh)


# ---------------------------------------------------------------------------
# Origin-A style panel door (hinge line at local X=0, door extends -X, vertical Z)
# ---------------------------------------------------------------------------
def _panel_door(part, prefix, width, height, mats, *, mesh=False, acrylic=False) -> None:
    stile = 0.038
    thick = 0.030
    wood, trim, mesh_m, black, clear = (
        mats["wood"], mats["trim"], mats["mesh"], mats["black"], mats["clear"],
    )
    _box(part, f"{prefix}_hinge_stile", (stile, thick, height), (-stile / 2, 0.0, 0.0), wood)
    _box(part, f"{prefix}_free_stile", (stile, thick, height), (-width + stile / 2, 0.0, 0.0), wood)
    _box(part, f"{prefix}_top_rail", (width, thick, stile), (-width / 2, 0.0, height / 2 - stile / 2), wood)
    _box(part, f"{prefix}_bottom_rail", (width, thick, stile), (-width / 2, 0.0, -height / 2 + stile / 2), wood)
    _box(part, f"{prefix}_inner_lip", (width - 0.075, 0.010, height - 0.075), (-width / 2, -0.003, 0.0), trim)
    if acrylic:
        _box(part, f"{prefix}_clear_window", (width - 0.092, 0.006, height - 0.100), (-width / 2, -0.006, 0.0), clear)
    if mesh:
        _front_mesh(part, f"{prefix}_mesh", -width + 0.052, -0.052, -height / 2 + 0.052,
                    height / 2 - 0.052, -0.008, mesh_m, wire=0.0045, depth=0.006)
    # Hinge knuckles + latch plate carried by the door (decoration, Rule 1).
    _cyl(part, f"{prefix}_hinge_pin_upper", 0.010, 0.085, (0.0, -0.002, height * 0.25), black)
    _cyl(part, f"{prefix}_hinge_pin_lower", 0.010, 0.085, (0.0, -0.002, -height * 0.25), black)
    _box(part, f"{prefix}_hinge_leaf_upper", (0.050, 0.008, 0.055), (-0.028, -0.017, height * 0.25), black)
    _box(part, f"{prefix}_hinge_leaf_lower", (0.050, 0.008, 0.055), (-0.028, -0.017, -height * 0.25), black)
    _box(part, f"{prefix}_latch_plate", (0.042, 0.014, 0.026), (-width + 0.032, -0.022, 0.0), black)
    _cyl(part, f"{prefix}_latch_knob", 0.010, 0.016, (-width + 0.010, -0.035, 0.0), black, rpy=(math.pi / 2, 0.0, 0.0))


# ---------------------------------------------------------------------------
# Origin-B style grid doors + latch hasp
# ---------------------------------------------------------------------------
def _add_wood_grain(part, prefix, width, height, y, material) -> None:
    for i, z in enumerate((height * 0.30, height * 0.45, height * 0.60, height * 0.75)):
        _box(part, f"{prefix}_plank_seam_{i}", (width * 0.74, 0.003, 0.004), (width * 0.50, y, z), material)
    for i, (xf, zf, lf) in enumerate(((0.25, 0.37, 0.20), (0.52, 0.51, 0.16), (0.38, 0.69, 0.12), (0.68, 0.82, 0.18))):
        _box(part, f"{prefix}_fine_grain_{i}", (width * lf, 0.0025, 0.003), (width * xf, y - 0.001, height * zf), material)


def _add_face_screws(part, prefix, width, height, y, material) -> None:
    for i, (x, z) in enumerate(((0.075, 0.075), (width - 0.075, 0.075), (0.075, height - 0.075), (width - 0.075, height - 0.075))):
        _cyl(part, f"{prefix}_screw_{i}", 0.006, 0.004, (x, y, z), material, rpy=(math.pi / 2, 0.0, 0.0))


def _add_hinge_knuckles(part, height, metal) -> None:
    for i, z in enumerate((height * 0.25, height * 0.74)):
        _cyl(part, f"hinge_barrel_{i}", 0.012, 0.105, (0.0, -0.002, z), metal)
        _box(part, f"hinge_leaf_{i}", (0.055, 0.006, 0.075), (0.028, -0.017, z), metal)
        # Return leaf reaches back to the fixed front stile (support path).
        _box(part, f"frame_leaf_{i}", (0.080, 0.035, 0.065), (-0.035, 0.010, z), metal)


def _add_latch_mount(part, width, height, metal, latch_face_y, prefix="latch"):
    z = height * 0.55
    bar_len = min(0.180, max(0.085, width * 0.22))
    pivot_x = width - bar_len - 0.045
    keeper_x = width - 0.036
    _box(part, f"{prefix}_pivot_plate", (0.052, 0.016, 0.038), (pivot_x, latch_face_y, z), metal)
    _box(part, f"{prefix}_keeper_plate", (0.048, 0.018, 0.034), (keeper_x, latch_face_y - 0.002, z), metal)
    _box(part, f"{prefix}_keeper_slot", (0.030, 0.022, 0.011), (keeper_x - 0.002, latch_face_y - 0.010, z), metal)
    for i, x in enumerate((pivot_x - 0.016, pivot_x + 0.016, keeper_x - 0.014, keeper_x + 0.014)):
        _cyl(part, f"{prefix}_plate_screw_{i}", 0.0045, 0.004,
             (x, latch_face_y - 0.010, z + (0.011 if i % 2 == 0 else -0.011)), metal, rpy=(math.pi / 2, 0.0, 0.0))
    return pivot_x, latch_face_y - 0.006, z, bar_len


def _add_latch_bar(part, length, metal, prefix="latch") -> None:
    _cyl(part, f"{prefix}_pivot_pin", 0.014, 0.026, (0.0, 0.0, 0.0), metal, rpy=(math.pi / 2, 0.0, 0.0))
    _box(part, f"{prefix}_hasp_bar", (length, 0.014, 0.016), (length / 2.0, -0.002, 0.0), metal)
    _box(part, f"{prefix}_hook_end", (0.026, 0.018, 0.024), (length + 0.006, -0.003, 0.0), metal)
    _cyl(part, f"{prefix}_small_pull", 0.008, 0.030, (length * 0.58, -0.012, 0.006), metal, rpy=(math.pi / 2, 0.0, 0.0))


def _solid_door_geometry(part, width, height, wood, dark_wood, metal, latch_face_y):
    # Panelled door built as ONE connected depth stack. The ``solid_panel`` slab
    # is a thick connective backbone that overlaps every other layer in Y so the
    # door is a single geometry island (front frame -> slab -> recessed inset ->
    # moldings -> surface detail -> latch mount all share volume with the slab).
    _box(part, "solid_panel", (width - 0.055, 0.034, height - 0.050), (width / 2.0, -0.014, height / 2.0), wood)
    rail = 0.050
    yf = -0.016  # frame stiles/rails; depth 0.028 -> [-0.030,-0.002] overlaps slab
    _box(part, "left_stile", (rail, 0.028, height), (rail / 2.0, yf, height / 2.0), wood)
    _box(part, "free_stile", (rail, 0.028, height), (width - rail / 2.0, yf, height / 2.0), wood)
    _box(part, "top_rail", (width, 0.028, rail), (width / 2.0, yf, height - rail / 2.0), wood)
    _box(part, "bottom_rail", (width, 0.028, rail), (width / 2.0, yf, rail / 2.0), wood)
    # Recessed inset panel behind the slab (each layer overlaps its neighbour).
    _box(part, "inset_panel_shadow", (width - 0.150, 0.012, height - 0.165), (width / 2.0, -0.030, height / 2.0), dark_wood)
    _box(part, "inset_panel_face", (width - 0.170, 0.010, height - 0.185), (width / 2.0, -0.034, height / 2.0), wood)
    # Moldings framing the inset step; deep enough to bridge slab <-> inset.
    _box(part, "inner_left_molding", (0.018, 0.018, height - 0.135), (0.090, -0.028, height / 2.0), wood)
    _box(part, "inner_right_molding", (0.018, 0.018, height - 0.135), (width - 0.090, -0.028, height / 2.0), wood)
    _box(part, "inner_top_molding", (width - 0.145, 0.018, 0.018), (width / 2.0, -0.028, height - 0.090), wood)
    _box(part, "inner_bottom_molding", (width - 0.145, 0.018, 0.018), (width / 2.0, -0.028, 0.090), wood)
    _add_wood_grain(part, "solid", width, height, -0.033, dark_wood)
    _add_face_screws(part, "solid", width, height, -0.022, dark_wood)
    _add_hinge_knuckles(part, height, metal)
    return _add_latch_mount(part, width, height, metal, latch_face_y)


def _mesh_door_geometry(part, width, height, wood, mesh, metal, latch_face_y, prefix):
    frame = 0.045
    yf = -0.018
    _box(part, f"{prefix}_hinge_stile", (frame, 0.030, height), (frame / 2.0, 0.0, height / 2.0), wood)
    _box(part, f"{prefix}_free_stile", (frame, 0.030, height), (width - frame / 2.0, 0.0, height / 2.0), wood)
    _box(part, f"{prefix}_top_rail", (width, 0.030, frame), (width / 2.0, 0.0, height - frame / 2.0), wood)
    _box(part, f"{prefix}_bottom_rail", (width, 0.030, frame), (width / 2.0, 0.0, frame / 2.0), wood)
    _box(part, f"{prefix}_mid_rail", (width, 0.025, 0.030), (width / 2.0, yf, height * 0.47), wood)
    inner_w = width - 2.0 * frame + 0.020
    inner_h = height - 2.0 * frame + 0.020
    x0, z0 = frame - 0.010, frame - 0.010
    v_count = max(4, int(inner_w / 0.055))
    for i in range(v_count + 1):
        x = x0 + inner_w * i / v_count
        _box(part, f"{prefix}_mesh_v_{i}", (0.005, 0.006, inner_h), (x, -0.026, z0 + inner_h / 2.0), mesh)
    h_count = max(5, int(inner_h / 0.055))
    for i in range(h_count + 1):
        z = z0 + inner_h * i / h_count
        _box(part, f"{prefix}_mesh_h_{i}", (inner_w, 0.006, 0.005), (x0 + inner_w / 2.0, -0.030, z), mesh)
    _add_hinge_knuckles(part, height, metal)
    return _add_latch_mount(part, width, height, metal, latch_face_y, prefix=f"{prefix}_latch")


# ===========================================================================
# Shared front-face hinge receiver (frame hardware the door knuckles rest on)
# ===========================================================================
def _door_hinge_receiver(frame, name, x, y_frame_face, y_axis, z_center, height, black) -> None:
    """Two black receiver plates on the frame at the door pivot. Each spans from
    just behind the frame front member (`y_frame_face`) to the door hinge plane
    (`y_axis`) so (a) the vertical hinge axis touches real hardware (joint-origin
    honesty) and (b) the door hinge knuckle has a support path (captured hinge)."""
    y0 = min(y_frame_face, y_axis) - 0.006
    y1 = max(y_frame_face, y_axis) + 0.006
    depth = y1 - y0
    yc = (y0 + y1) / 2.0
    for sign, tag in ((1.0, "u"), (-1.0, "l")):
        _box(frame, f"{name}_{tag}", (0.016, depth, 0.060), (x, yc, z_center + sign * height * 0.25), black)


# ===========================================================================
# Mobility
# ===========================================================================
def _build_casters(model, frame, r, mats, corners) -> list[str]:
    """4 corner caster plates/forks (frame visuals) + CONTINUOUS wheel children."""
    black, trim = mats["black"], mats["trim"]
    z_axle = CASTER_CLEARANCE - 0.055  # wheel center below the frame legs
    wheels: list[str] = []
    for i, (x, y) in enumerate(corners):
        _box(frame, f"caster_plate_{i}", (0.080, 0.070, 0.010), (x, y, CASTER_CLEARANCE - 0.008), black)
        _box(frame, f"caster_fork_a_{i}", (0.006, 0.055, 0.070), (x - 0.016, y, z_axle + 0.030), black)
        _box(frame, f"caster_fork_b_{i}", (0.006, 0.055, 0.070), (x + 0.016, y, z_axle + 0.030), black)
        wheel = model.part(f"caster_wheel_{i}")
        _cyl(wheel, f"wheel_tire_{i}", 0.034, 0.026, (0.0, 0.0, 0.0), black, rpy=(0.0, math.pi / 2, 0.0))
        _cyl(wheel, f"wheel_hub_{i}", 0.014, 0.030, (0.0, 0.0, 0.0), trim, rpy=(0.0, math.pi / 2, 0.0))
        model.articulation(
            f"fork_to_caster_wheel_{i}", ArticulationType.CONTINUOUS, parent=frame, child=wheel,
            origin=Origin(xyz=(x, y, z_axle)), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=12.0),
        )
        wheels.append(wheel.name)
    return wheels


# ===========================================================================
# Front access members
# ===========================================================================
def _build_drop_ramp(model, frame, r, mats, *, x_center, y_face, z_hinge, width, length=0.56, fold_upper=1.35) -> str:
    """Origin-A drop-down front ramp (REVOLUTE about lateral -X). ``length`` is
    the down-slope board length; kept short enough that the folded pose clears
    the compartment doors above it."""
    ramp_m, wood, trim, black = mats["ramp"], mats["wood"], mats["trim"], mats["black"]
    # Frame receiver (a lintel the ramp hinge rod nests against). Deep enough to
    # reach back and overlap the front floor rail so it shares the frame island
    # (no floating hardware) while its front face still meets the hinge line.
    _box(frame, "front_ramp_hinge_receiver", (width + 0.06, 0.075, 0.030), (x_center, y_face + 0.030, z_hinge), black)
    ramp = model.part("front_ramp")
    down = math.radians(24.0)
    half = length / 2.0
    cy = -half * math.cos(down)
    cz = -half * math.sin(down)
    _box(ramp, "ramp_board", (width, length, 0.026), (0.0, cy, cz), ramp_m, rpy=(down, 0.0, 0.0))
    rail_len = length - 0.11
    _box(ramp, "ramp_side_rail_a", (0.030, rail_len, 0.035), (-width / 2 + 0.015, cy - 0.055, cz - 0.025), wood, rpy=(down, 0.0, 0.0))
    _box(ramp, "ramp_side_rail_b", (0.030, rail_len, 0.035), (width / 2 - 0.015, cy - 0.055, cz - 0.025), wood, rpy=(down, 0.0, 0.0))
    n_cleats = max(2, int(length / 0.14))
    for j in range(n_cleats):
        y = -0.08 - j * (length - 0.12) / max(1, n_cleats - 1)
        z = y * math.sin(down) + 0.022
        _box(ramp, f"ramp_cleat_{j}", (width - 0.04, 0.022, 0.018), (0.0, y * math.cos(down), z), trim, rpy=(down, 0.0, 0.0))
    _cyl(ramp, "ramp_hinge_rod", 0.008, width + 0.02, (0.0, 0.0, 0.0), black, rpy=(0.0, math.pi / 2, 0.0))
    model.articulation(
        "frame_to_front_ramp", ArticulationType.REVOLUTE, parent=frame, child=ramp,
        origin=Origin(xyz=(x_center, y_face, z_hinge)), axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=fold_upper, effort=5.0, velocity=1.0),
    )
    return ramp.name


def _build_pop_hole(model, frame, r, mats, *, x_div, z_center) -> str:
    """Guillotine pop-hole: divider guide rails + trim (frame) + PRISMATIC +Z
    clear slide panel child (slide_door fork)."""
    wood, trim, black, clear = mats["wood"], mats["trim"], mats["black"], mats["clear"]
    pop_w, pop_h = 0.20, 0.28
    pop_z0, pop_z1 = z_center - pop_h / 2 - 0.02, z_center + pop_h / 2 + 0.02
    # Pop-hole wooden frame trim (four sides) on the divider.
    tw, td = 0.032, 0.018
    _box(frame, "pop_hole_frame_top", (td, pop_w + 2 * tw, tw), (x_div + 0.004, 0.0, pop_z1 + tw / 2), trim)
    _box(frame, "pop_hole_frame_bottom", (td, pop_w + 2 * tw, tw), (x_div + 0.004, 0.0, pop_z0 - tw / 2), trim)
    _box(frame, "pop_hole_frame_left", (td, tw, (pop_z1 - pop_z0) + 2 * tw), (x_div + 0.004, -pop_w / 2 - tw / 2, (pop_z0 + pop_z1) / 2), trim)
    _box(frame, "pop_hole_frame_right", (td, tw, (pop_z1 - pop_z0) + 2 * tw), (x_div + 0.004, pop_w / 2 + tw / 2, (pop_z0 + pop_z1) / 2), trim)
    # Two U-channel guide rails that capture the sliding panel through travel.
    gz0, gz1 = pop_z0 - 0.03, pop_z1 + 0.28
    gh = gz1 - gz0
    gw, gd, gap = 0.010, 0.016, 0.016
    for sign, side in ((-1.0, "left"), (1.0, "right")):
        yc = sign * (pop_w / 2 + tw + gap / 2 + gw / 2)
        _box(frame, f"pop_hole_guide_{side}_outer", (gd, gw, gh), (x_div + gd / 2, yc, (gz0 + gz1) / 2), wood)
        _box(frame, f"pop_hole_guide_{side}_inner", (gd, gw, gh), (x_div + gd / 2, yc - sign * (gw + gap), (gz0 + gz1) / 2), wood)
    _box(frame, "pop_hole_bottom_stop", (0.028, pop_w + 0.008, 0.012), (x_div - 0.008, 0.0, pop_z0 + 0.001), trim)
    # Sliding panel child (lift +Z to open).
    pop = model.part("pop_hole_door")
    panel_t = 0.012
    _box(pop, "pop_panel", (panel_t, pop_w, pop_h), (0.0, 0.0, 0.0), clear)
    _box(pop, "pop_panel_top_rail", (panel_t + 0.004, pop_w + 0.008, 0.018), (0.0, 0.0, pop_h / 2 + 0.008), wood)
    _box(pop, "pop_panel_bottom_rail", (panel_t + 0.004, pop_w + 0.008, 0.014), (0.0, 0.0, -pop_h / 2 - 0.006), wood)
    arm_x = panel_t / 2 + 0.019
    _box(pop, "pop_pull_bracket", (0.040, 0.024, 0.018), (arm_x, 0.0, pop_h / 2 + 0.018), black)
    _cyl(pop, "pop_pull_loop", 0.014, 0.020, (arm_x + 0.012, 0.0, pop_h / 2 + 0.026), black, rpy=(0.0, math.pi / 2, 0.0))
    model.articulation(
        "frame_to_pop_hole_door", ArticulationType.PRISMATIC, parent=frame, child=pop,
        origin=Origin(xyz=(x_div, 0.0, z_center)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=0.24, effort=15.0, velocity=0.40),
    )
    return pop.name


# ===========================================================================
# Slot A candidate: wheeled_hutch_run  (Origin A)
# ===========================================================================
def _build_wheeled(model, frame, r, mats) -> dict:
    wood, trim, mesh, black, tray_m, clear = (
        mats["wood"], mats["trim"], mats["mesh"], mats["black"], mats["tray"], mats["clear"],
    )
    ohs = r.roof_overhang_scale
    x_left, x_mid, x_right = -0.80, -0.18, 0.84
    y_front, y_back = -0.36, 0.36
    z_bot = r.leg_bottom_z
    z_floor, z_mid, z_top = 0.30, 0.70, 1.08
    post = 0.045

    for ix, x in enumerate((x_left, x_mid, x_right)):
        for iy, y in enumerate((y_front, y_back)):
            _box(frame, f"post_{ix}_{iy}", (post, post, z_top - z_bot), (x, y, (z_top + z_bot) / 2), wood)
    # Rails
    for iz, z in enumerate((z_floor, z_mid, z_top)):
        _box(frame, f"front_rail_{iz}", (x_right - x_left + post, post, post), ((x_left + x_right) / 2, y_front, z), wood)
        _box(frame, f"back_rail_{iz}", (x_right - x_left + post, post, post), ((x_left + x_right) / 2, y_back, z), wood)
        _box(frame, f"left_side_rail_{iz}", (post, y_back - y_front + post, post), (x_left, 0.0, z), wood)
        _box(frame, f"divider_side_rail_{iz}", (post, y_back - y_front + post, post), (x_mid, 0.0, z), wood)
        _box(frame, f"right_side_rail_{iz}", (post, y_back - y_front + post, post), (x_right, 0.0, z), wood)
    # Shelves / platforms
    _box(frame, "left_mid_shelf", (0.63, 0.72, 0.026), (-0.49, 0.0, z_mid - 0.020), wood)
    _box(frame, "run_upper_platform", (0.34, 0.62, 0.030), (0.00, 0.0, 0.745), wood)
    _box(frame, "run_back_floor_rail", (0.98, 0.130, 0.030), (0.33, 0.320, z_floor + 0.005), trim)
    _box(frame, "run_front_floor_rail", (0.98, 0.130, 0.030), (0.33, -0.320, z_floor + 0.005), trim)
    # Left compartment solid walls
    _box(frame, "upper_back_panel", (0.56, 0.018, 0.34), (-0.49, y_back + 0.018, 0.885), wood)
    for i, z in enumerate((0.790, 0.875, 0.960)):
        _box(frame, f"upper_back_plank_line_{i}", (0.54, 0.010, 0.008), (-0.49, y_back + 0.030, z), trim)
    _box(frame, "left_solid_side", (0.018, 0.64, 0.36), (x_left - 0.010, 0.0, 0.880), wood)
    _box(frame, "left_lower_back_mesh_frame", (0.62, 0.030, 0.32), (-0.49, y_back + 0.005, 0.500), trim)
    # Wire-mesh run panels
    _front_mesh(frame, "run_back_mesh", x_mid + 0.055, x_right - 0.055, z_floor + 0.055, z_top - 0.065, y_back + 0.010, mesh)
    _side_mesh(frame, "run_side_mesh", y_front + 0.055, y_back - 0.055, z_floor + 0.055, z_top - 0.065, x_right + 0.010, mesh)
    # Divider mesh: full unless a pop-hole opening is carved (front_access).
    if r.front_access != "guillotine_pop_hole":
        _side_mesh(frame, "divider_mesh", y_front + 0.055, y_back - 0.055, z_floor + 0.055, z_top - 0.065, x_mid + 0.010, mesh)
    else:
        pop_y0, pop_y1 = -0.12, 0.12
        pop_z0, pop_z1 = 0.40, 0.62
        dvx = x_mid + 0.010
        _side_mesh(frame, "divider_mesh_below", y_front + 0.055, y_back - 0.055, z_floor + 0.055, pop_z0, dvx, mesh)
        _side_mesh(frame, "divider_mesh_above", y_front + 0.055, y_back - 0.055, pop_z1, z_top - 0.065, dvx, mesh)
        _side_mesh(frame, "divider_mesh_left", y_front + 0.055, pop_y0, pop_z0, pop_z1, dvx, mesh)
        _side_mesh(frame, "divider_mesh_right", pop_y1, y_back - 0.055, pop_z0, pop_z1, dvx, mesh)
    # Fixed roof over the enclosed left compartment. The left overhang sits just
    # inboard of the run roof lid, so it is NOT scaled (only the free front/back
    # lips ride roof_overhang_scale) to keep clear of the lid.
    _box(frame, "left_roof_overhang", (0.70, 0.82, 0.035), (-0.50, 0.0, 1.115), trim)
    _box(frame, "left_roof_white_edge", (0.66, 0.76, 0.018), (-0.50, 0.0, 1.090), wood)
    _box(frame, "front_roof_lip", (1.68, 0.038 * ohs, 0.035), (0.02, y_front - 0.025, 1.070), wood)
    _box(frame, "back_roof_lip", (1.68, 0.038 * ohs, 0.035), (0.02, y_back + 0.025, 1.070), wood)

    # Door hinge receivers (frame hardware). Left compartment doors at x_mid front.
    face = y_front - post / 2  # front face of the front posts/rails
    _door_hinge_receiver(frame, "upper_receiver", x_mid - 0.028, face, y_front - 0.050, 0.875, 0.30, black)
    _door_hinge_receiver(frame, "lower_receiver", x_mid - 0.028, face, y_front - 0.050, 0.505, 0.30, black)
    _door_hinge_receiver(frame, "run_receiver", x_right - 0.030, face, y_front - 0.052, 0.690, 0.62, black)

    doors: list[tuple[str, float]] = []
    # Upper acrylic door
    upper = model.part("upper_door")
    _panel_door(upper, "upper_door", 0.50, 0.30, mats, mesh=False, acrylic=True)
    model.articulation("frame_to_upper_door", ArticulationType.REVOLUTE, parent=frame, child=upper,
                       origin=Origin(xyz=(x_mid - 0.028, y_front - 0.050, 0.875)), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(lower=0.0, upper=r.door_swing, effort=6.0, velocity=1.5))
    doors.append(("upper_door", 0.30))
    # Lower mesh door — omitted when the drop ramp serves the lower opening
    # (the drop-down ramp IS the lower-compartment access on that variant).
    if r.front_access != "drop_ramp":
        lower = model.part("lower_door")
        _panel_door(lower, "lower_door", 0.50, 0.30, mats, mesh=True)
        model.articulation("frame_to_lower_door", ArticulationType.REVOLUTE, parent=frame, child=lower,
                           origin=Origin(xyz=(x_mid - 0.028, y_front - 0.050, 0.505)), axis=(0.0, 0.0, 1.0),
                           motion_limits=MotionLimits(lower=0.0, upper=r.door_swing, effort=6.0, velocity=1.5))
        doors.append(("lower_door", 0.30))
    # Large run mesh door
    run = model.part("run_door")
    _panel_door(run, "run_door", 0.88, 0.62, mats, mesh=True)
    model.articulation("frame_to_run_door", ArticulationType.REVOLUTE, parent=frame, child=run,
                       origin=Origin(xyz=(x_right - 0.030, y_front - 0.052, 0.690)), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(lower=0.0, upper=min(r.door_swing, 1.45), effort=7.0, velocity=1.2))
    doors.append(("run_door", 0.62))

    # Top-hinge roof lid over the run.
    roof = model.part("roof_lid")
    _box(roof, "roof_panel", (0.95, 0.78, 0.035), (0.0, -0.39, 0.018), trim)
    _box(roof, "roof_front_edge", (0.95, 0.035, 0.040), (0.0, -0.775, -0.010), wood)
    _box(roof, "roof_side_edge_a", (0.035, 0.78, 0.038), (-0.475, -0.39, -0.012), wood)
    _box(roof, "roof_side_edge_b", (0.035, 0.78, 0.038), (0.475, -0.39, -0.012), wood)
    _cyl(roof, "roof_piano_hinge", 0.009, 0.90, (0.0, 0.0, -0.006), black, rpy=(0.0, math.pi / 2, 0.0))
    model.articulation("frame_to_roof_lid", ArticulationType.REVOLUTE, parent=frame, child=roof,
                       origin=Origin(xyz=(0.35, y_back + 0.030, 1.1335)), axis=(-1.0, 0.0, 0.0),
                       motion_limits=MotionLimits(lower=0.0, upper=1.20, effort=8.0, velocity=1.0))

    # Slide-out tray under the run.
    tray = model.part("floor_tray")
    _box(tray, "tray_pan", (0.86, 0.58, 0.025), (0.0, 0.0, 0.0), tray_m)
    _box(tray, "tray_front_pull", (0.28, 0.018, 0.030), (0.0, -0.293, 0.018), black)
    # Runners the tray rests on (frame hardware, gives the tray a support path).
    for sgn, tag in ((-1.0, "0"), (1.0, "1")):
        _box(frame, f"tray_runner_{tag}", (0.030, 0.60, 0.020), (0.32 + sgn * 0.44, 0.0, z_floor + 0.020), trim)
    model.articulation("frame_to_floor_tray", ArticulationType.PRISMATIC, parent=frame, child=tray,
                       origin=Origin(xyz=(0.32, 0.0, z_floor + 0.030)), axis=(0.0, -1.0, 0.0),
                       motion_limits=MotionLimits(lower=0.0, upper=r.tray_travel, effort=25.0, velocity=0.25))

    corners = [(x_left + 0.035, y_front + 0.035), (x_left + 0.035, y_back - 0.035),
               (x_right - 0.035, y_front + 0.035), (x_right - 0.035, y_back - 0.035)]
    return {
        "doors": doors, "latched_doors": [], "tray": "floor_tray", "roof_lid": "roof_lid",
        "corners": corners, "tray_runners": ["tray_runner_0", "tray_runner_1"],
        "ramp_mount": dict(x_center=-0.50, y_face=y_front - 0.055, z_hinge=z_floor - 0.010, width=0.34, length=0.40, fold_upper=1.30),
        "pop_mount": dict(x_div=x_mid, z_center=0.51),
        "door_receivers": {"upper_door": "upper_receiver", "lower_door": "lower_receiver", "run_door": "run_receiver"},
    }


# ===========================================================================
# Slot A candidate: grid_cabinet  (Origin B, n_tiers multiplicity)
# ===========================================================================
GRID_FRONT_Y = -0.430
# Latch mount face kept close to the door body so its pivot/keeper plates overlap
# the door slab (single geometry island); the latch child hangs off this face.
GRID_LATCH_FACE_Y = -0.034


def _build_grid(model, frame, r, mats) -> dict:
    wood, dark, mesh, black, tray_m = (
        mats["wood"], mats["trim"], mats["mesh"], mats["black"], mats["tray"],
    )
    ohs = r.roof_overhang_scale
    n_tiers = r.n_tiers
    width, depth = 2.40, 0.72
    door_h = 0.465
    tier_spacing = 0.580
    body_bottom = 0.18 + (3 - n_tiers) * 0.14
    row_bottoms = [body_bottom + 0.085 + i * tier_spacing for i in range(n_tiers)]
    body_top = row_bottoms[-1] + door_h + 0.055
    front_rail_y, rear_y = -0.370, 0.360
    post = 0.060
    z_bot = r.leg_bottom_z
    cab_h = body_top - body_bottom
    cab_cz = (body_top + body_bottom) / 2.0

    for ix, x in enumerate((-width / 2 + post / 2, width / 2 - post / 2)):
        for iy, y in enumerate((front_rail_y, rear_y)):
            _box(frame, f"leg_{ix}_{iy}", (post, post, body_top - z_bot), (x, y, (body_top + z_bot) / 2), wood)
    x_lines = (-1.20, -0.52, -0.10, 1.20)
    for i, x in enumerate(x_lines):
        _box(frame, f"front_stile_{i}", (0.060, 0.065, cab_h), (x, front_rail_y, cab_cz), wood)
    rail_gap = 0.055
    rail_zs = [row_bottoms[0] - rail_gap]
    for i in range(n_tiers - 1):
        rail_zs.append((row_bottoms[i] + door_h + row_bottoms[i + 1]) / 2.0)
    rail_zs.append(row_bottoms[-1] + door_h + rail_gap)
    for i, z in enumerate(rail_zs):
        _box(frame, f"front_rail_{i}", (width, 0.065, 0.060), (0.0, front_rail_y, z), wood)
    # Vertical hinge mullions (one per door column): full-height members that
    # reach forward to the door hinge plane (y=GRID_FRONT_Y) so every door's
    # vertical hinge axis touches real hardware (joint-origin honesty) while
    # overlapping the front rails for a connected support path.
    for kind, hinge_x, _dw in (("solid", -1.130, 0.0), ("mesh_narrow", -0.455, 0.0), ("mesh_wide", -0.030, 0.0)):
        _box(frame, f"hinge_mullion_{kind}", (0.020, 0.075, cab_h), (hinge_x, -0.400, cab_cz), wood)
    for i, z in enumerate(row_bottoms):
        _box(frame, f"compartment_floor_{i}", (width - 0.08, depth + 0.02, 0.030), (0.0, 0.010, z - 0.035), wood)
    _box(frame, "back_wall", (width - 0.08, 0.040, cab_h - 0.04), (0.0, 0.390, cab_cz), wood)
    _box(frame, "side_wall_0", (0.040, depth + 0.08, cab_h - 0.04), (-1.230, 0.020, cab_cz), wood)
    _box(frame, "side_wall_1", (0.040, depth + 0.08, cab_h - 0.04), (1.230, 0.020, cab_cz), wood)
    for i, f in enumerate((0.12, 0.32, 0.55, 0.78)):
        z = body_bottom + cab_h * f
        _box(frame, f"side_plank_seam_0_{i}", (0.006, depth - 0.10, 0.010), (-1.253, 0.020, z), dark)
        _box(frame, f"side_plank_seam_1_{i}", (0.006, depth - 0.10, 0.010), (1.253, 0.020, z), dark)
        _box(frame, f"back_plank_seam_{i}", (width - 0.18, 0.006, 0.010), (0.0, 0.413, z), dark)
    # Sloped overhang roof (offsets from body_top; overhang rides roof_overhang_scale).
    rc_y, rc_z = 0.010, body_top + 0.032
    pitch = 0.035
    # Fascia boards ride the sloped panel's scaled edges (they track
    # roof_overhang_scale) so they always straddle the panel rim with no gap
    # regardless of overhang — a fixed offset floated off when the overhang shrank.
    roof_half_y = (depth + 0.18) * ohs / 2.0
    roof_half_x = (width + 0.22) * ohs / 2.0
    _box(frame, "roof_bearing_frame", (width + 0.08, depth + 0.04, 0.050), (0.0, rc_y, body_top - 0.002), wood)
    _box(frame, "sloped_roof_panel", ((width + 0.22) * ohs, (depth + 0.18) * ohs, 0.075), (0.0, rc_y, rc_z), wood, rpy=(pitch, 0.0, 0.0))
    _box(frame, "front_roof_fascia", ((width + 0.28) * ohs, 0.060, 0.105), (0.0, rc_y - roof_half_y, body_top + 0.005), dark, rpy=(pitch, 0.0, 0.0))
    _box(frame, "rear_roof_fascia", ((width + 0.22) * ohs, 0.055, 0.095), (0.0, rc_y + roof_half_y, body_top + 0.018), dark, rpy=(pitch, 0.0, 0.0))
    _box(frame, "left_roof_side_fascia", (0.070, (depth + 0.18) * ohs, 0.105), (-roof_half_x + 0.025, rc_y, body_top + 0.012), dark, rpy=(pitch, 0.0, 0.0))
    _box(frame, "right_roof_side_fascia", (0.070, (depth + 0.18) * ohs, 0.105), (roof_half_x - 0.025, rc_y, body_top + 0.012), dark, rpy=(pitch, 0.0, 0.0))
    # Tray runners + slide-out cleaning tray.
    tray_runner_z = body_bottom - 0.0175
    _box(frame, "tray_runner_0", (0.045, 0.610, 0.035), (-1.105, -0.0325, tray_runner_z), dark)
    _box(frame, "tray_runner_1", (0.045, 0.610, 0.035), (1.105, -0.0325, tray_runner_z), dark)

    columns = (("solid", -1.130, 0.555), ("mesh_narrow", -0.455, 0.300), ("mesh_wide", -0.030, 1.125))
    latched: list[tuple[str, str]] = []
    doors: list[tuple[str, float]] = []
    for row, z0 in enumerate(row_bottoms):
        for kind, hinge_x, door_w in columns:
            name = f"{kind}_door_{row}"
            door = model.part(name)
            if kind == "solid":
                lox, loy, loz, ll = _solid_door_geometry(door, door_w, door_h, wood, dark, black, GRID_LATCH_FACE_Y)
            else:
                pfx = "narrow" if kind == "mesh_narrow" else "wide"
                lox, loy, loz, ll = _mesh_door_geometry(door, door_w, door_h, wood, mesh, black, GRID_LATCH_FACE_Y, pfx)
            model.articulation(f"frame_to_{name}", ArticulationType.REVOLUTE, parent=frame, child=door,
                               origin=Origin(xyz=(hinge_x, GRID_FRONT_Y, z0)), axis=(0.0, 0.0, -1.0),
                               motion_limits=MotionLimits(effort=8.0, velocity=1.8, lower=0.0, upper=r.door_swing))
            doors.append((name, door_h))
            latch = model.part(f"{name}_latch")
            _add_latch_bar(latch, ll, black, prefix=f"{name}_latch")
            model.articulation(f"{name}_to_latch", ArticulationType.REVOLUTE, parent=door, child=latch,
                               origin=Origin(xyz=(lox, loy, loz)), axis=(0.0, 1.0, 0.0),
                               motion_limits=MotionLimits(effort=1.5, velocity=2.0, lower=0.0, upper=1.15))
            latched.append((name, f"{name}_latch"))

    tray = model.part("cleaning_tray")
    _box(tray, "tray_pan", (2.115, 0.515, 0.018), (0.0, 0.235, 0.0), tray_m)
    _box(tray, "front_lip", (2.100, 0.030, 0.065), (0.0, -0.030, 0.000), tray_m)
    _box(tray, "tray_handle", (0.280, 0.020, 0.030), (0.0, -0.055, 0.025), black)
    _box(tray, "side_lip_0", (0.025, 0.500, 0.045), (-1.070, 0.220, 0.020), tray_m)
    _box(tray, "side_lip_1", (0.025, 0.500, 0.045), (1.070, 0.220, 0.020), tray_m)
    model.articulation("frame_to_cleaning_tray", ArticulationType.PRISMATIC, parent=frame, child=tray,
                       origin=Origin(xyz=(0.0, -0.330, body_bottom - 0.055)), axis=(0.0, -1.0, 0.0),
                       motion_limits=MotionLimits(effort=25.0, velocity=0.25, lower=0.0, upper=min(r.tray_travel, 0.32)))

    corners = [(-width / 2 + post / 2, front_rail_y), (-width / 2 + post / 2, rear_y),
               (width / 2 - post / 2, front_rail_y), (width / 2 - post / 2, rear_y)]
    return {
        "doors": doors, "latched_doors": latched, "tray": "cleaning_tray", "roof_lid": None,
        "corners": corners, "tray_runners": [],
        "ramp_mount": None,
        # Rabbit-exit guillotine pop-hole in the right side wall (clear of the
        # front doors and the front-sliding tray). Panel sits just outside the
        # side-wall outer face (x≈1.250).
        "pop_mount": dict(x_div=1.250, z_center=row_bottoms[0] + 0.12),
        "door_receivers": {},
    }


# ===========================================================================
# Slot A candidate: aframe_ark  (fork; box gable planks instead of cadquery)
# ===========================================================================
def _build_aframe(model, frame, r, mats) -> dict:
    wood, trim, mesh, black, tray_m = (
        mats["wood"], mats["trim"], mats["mesh"], mats["black"], mats["tray"],
    )
    X_NEST_END, X_NEST_FRONT, X_RUN_END = -0.70, -0.20, 0.70
    Y_HALF = 0.40
    z_leg = r.leg_bottom_z
    Z_BASE, Z_RIDGE = 0.25, 0.95
    RISE = Z_RIDGE - Z_BASE
    SLOPE_ANGLE = math.atan2(RISE, Y_HALF)
    SLOPE_LEN = math.hypot(RISE, Y_HALF)
    TILT = math.pi / 2 - SLOPE_ANGLE
    L_ROLL, R_ROLL = -TILT, TILT
    FRAME_LEN = X_RUN_END - X_NEST_END
    FRAME_CX = (X_NEST_END + X_RUN_END) / 2
    NEST_CX = (X_NEST_END + X_NEST_FRONT) / 2
    NEST_LEN = X_NEST_FRONT - X_NEST_END
    POST = 0.042

    def gable(prefix, x_pos):
        _box(frame, f"{prefix}_base_rail", (POST, 2 * Y_HALF + POST, POST), (x_pos, 0.0, Z_BASE), wood)
        _box(frame, f"{prefix}_left_rafter", (POST, POST, SLOPE_LEN), (x_pos, -Y_HALF / 2, (Z_BASE + Z_RIDGE) / 2), wood, rpy=(L_ROLL, 0.0, 0.0))
        _box(frame, f"{prefix}_right_rafter", (POST, POST, SLOPE_LEN), (x_pos, Y_HALF / 2, (Z_BASE + Z_RIDGE) / 2), wood, rpy=(R_ROLL, 0.0, 0.0))

    def gable_planks(prefix, x_pos, n=7):
        ph = RISE / n
        for i in range(n):
            t = (i + 0.5) / n
            z = Z_BASE + RISE * t
            w = 2 * Y_HALF * (1 - t) - 0.06
            if w > 0.04:
                _box(frame, f"{prefix}_plank_{i}", (0.018, w, ph - 0.003), (x_pos, 0.0, z), wood)

    def slope_mesh(prefix, x0, x1, y_sign):
        roll = L_ROLL if y_sign < 0 else R_ROLL
        w = x1 - x0
        cols = max(3, int(w / 0.095))
        rows = max(3, int(SLOPE_LEN / 0.085))
        yc = y_sign * Y_HALF / 2
        zc = (Z_BASE + Z_RIDGE) / 2
        for j in range(rows + 1):
            t = j / rows
            y = y_sign * Y_HALF * (1 - t)
            z = Z_BASE + RISE * t
            _box(frame, f"{prefix}_h_{j}", (w + 0.006, 0.010, 0.006), ((x0 + x1) / 2, y, z), mesh, rpy=(roll, 0.0, 0.0))
        for i in range(cols + 1):
            x = x0 + w * i / cols
            _box(frame, f"{prefix}_v_{i}", (0.006, 0.010, SLOPE_LEN + 0.006), (x, yc, zc), mesh, rpy=(roll, 0.0, 0.0))

    # Legs + base rails + ridge
    for i, (lx, ly) in enumerate(((X_NEST_END, -Y_HALF), (X_NEST_END, Y_HALF), (X_RUN_END, -Y_HALF), (X_RUN_END, Y_HALF))):
        _box(frame, f"leg_{i}", (POST, POST, Z_BASE - z_leg), (lx, ly, (Z_BASE + z_leg) / 2), wood)
    _box(frame, "left_base_rail", (FRAME_LEN + POST, POST, POST), (FRAME_CX, -Y_HALF, Z_BASE), wood)
    _box(frame, "right_base_rail", (FRAME_LEN + POST, POST, POST), (FRAME_CX, Y_HALF, Z_BASE), wood)
    _box(frame, "back_base_rail", (POST, 2 * Y_HALF + POST, POST), (X_NEST_END, 0.0, Z_BASE), wood)
    _box(frame, "front_base_rail", (POST, 2 * Y_HALF + POST, POST), (X_RUN_END, 0.0, Z_BASE), wood)
    _box(frame, "divider_base_rail", (POST, 2 * Y_HALF + POST, POST), (X_NEST_FRONT, 0.0, Z_BASE), wood)
    _box(frame, "ridge_beam", (FRAME_LEN + POST, POST, POST), (FRAME_CX, 0.0, Z_RIDGE), wood)
    gable("nest_back_gable", X_NEST_END)
    gable("divider_gable", X_NEST_FRONT)
    gable("run_front_gable", X_RUN_END)
    # Nest box: solid slope panels + gable planks + floor
    _box(frame, "nest_left_slope_panel", (NEST_LEN, 0.018, SLOPE_LEN), (NEST_CX, -Y_HALF / 2, (Z_BASE + Z_RIDGE) / 2), wood, rpy=(L_ROLL, 0.0, 0.0))
    _box(frame, "nest_right_slope_panel", (NEST_LEN, 0.018, SLOPE_LEN), (NEST_CX, Y_HALF / 2, (Z_BASE + Z_RIDGE) / 2), wood, rpy=(R_ROLL, 0.0, 0.0))
    _box(frame, "nest_floor", (NEST_LEN, 2 * Y_HALF - 0.04, 0.018), (NEST_CX, 0.0, Z_BASE + 0.009), wood)
    gable_planks("nest_back_gable_wall", X_NEST_END)
    gable_planks("nest_divider_wall", X_NEST_FRONT)
    for i, t in enumerate((0.25, 0.50, 0.75)):
        y = -Y_HALF * (1 - t)
        z = Z_BASE + RISE * t
        _box(frame, f"nest_left_plank_line_{i}", (NEST_LEN - 0.02, 0.008, 0.006), (NEST_CX, y - 0.012, z), trim, rpy=(L_ROLL, 0.0, 0.0))
        _box(frame, f"nest_right_plank_line_{i}", (NEST_LEN - 0.02, 0.008, 0.006), (NEST_CX, -y + 0.012, z), trim, rpy=(R_ROLL, 0.0, 0.0))
    # Run section wire mesh (right slope full; left slope split around the door).
    DOOR_W, DOOR_H = 0.50, 0.55
    DOOR_CX = (X_NEST_FRONT + X_RUN_END) / 2
    slope_mesh("run_right_slope_mesh", X_NEST_FRONT + 0.04, X_RUN_END - 0.04, +1)
    lo_x1 = DOOR_CX - DOOR_W / 2 - 0.03
    hi_x0 = DOOR_CX + DOOR_W / 2 + 0.03
    if lo_x1 > X_NEST_FRONT + 0.06:
        slope_mesh("run_left_slope_mesh_lo", X_NEST_FRONT + 0.04, lo_x1, -1)
    if hi_x0 < X_RUN_END - 0.06:
        slope_mesh("run_left_slope_mesh_hi", hi_x0, X_RUN_END - 0.04, -1)

    # Door hinge plates (frame hardware on the left base rail).
    plate_z = Z_BASE + POST / 2
    _box(frame, "door_hinge_plate_a", (0.055, 0.025, 0.014), (DOOR_CX - DOOR_W * 0.25, -Y_HALF, plate_z), black)
    _box(frame, "door_hinge_plate_b", (0.055, 0.025, 0.014), (DOOR_CX + DOOR_W * 0.25, -Y_HALF, plate_z), black)
    # Tray rails under the nest box.
    TRAY_W = 0.60
    _box(frame, "tray_rail_left", (NEST_LEN - 0.04, 0.025, 0.020), (NEST_CX, -TRAY_W / 2 - 0.030, Z_BASE - 0.028), trim)
    _box(frame, "tray_rail_right", (NEST_LEN - 0.04, 0.025, 0.020), (NEST_CX, TRAY_W / 2 + 0.030, Z_BASE - 0.028), trim)

    # Run door on the left slope (REVOLUTE about slope-aligned X).
    run_door = model.part("run_door")
    stile, thick = 0.035, 0.028
    _box(run_door, "door_left_stile", (stile, thick, DOOR_H), (-DOOR_W / 2 + stile / 2, 0.0, DOOR_H / 2), wood)
    _box(run_door, "door_right_stile", (stile, thick, DOOR_H), (DOOR_W / 2 - stile / 2, 0.0, DOOR_H / 2), wood)
    _box(run_door, "door_bottom_rail", (DOOR_W, thick, stile), (0.0, 0.0, stile / 2), wood)
    _box(run_door, "door_top_rail", (DOOR_W, thick, stile), (0.0, 0.0, DOOR_H - stile / 2), wood)
    _box(run_door, "door_inner_lip", (DOOR_W - 0.07, 0.010, DOOR_H - 0.07), (0.0, -0.003, DOOR_H / 2), trim)
    mw, mh = DOOR_W - 0.09, DOOR_H - 0.09
    dc, dr = max(3, int(mw / 0.080)), max(3, int(mh / 0.080))
    for i in range(dc + 1):
        x = -mw / 2 + mw * i / dc
        _box(run_door, f"door_mesh_v_{i}", (0.004, 0.005, mh), (x, -0.006, DOOR_H / 2), mesh)
    for j in range(dr + 1):
        z = stile + mh * j / dr
        _box(run_door, f"door_mesh_h_{j}", (mw, 0.005, 0.004), (0.0, -0.006, z), mesh)
    _cyl(run_door, "door_hinge_knuckle_a", 0.009, 0.050, (-DOOR_W * 0.25, 0.0, 0.0), black, rpy=(0.0, math.pi / 2, 0.0))
    _cyl(run_door, "door_hinge_knuckle_b", 0.009, 0.050, (DOOR_W * 0.25, 0.0, 0.0), black, rpy=(0.0, math.pi / 2, 0.0))
    _box(run_door, "door_latch_plate", (0.040, 0.012, 0.025), (0.0, -0.018, DOOR_H - 0.025), black)
    _cyl(run_door, "door_latch_knob", 0.008, 0.014, (0.0, -0.030, DOOR_H - 0.025), black, rpy=(math.pi / 2, 0.0, 0.0))
    hinge_z = Z_BASE + POST / 2
    model.articulation("frame_to_run_door", ArticulationType.REVOLUTE, parent=frame, child=run_door,
                       origin=Origin(xyz=(DOOR_CX, -Y_HALF, hinge_z), rpy=(L_ROLL, 0.0, 0.0)), axis=(1.0, 0.0, 0.0),
                       motion_limits=MotionLimits(lower=0.0, upper=min(r.door_swing, 1.35), effort=6.0, velocity=1.2))

    # Slide-out floor tray under the nest box.
    tray = model.part("floor_tray")
    TRAY_LEN = NEST_LEN - 0.14
    _box(tray, "tray_pan", (TRAY_LEN, TRAY_W, 0.025), (0.0, 0.0, 0.0), tray_m)
    _box(tray, "tray_front_pull", (0.26, 0.018, 0.028), (0.0, -TRAY_W / 2, 0.016), black)
    model.articulation("frame_to_floor_tray", ArticulationType.PRISMATIC, parent=frame, child=tray,
                       origin=Origin(xyz=(NEST_CX, 0.0, Z_BASE - 0.030)), axis=(0.0, -1.0, 0.0),
                       motion_limits=MotionLimits(lower=0.0, upper=r.tray_travel, effort=25.0, velocity=0.25))

    corners = [(X_NEST_END, -Y_HALF), (X_NEST_END, Y_HALF), (X_RUN_END, -Y_HALF), (X_RUN_END, Y_HALF)]
    return {
        "doors": [("run_door", DOOR_H)], "latched_doors": [], "tray": "floor_tray", "roof_lid": None,
        "corners": corners, "tray_runners": ["tray_rail_left", "tray_rail_right"],
        "ramp_mount": dict(x_center=X_NEST_END, y_face=0.0, z_hinge=Z_BASE - 0.05, width=0.30, aframe=True),
        "pop_mount": dict(x_div=X_NEST_FRONT, z_center=Z_BASE + 0.30),
        "door_receivers": {"run_door": "door_hinge_plate"},
    }


FORM_BUILDERS = {
    "wheeled_hutch_run": _build_wheeled,
    "grid_cabinet": _build_grid,
    "aframe_ark": _build_aframe,
}


# ===========================================================================
# Assembly
# ===========================================================================
def build_rabbit_hutch(config: RabbitHutchConfig | None = None, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    pal = PALETTES[r.palette]
    mats = {k: model.material(f"hutch_{k}_{r.palette}", rgba=v) for k, v in pal.items()}

    frame = model.part("hutch_frame")
    info = FORM_BUILDERS[r.body_form](model, frame, r, mats)

    # Mobility
    casters: list[str] = []
    if r.mobility == "swivel_casters":
        casters = _build_casters(model, frame, r, mats, info["corners"])

    # Front access
    ramp = None
    pop = None
    if r.front_access == "drop_ramp":
        rm = dict(info["ramp_mount"])
        rm.pop("aframe", None)
        if info["ramp_mount"].get("aframe"):
            ramp = _build_aframe_ramp(model, frame, r, mats, **rm)
        else:
            ramp = _build_drop_ramp(model, frame, r, mats, **rm)
    elif r.front_access == "guillotine_pop_hole" and info["pop_mount"] is not None:
        pop = _build_pop_hole(model, frame, r, mats, **info["pop_mount"])

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["hutch_info"] = {
        "doors": info["doors"], "latched_doors": info["latched_doors"], "tray": info["tray"],
        "roof_lid": info["roof_lid"], "casters": casters, "ramp": ramp, "pop": pop,
        "tray_runners": info["tray_runners"], "door_receivers": info["door_receivers"],
    }
    return model


def _build_aframe_ramp(model, frame, r, mats, *, x_center, y_face, z_hinge, width) -> str:
    """A-frame drop ramp: hinge at the nest back, drops toward the ground (fork)."""
    ramp_m, wood, trim, black = mats["ramp"], mats["wood"], mats["trim"], mats["black"]
    RAMP_LEN = 0.40
    down = math.asin(max(0.05, min(0.9, (z_hinge) / RAMP_LEN)))
    _box(frame, "ramp_hinge_plate", (0.030, width + 0.04, 0.10), (x_center + 0.020, 0.0, z_hinge - 0.02), black)
    ramp = model.part("front_ramp")
    _box(ramp, "ramp_board", (RAMP_LEN, width, 0.024), (-RAMP_LEN / 2, 0.0, 0.0), ramp_m)
    for j in range(4):
        t = (j + 1) / 5
        _box(ramp, f"ramp_cleat_{j}", (0.018, width - 0.06, 0.016), (-RAMP_LEN * t, 0.0, 0.020), trim)
    _box(ramp, "ramp_side_rail_a", (RAMP_LEN - 0.08, 0.028, 0.032), (-RAMP_LEN / 2 - 0.04, -width / 2 + 0.014, 0.020), wood)
    _box(ramp, "ramp_side_rail_b", (RAMP_LEN - 0.08, 0.028, 0.032), (-RAMP_LEN / 2 - 0.04, width / 2 - 0.014, 0.020), wood)
    _cyl(ramp, "ramp_hinge_rod", 0.008, width + 0.04, (0.0, 0.0, 0.0), black, rpy=(math.pi / 2, 0.0, 0.0))
    model.articulation("frame_to_front_ramp", ArticulationType.REVOLUTE, parent=frame, child=ramp,
                       origin=Origin(xyz=(x_center, 0.0, z_hinge), rpy=(0.0, -down, 0.0)), axis=(0.0, 1.0, 0.0),
                       motion_limits=MotionLimits(lower=0.0, upper=1.20, effort=5.0, velocity=1.0))
    return ramp.name


def build_seeded_rabbit_hutch(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_rabbit_hutch(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _art(model, name):
    """Return the named articulation or None (get_articulation raises on miss)."""
    for a in model.articulations:
        if a.name == name:
            return a
    return None


def _allow_captures(ctx, model, r, info) -> None:
    frame = model.get_part("hutch_frame")
    # Door hinge leaves / knuckles nest against frame receivers.
    for door_name, _h in info["doors"]:
        door = model.get_part(door_name)
        if door is None:
            continue
        ctx.allow_overlap(frame, door, reason="Door hinge knuckles/leaves interleave with the frame hinge receiver at the pivot; the door swings clear on positive articulation.")
    # Grid latch pivot pins captured in the door pivot plate.
    for door_name, latch_name in info["latched_doors"]:
        door = model.get_part(door_name)
        latch = model.get_part(latch_name)
        if door is None or latch is None:
            continue
        ctx.allow_overlap(door, latch, reason="Latch pivot pin captured inside the door pivot plate (captured-pin hasp).")
    # Casters: wheel captured between forks.
    for wname in info["casters"]:
        wheel = model.get_part(wname)
        if wheel is not None:
            ctx.allow_overlap(frame, wheel, reason="Caster wheel is captured on its axle between the two fixed forks.")
    # Ramp hinge rod captured in the frame receiver/plate.
    if info["ramp"] is not None:
        ramp = model.get_part(info["ramp"])
        if ramp is not None:
            ctx.allow_overlap(frame, ramp, reason="Ramp hinge rod is a captured pin seated against the frame hinge receiver; the board shares the base-rail pivot line at rest and drops away on articulation.")
    # Pop-hole panel captured behind guides/trim.
    if info["pop"] is not None:
        pop = model.get_part(info["pop"])
        if pop is not None:
            ctx.allow_overlap(frame, pop, reason="The guillotine slide panel and its pull bracket are intentionally captured behind the pop-hole trim/guide channels through their full travel.")
    # Tray rests on its runners.
    tray = model.get_part(info["tray"]) if info["tray"] else None
    if tray is not None and info["tray_runners"]:
        ctx.allow_overlap(frame, tray, reason="The slide-out tray rests on its fixed runner rails (sliding contact).")


def run_rabbit_hutch_tests(object_model: ArticulatedObject, config: RabbitHutchConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    info = object_model.meta.get("hutch_info", {})

    _allow_captures(ctx, object_model, r, info)

    roof_name = info.get("roof_lid")
    if roof_name:
        ctx.allow_isolated_part(
            object_model.get_part(roof_name),
            reason="roof lid lifts off the hutch and loses frame contact",
        )

    # ---- Identity: raised hutch with an enclosed compartment + opening access + tray. ----
    frame = object_model.get_part("hutch_frame")
    ctx.check(
        "rabbit hutch has a frame, at least one door and a slide-out tray",
        frame is not None
        and len(info.get("doors", [])) >= 1
        and info.get("tray") is not None
        and object_model.get_part(info["tray"]) is not None,
        details=f"doors={[d for d, _ in info.get('doors', [])]}, tray={info.get('tray')}",
    )
    faabb = ctx.part_world_aabb(frame)
    ctx.check(
        "frame stands at a raised hutch height",
        faabb is not None and (faabb[1][2] - faabb[0][2]) > 0.30,
        details=f"frame_aabb={faabb}",
    )

    # ---- Targeted mechanism poses (one per key mechanism family present). ----
    # A compartment door opens outward toward -Y.
    if info.get("doors"):
        dname = info["doors"][0][0]
        door = object_model.get_part(dname)
        dj = _art(object_model, f"frame_to_{dname}")
        if door is not None and dj is not None:
            rest = ctx.part_world_aabb(door)
            with ctx.pose({dj: 0.9}):
                openp = ctx.part_world_aabb(door)
            ctx.check(
                "compartment door opens outward (-Y)",
                rest is not None and openp is not None and openp[0][1] < rest[0][1] - 0.05,
                details=f"rest={rest}, open={openp}",
            )

    # Roof lid lifts up.
    if info.get("roof_lid"):
        roof = object_model.get_part(info["roof_lid"])
        rj = _art(object_model, "frame_to_roof_lid")
        if roof is not None and rj is not None:
            rest = ctx.part_world_aabb(roof)
            with ctx.pose({rj: 0.75}):
                up = ctx.part_world_aabb(roof)
            ctx.check("roof lid lifts upward", rest is not None and up is not None and up[1][2] > rest[1][2] + 0.10, details=f"rest={rest}, up={up}")

    # Latch hasp lifts on its pivot.
    if info.get("latched_doors"):
        _dn, lname = info["latched_doors"][0]
        latch = object_model.get_part(lname)
        lj = _art(object_model, f"{_dn}_to_latch")
        if latch is not None and lj is not None:
            rest = ctx.part_world_aabb(latch)
            with ctx.pose({lj: 0.8}):
                lifted = ctx.part_world_aabb(latch)
            ctx.check("latch hasp pivots on its joint", rest is not None and lifted is not None and lifted[0][2] < rest[0][2] - 0.03, details=f"rest={rest}, moved={lifted}")

    # Tray slides out toward -Y.
    tray = object_model.get_part(info["tray"]) if info.get("tray") else None
    tj = _art(object_model, "frame_to_floor_tray") or _art(object_model, "frame_to_cleaning_tray")
    if tray is not None and tj is not None:
        rest = ctx.part_world_aabb(tray)
        with ctx.pose({tj: min(r.tray_travel, 0.28)}):
            out = ctx.part_world_aabb(tray)
        ctx.check("tray slides out toward the front (-Y)", rest is not None and out is not None and out[0][1] < rest[0][1] - 0.15, details=f"rest={rest}, out={out}")

    # Drop ramp folds up.
    if info.get("ramp"):
        ramp = object_model.get_part(info["ramp"])
        rj = _art(object_model, "frame_to_front_ramp")
        if ramp is not None and rj is not None:
            rest = ctx.part_world_aabb(ramp)
            with ctx.pose({rj: 1.0}):
                up = ctx.part_world_aabb(ramp)
            ctx.check("front ramp folds upward", rest is not None and up is not None and up[1][2] > rest[1][2] + 0.10, details=f"rest={rest}, up={up}")

    # Guillotine pop-hole lifts on +Z.
    if info.get("pop"):
        pop = object_model.get_part(info["pop"])
        pj = _art(object_model, "frame_to_pop_hole_door")
        if pop is not None and pj is not None:
            rest = ctx.part_world_aabb(pop)
            with ctx.pose({pj: 0.20}):
                up = ctx.part_world_aabb(pop)
            ctx.check("guillotine pop-hole door lifts upward", rest is not None and up is not None and up[0][2] > rest[0][2] + 0.12, details=f"rest={rest}, up={up}")

    # Caster spins (CONTINUOUS).
    if info.get("casters"):
        cj = _art(object_model, "fork_to_caster_wheel_0")
        if cj is not None:
            ctx.check("caster wheel joint is CONTINUOUS +X", cj.articulation_type == ArticulationType.CONTINUOUS and abs(cj.axis[0]) > 0.99, details=f"type={cj.articulation_type}, axis={cj.axis}")

    # ---- Rule 5: full-travel non-穿模 across sampled joint poses. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=28, ignore_fixed=True)

    # ---- Compiler-owned baseline (also enforced by the sweep). ----
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    return ctx.report()


__all__ = [
    "BodyForm",
    "Mobility",
    "FrontAccess",
    "Palette",
    "RabbitHutchConfig",
    "ResolvedRabbitHutchConfig",
    "build_rabbit_hutch",
    "build_seeded_rabbit_hutch",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_rabbit_hutch_tests",
]
