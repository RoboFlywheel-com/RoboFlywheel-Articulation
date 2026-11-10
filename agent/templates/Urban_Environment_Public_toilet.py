# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Procedural template: PUBLIC TOILET (portable porta-potty cabin / block).
#
# Axes (sourced from the porta-potty parent + 12 qwen-forked workbench variants
# in articraft_data: roof_gable/domed/flat, walls_corrugated/smooth, door_window,
# vent_twin, utility_handwash, base_skid, accessible_wide, tall_narrow, ...):
#   - roof:        sloped / gable / domed / flat          (Slot A, 4)
#   - walls:       ribbed / corrugated / smooth           (Slot B, 3)
#   - utility:     corner_stack / twin_stack / roof_unit  (Slot C, 3)
#   - door:        louvered / window                      (per-cabin, 2)
#   - cabin_count: 1..4 cabins in a row (multiplicity; each cabin has a door)
#   - footprint width/height scale; palette
#
# Conventions (meters, Z-up): each cabin's DOOR is on the front (+X) face and
# swings on a VERTICAL (+Z) hinge at a front corner. Cabins tile along +Y. The
# block (all cabin shells) is the grounded root; each door is a REVOLUTE child.

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

RoofModule = Literal["sloped", "gable", "domed", "flat"]
WallsModule = Literal["ribbed", "corrugated", "smooth"]
UtilityModule = Literal["corner_stack", "twin_stack", "roof_unit"]
DoorModule = Literal["louvered", "window"]
PaletteTheme = Literal["magenta", "blue", "green", "gray", "sand"]

ROOF_MODULES: tuple[RoofModule, ...] = ("sloped", "gable", "domed", "flat")
WALLS_MODULES: tuple[WallsModule, ...] = ("ribbed", "corrugated", "smooth")
UTILITY_MODULES: tuple[UtilityModule, ...] = ("corner_stack", "twin_stack", "roof_unit")
DOOR_MODULES: tuple[DoorModule, ...] = ("louvered", "window")
PALETTE_THEMES: tuple[PaletteTheme, ...] = ("magenta", "blue", "green", "gray", "sand")

CABIN_MIN, CABIN_MAX = 1, 15

PALETTES: dict[PaletteTheme, dict[str, tuple[float, float, float, float]]] = {
    "magenta": {"body": (0.74, 0.10, 0.30, 1.0), "body_dark": (0.57, 0.07, 0.22, 1.0)},
    "blue": {"body": (0.13, 0.34, 0.62, 1.0), "body_dark": (0.09, 0.24, 0.46, 1.0)},
    "green": {"body": (0.16, 0.46, 0.30, 1.0), "body_dark": (0.10, 0.34, 0.21, 1.0)},
    "gray": {"body": (0.55, 0.57, 0.60, 1.0), "body_dark": (0.40, 0.42, 0.45, 1.0)},
    "sand": {"body": (0.80, 0.71, 0.50, 1.0), "body_dark": (0.62, 0.54, 0.36, 1.0)},
}
_COMMON = {
    "roof_white": (0.90, 0.90, 0.88, 0.95),
    "dark": (0.11, 0.11, 0.13, 1.0),
    "vent_white": (0.85, 0.85, 0.84, 1.0),
    "glass": (0.35, 0.55, 0.68, 0.6),
    "indicator": (0.85, 0.18, 0.16, 1.0),
    "chrome": (0.80, 0.82, 0.85, 1.0),
}

# ---- Base dimensions ---------------------------------------------------------
W = 1.16
D = 1.16
WALL_T = 0.035
FLOOR_H = 0.12
WALL_BASE = FLOOR_H
WALL_TOP = 2.18
ROOF_T = 0.06
RIB_COUNT = 7
DOOR_GAP = 0.006
OPEN_ANGLE = math.radians(100.0)


def _clampi(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))


def _clampf(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


@dataclass(frozen=True)
class PublicToiletConfig:
    roof_module: RoofModule = "sloped"
    walls_module: WallsModule = "ribbed"
    utility_module: UtilityModule = "corner_stack"
    door_module: DoorModule = "louvered"
    palette_theme: PaletteTheme = "magenta"
    cabin_count: int = 1
    width_scale: float = 1.0
    height_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedPublicToiletConfig:
    roof_module: RoofModule
    walls_module: WallsModule
    utility_module: UtilityModule
    door_module: DoorModule
    palette_theme: PaletteTheme
    cabin_count: int
    w: float          # scaled footprint x
    d: float          # scaled footprint y
    wall_top: float   # scaled wall height
    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> PublicToiletConfig:
    rng = random.Random(seed)
    return PublicToiletConfig(
        roof_module=rng.choice(ROOF_MODULES),
        walls_module=rng.choice(WALLS_MODULES),
        utility_module=rng.choice(UTILITY_MODULES),
        door_module=rng.choice(DOOR_MODULES),
        palette_theme=rng.choice(PALETTE_THEMES),
        cabin_count=rng.randint(CABIN_MIN, CABIN_MAX),
        width_scale=round(rng.uniform(0.9, 1.35), 4),   # accessible-wide reaches up
        height_scale=round(rng.uniform(0.92, 1.10), 4),
    )


def resolve_config(config: PublicToiletConfig) -> ResolvedPublicToiletConfig:
    def pick(v, opts, default):
        return v if v in opts else default

    palette_theme = pick(config.palette_theme, PALETTES, "magenta")
    wfp = _clampf(config.width_scale, 0.85, 1.45)
    hfp = _clampf(config.height_scale, 0.85, 1.18)
    return ResolvedPublicToiletConfig(
        roof_module=pick(config.roof_module, ROOF_MODULES, "sloped"),
        walls_module=pick(config.walls_module, WALLS_MODULES, "ribbed"),
        utility_module=pick(config.utility_module, UTILITY_MODULES, "corner_stack"),
        door_module=pick(config.door_module, DOOR_MODULES, "louvered"),
        palette_theme=palette_theme,
        cabin_count=_clampi(config.cabin_count, CABIN_MIN, CABIN_MAX),
        w=W * wfp,
        d=D * wfp,
        wall_top=WALL_TOP * hfp,
        palette={**PALETTES[palette_theme], **_COMMON},
    )


# ---------------------------------------------------------------------------
# Geometry helpers (ported from the porta-potty parent; Box/Cylinder only)
# ---------------------------------------------------------------------------
def _wall(part, r, *, face, span, z0, z1, cx, cy, mat, rib_mat, mode, name_prefix):
    """One wall panel on the given outer face, with rib/corrugation/smooth skin."""
    w, d = r.w, r.d
    h = z1 - z0
    zc = 0.5 * (z0 + z1)
    if face in ("+x", "-x"):
        sign = 1.0 if face == "+x" else -1.0
        x = cx + sign * (w * 0.5 - WALL_T * 0.5)
        part.visual(Box((WALL_T, span, h)), origin=Origin(xyz=(x, cy, zc)), material=mat, name=f"{name_prefix}_panel", material_class_id="plastic.opaque_glossy_molded")
        sx = cx + sign * (w * 0.5 + 0.004)
        if mode == "ribbed":
            for i in range(RIB_COUNT):
                y = cy - span * 0.5 + span * (i + 0.5) / RIB_COUNT
                part.visual(Box((0.016, 0.024, h * 0.94)), origin=Origin(xyz=(sx, y, zc)), material=rib_mat, name=f"{name_prefix}_rib_{i}", material_class_id="plastic.opaque_glossy_molded")
        elif mode == "corrugated":
            for i in range(6):
                z = z0 + h * (i + 0.5) / 6.0
                part.visual(Box((0.018, span * 0.96, 0.02)), origin=Origin(xyz=(sx, cy, z)), material=rib_mat, name=f"{name_prefix}_flute_{i}", material_class_id="plastic.opaque_glossy_molded")
        else:  # smooth -> a flush recessed framing border
            part.visual(Box((0.010, span * 0.86, h * 0.86)), origin=Origin(xyz=(sx, cy, zc)), material=rib_mat, name=f"{name_prefix}_frame", material_class_id="plastic.opaque_glossy_molded")
    else:
        sign = 1.0 if face == "+y" else -1.0
        y = cy + sign * (d * 0.5 - WALL_T * 0.5)
        part.visual(Box((span, WALL_T, h)), origin=Origin(xyz=(cx, y, zc)), material=mat, name=f"{name_prefix}_panel", material_class_id="plastic.opaque_glossy_molded")
        sy = cy + sign * (d * 0.5 + 0.004)
        if mode == "ribbed":
            for i in range(RIB_COUNT):
                x = cx - span * 0.5 + span * (i + 0.5) / RIB_COUNT
                part.visual(Box((0.024, 0.016, h * 0.94)), origin=Origin(xyz=(x, sy, zc)), material=rib_mat, name=f"{name_prefix}_rib_{i}", material_class_id="plastic.opaque_glossy_molded")
        elif mode == "corrugated":
            for i in range(6):
                z = z0 + h * (i + 0.5) / 6.0
                part.visual(Box((span * 0.96, 0.018, 0.02)), origin=Origin(xyz=(cx, sy, z)), material=rib_mat, name=f"{name_prefix}_flute_{i}", material_class_id="plastic.opaque_glossy_molded")
        else:
            part.visual(Box((span * 0.86, 0.010, h * 0.86)), origin=Origin(xyz=(cx, sy, zc)), material=rib_mat, name=f"{name_prefix}_frame", material_class_id="plastic.opaque_glossy_molded")


def _roof(part, r, *, cx, cy, mat, name_prefix):
    """Roof cap per roof_module. Returns the crown z (for roof-mounted utility)."""
    w, d, wt = r.w, r.d, r.wall_top
    span_y = d + 0.06
    rm = r.roof_module
    if rm == "flat":
        part.visual(Box((w + 0.08, d + 0.08, ROOF_T)), origin=Origin(xyz=(cx, cy, wt + ROOF_T * 0.5)), material=mat, name=f"{name_prefix}_flat", material_class_id="plastic.opaque_glossy_molded")
        return wt + ROOF_T
    if rm == "sloped":
        pitch = math.atan2(0.16 * (wt / WALL_TOP), w)
        part.visual(Box((w + 0.08, d + 0.08, ROOF_T)), origin=Origin(xyz=(cx, cy, wt + 0.08), rpy=(0.0, pitch, 0.0)), material=mat, name=f"{name_prefix}_slab", material_class_id="plastic.opaque_glossy_molded")
        return wt + 0.16
    if rm == "gable":
        ridge = wt + 0.28
        for s, sl in ((1.0, "p"), (-1.0, "m")):
            pitch = math.atan2(0.28, w * 0.5)
            part.visual(Box((math.hypot(w * 0.5, 0.28) + 0.05, d + 0.08, ROOF_T)),
                        origin=Origin(xyz=(cx + s * w * 0.25, cy, wt + 0.14), rpy=(0.0, -s * pitch, 0.0)),
                        material=mat, name=f"{name_prefix}_gable_{sl}", material_class_id="plastic.opaque_glossy_molded")
        return ridge
    # domed (barrel vault) — ported _curved_roof
    n = 12
    a = w * 0.5
    sagitta = 0.18
    radius = (a * a + sagitta * sagitta) / (2.0 * sagitta)
    xc = -0.12
    front_dx = abs(w * 0.5 - xc)
    front_drop = radius - math.sqrt(radius * radius - front_dx * front_dx)
    z_top = wt + front_drop + 0.04
    step = w / n
    crown_z = z_top
    for s in range(n):
        x = -w * 0.5 + (s + 0.5) * step
        dx = x - xc
        root = math.sqrt(radius * radius - dx * dx)
        z = z_top - (radius - root)
        beta = math.atan2(dx, root)
        part.visual(Box((step / math.cos(beta) * 1.18, span_y, ROOF_T)),
                    origin=Origin(xyz=(cx + x, cy, z + ROOF_T * 0.5 * math.cos(beta)), rpy=(0.0, beta, 0.0)),
                    material=mat, name=f"{name_prefix}_seg_{s}", material_class_id="plastic.opaque_glossy_molded")
        if abs(dx) < step:
            crown_z = z
    return crown_z


def _utility(part, r, *, cx, cy, crown_z, mats, name_prefix):
    """Vent / utility module on a cabin."""
    body, body_dark, roof_white, dark, vent_white, glass, chrome = mats
    w, d, wt = r.w, r.d, r.wall_top
    um = r.utility_module
    if um == "corner_stack":
        stacks = [(-w * 0.5 + 0.12, d * 0.5 - 0.12)]
    elif um == "twin_stack":
        stacks = [(-w * 0.5 + 0.12, d * 0.5 - 0.12), (-w * 0.5 + 0.12, -d * 0.5 + 0.12)]
    else:  # roof_unit -> a molded roof utility box rising from the flat eave
        # (its base sits on the wall-top eave so it is always supported, then
        # pokes up through the roof cap regardless of roof shape).
        part.visual(Box((0.30, 0.30, 0.24)), origin=Origin(xyz=(cx - w * 0.18, cy, wt + 0.12)), material=vent_white, name=f"{name_prefix}_roof_unit", material_class_id="plastic.opaque_glossy_molded")
        stacks = [(-w * 0.5 + 0.12, d * 0.5 - 0.12)]
    for i, (sx, sy) in enumerate(stacks):
        top = wt + 0.30
        part.visual(Cylinder(radius=0.05, length=top), origin=Origin(xyz=(cx + sx, cy + sy, top * 0.5)), material=dark, name=f"{name_prefix}_stack_{i}", material_class_id="plastic.opaque_generic")
        part.visual(Cylinder(radius=0.066, length=0.04), origin=Origin(xyz=(cx + sx, cy + sy, top + 0.01)), material=dark, name=f"{name_prefix}_stack_cap_{i}", material_class_id="plastic.opaque_generic")


def _build_cabin_shell(part, r, *, cx, cy, mats, idx):
    body, body_dark, roof_white, dark, vent_white, glass, chrome = mats
    w, d, wt = r.w, r.d, r.wall_top
    p = f"c{idx}"
    # floor pan + skids
    part.visual(Box((w, d, FLOOR_H)), origin=Origin(xyz=(cx, cy, FLOOR_H * 0.5)), material=body_dark, name=f"{p}_floor", material_class_id="plastic.opaque_glossy_molded")
    for sy in (1.0, -1.0):
        part.visual(Box((w + 0.02, 0.12, 0.04)), origin=Origin(xyz=(cx, cy + sy * (d * 0.5 - 0.12), 0.02)), material=dark, name=f"{p}_skid_{'p' if sy>0 else 'm'}", material_class_id="metal.paint_coated")
    # three walls (sides + back); front is the door opening
    _wall(part, r, face="+y", span=d - 2 * WALL_T, z0=WALL_BASE, z1=wt, cx=cx, cy=cy, mat=body, rib_mat=body_dark, mode=r.walls_module, name_prefix=f"{p}_wl")
    _wall(part, r, face="-y", span=d - 2 * WALL_T, z0=WALL_BASE, z1=wt, cx=cx, cy=cy, mat=body, rib_mat=body_dark, mode=r.walls_module, name_prefix=f"{p}_wr")
    _wall(part, r, face="-x", span=d - 2 * WALL_T, z0=WALL_BASE, z1=wt, cx=cx, cy=cy, mat=body, rib_mat=body_dark, mode=r.walls_module, name_prefix=f"{p}_wb")
    # front header + corner jambs (frame for the door)
    header_h = 0.12
    part.visual(Box((WALL_T, d - 2 * WALL_T, header_h)), origin=Origin(xyz=(cx + w * 0.5 - WALL_T * 0.5, cy, wt - header_h * 0.5)), material=body, name=f"{p}_header", material_class_id="plastic.opaque_glossy_molded")
    for sy in (1.0, -1.0):
        part.visual(Box((WALL_T, 0.05, wt - WALL_BASE)), origin=Origin(xyz=(cx + w * 0.5 - WALL_T * 0.5, cy + sy * (d * 0.5 - WALL_T - 0.025), WALL_BASE + (wt - WALL_BASE) * 0.5)), material=body, name=f"{p}_jamb_{'p' if sy>0 else 'm'}", material_class_id="plastic.opaque_glossy_molded")
    # eave + roof + utility
    part.visual(Box((w + 0.08, d + 0.08, 0.03)), origin=Origin(xyz=(cx, cy, wt - 0.005)), material=roof_white, name=f"{p}_eave", material_class_id="plastic.opaque_glossy_molded")
    crown_z = _roof(part, r, cx=cx, cy=cy, mat=roof_white, name_prefix=f"{p}_roof")
    _utility(part, r, cx=cx, cy=cy, crown_z=crown_z, mats=mats, name_prefix=p)


def _build_door(model, r, block, *, cx, cy, mats, idx):
    body, body_dark, roof_white, dark, vent_white, glass, chrome = mats
    w, d, wt = r.w, r.d, r.wall_top
    door = model.part(f"door_{idx}")
    door_w = (d - 2 * WALL_T) - 2 * DOOR_GAP
    door_z0 = WALL_BASE + DOOR_GAP
    door_z1 = wt - 0.12 - DOOR_GAP
    leaf_cy = -door_w * 0.5
    door_h = door_z1 - door_z0
    door_zc = 0.5 * (door_z0 + door_z1)
    door.visual(Box((0.045, door_w, door_h)), origin=Origin(xyz=(0.0, leaf_cy, door_zc)), material=body, name="door_leaf", material_class_id="plastic.opaque_glossy_molded")
    # Hinge stile runs down to the floor (z=0) so the door child geometry
    # contains the hinge-joint origin (origin-distance gate).
    door.visual(Cylinder(radius=0.026, length=door_z1), origin=Origin(xyz=(0.0, 0.010, door_z1 * 0.5)), material=dark, name="hinge_stile", material_class_id="metal.blackened_gunmetal")
    if r.door_module == "window":
        door.visual(Box((0.05, door_w * 0.55, door_h * 0.34)), origin=Origin(xyz=(0.028, leaf_cy, door_zc + door_h * 0.18)), material=glass, name="door_window", material_class_id="glass.clear_transparent")
    else:  # louvered vent slats near the top
        for s in range(4):
            door.visual(Box((0.018, door_w * 0.62, 0.014)), origin=Origin(xyz=(0.028, leaf_cy, door_z1 - 0.06 - s * 0.026)), material=dark, name=f"door_vent_slat_{s}", material_class_id="plastic.opaque_glossy_molded")
    # occupancy indicator + handle on the free (-Y) edge
    latch_y = -door_w + 0.05
    door.visual(Box((0.03, 0.05, 0.09)), origin=Origin(xyz=(0.030, latch_y, door_zc + 0.18)), material="indicator", name="occupancy_indicator", appearance_only=AppearanceOnlySpec(kind="overlay"))
    door.visual(Box((0.05, 0.028, 0.13)), origin=Origin(xyz=(0.038, latch_y, door_zc)), material=dark, name="door_handle", material_class_id="metal.blackened_gunmetal")
    door.inertial = Inertial.from_geometry(Box((0.05, door_w, door_h)), mass=13.0, origin=Origin(xyz=(0.0, leaf_cy, door_zc)))
    hinge_y = cy + (d * 0.5 - WALL_T - DOOR_GAP)
    hinge_x = cx + (w * 0.5 - WALL_T - 0.004)
    model.articulation(
        f"cabin_{idx}_to_door", ArticulationType.REVOLUTE, parent=block, child=door,
        origin=Origin(xyz=(hinge_x, hinge_y, 0.0)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=35.0, velocity=1.5, lower=0.0, upper=OPEN_ANGLE),
    )


def build_public_toilet(config: PublicToiletConfig, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="public_toilet", assets=assets)
    P = r.palette
    mats = (
        model.material("body", rgba=P["body"]),
        model.material("body_dark", rgba=P["body_dark"]),
        model.material("roof_white", rgba=P["roof_white"]),
        model.material("dark", rgba=P["dark"]),
        model.material("vent_white", rgba=P["vent_white"]),
        model.material("glass", rgba=P["glass"]),
        model.material("chrome", rgba=P["chrome"]),
    )
    model.material("indicator", rgba=P["indicator"])
    block = model.part("block")
    n = r.cabin_count
    cys = [i * r.d for i in range(n)]
    for i, cy in enumerate(cys):
        _build_cabin_shell(block, r, cx=0.0, cy=cy, mats=mats, idx=i)
    block.inertial = Inertial.from_geometry(
        Box((r.w, max(r.d, n * r.d), r.wall_top)), mass=85.0 * n,
        origin=Origin(xyz=(0.0, (n - 1) * r.d * 0.5, r.wall_top * 0.45)),
    )
    for i, cy in enumerate(cys):
        _build_door(model, r, block, cx=0.0, cy=cy, mats=mats, idx=i)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_public_toilet(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_public_toilet(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedPublicToiletConfig) -> list[tuple[str, str]]:
    return [
        ("roof", r.roof_module),
        ("walls", r.walls_module),
        ("utility", r.utility_module),
        ("door", r.door_module),
        ("cabins", f"n{r.cabin_count}"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def run_public_toilet_tests(object_model: ArticulatedObject, config: PublicToiletConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    block = object_model.get_part("block")
    names = {p.name for p in object_model.parts}
    ctx.check("block_present", "block" in names, "missing block")
    ctx.check("cabin_count_doors", sum(1 for nm in names if nm.startswith("door_")) == r.cabin_count, f"expected {r.cabin_count} doors")
    for i in range(r.cabin_count):
        door = object_model.get_part(f"door_{i}")
        j = object_model.get_articulation(f"cabin_{i}_to_door")
        ctx.check(f"door_{i}_revolute_z", j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99 and abs(j.motion_limits.lower) < 1e-9, f"door {i} must be a vertical revolute opening from closed")
        ctx.allow_overlap(door, block, reason=f"Closed door {i} leaf + hinge stile seat in the cabin front frame; pose-invariant at the hinge.")
    return ctx.report()


__all__ = [
    "PublicToiletConfig",
    "ResolvedPublicToiletConfig",
    "config_from_seed",
    "resolve_config",
    "build_public_toilet",
    "build_seeded_public_toilet",
    "slot_choices_for_seed",
    "run_public_toilet_tests",
]
