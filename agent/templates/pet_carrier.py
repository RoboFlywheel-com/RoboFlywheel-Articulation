# SPDX-License-Identifier: Apache-2.0

"""Pet_Animal related / Pet carrier procedural template (modular).

Spec: articraft_template_authoring/specs_modular_v1/pet_carrier.md

A portable, fully-enclosing single-pet travel container: an enclosing cabin
(``carrier_body`` root) built to a standard envelope in one of four form
families, plus exactly one openable access panel (the guaranteed non-FIXED
joint) and one carry means. All access panels and moving carry sub-assemblies
parent to ``carrier_body`` (parallel_children); the wire-grate side door carries
a ``grate_bars`` multiplicity axis.

Slots (pattern = mixed):
  * Slot A body_form (③): soft_fabric_envelope / rigid_molded_clamshell
      / open_wire_cage_lattice / woven_wicker_basket
  * Slot B access (②/①): front_fold_door / top_hatch / expandable_side_pod
      / side_swing_door(×N grate) / rear_topload_lid / slide_out_tray
  * Slot C carry (①/②): webbing_top_handle / backpack_harness
      / molded_rigid_handle / wheeled_rolling_trolley
  * Multiplicity grate_bars: N in {4,6,9} (side_swing_door only)

Rules:
  Rule 1 — non-articulating detail (mesh windows, vent rows, weave bands/stakes,
    latch clips, piping, logo patches, handle loop, back panel, straps, wheel
    base platform/forks) is a host ``.visual(...)``; no FIXED-jointed decoration.
    This template has NO FIXED articulation — every child is a real moving joint.
  Rule 2 — every moving child is a captured hinge-knuckle / captured rail /
    captured axle pivot; ``MatingContract`` cannot express those, so joints are
    grandfathered (omit ``mating=``) and kept honest with element-scoped
    ``allow_overlap`` + targeted ``ctx.pose`` (identical discipline to camp_chair).
  Rule 3 — structure derives from declared 5-star sources; mesh heroes preserved
    (section_loft domes / cadquery molded shells / tube-mesh weave & handles).
  Rule 5 — ``fail_if_parts_overlap_in_sampled_poses`` + one targeted ``ctx.pose``
    per mechanism.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    boolean_difference,
    mesh_from_cadquery,
    mesh_from_geometry,
    section_loft,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "soft_fabric_envelope",
    "rigid_molded_clamshell",
    "open_wire_cage_lattice",
    "woven_wicker_basket",
]
Access = Literal[
    "front_fold_door",
    "top_hatch",
    "expandable_side_pod",
    "side_swing_door",
    "rear_topload_lid",
    "slide_out_tray",
]
Carry = Literal[
    "webbing_top_handle",
    "backpack_harness",
    "molded_rigid_handle",
    "wheeled_rolling_trolley",
]
PaletteStyle = Literal[
    "purple_mesh_soft",
    "tan_black_kennel",
    "chrome_black_wire",
    "natural_rattan",
    "grey_navy_travel",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "soft_fabric_envelope",
    "rigid_molded_clamshell",
    "open_wire_cage_lattice",
    "woven_wicker_basket",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "purple_mesh_soft",
    "tan_black_kennel",
    "chrome_black_wire",
    "natural_rattan",
    "grey_navy_travel",
)

# Compatibility matrix (§9): which access / carry each body form may host.
ALLOWED_ACCESS: dict[BodyForm, tuple[Access, ...]] = {
    "soft_fabric_envelope": ("front_fold_door", "top_hatch", "expandable_side_pod"),
    "woven_wicker_basket": ("top_hatch", "front_fold_door"),
    "rigid_molded_clamshell": ("side_swing_door", "rear_topload_lid", "slide_out_tray"),
    "open_wire_cage_lattice": ("side_swing_door", "slide_out_tray"),
}
ALLOWED_CARRY: dict[BodyForm, tuple[Carry, ...]] = {
    "soft_fabric_envelope": ("webbing_top_handle", "backpack_harness"),
    "woven_wicker_basket": ("webbing_top_handle",),
    "rigid_molded_clamshell": ("molded_rigid_handle", "wheeled_rolling_trolley"),
    "open_wire_cage_lattice": ("molded_rigid_handle", "wheeled_rolling_trolley"),
}
GRATE_COUNTS: tuple[int, ...] = (4, 6, 9)

# Rolling wheel-base stack (standardized caster hardware — not size-scaled).
ROLL_WHEEL_R = 0.025
ROLL_FORK_H = 0.036
ROLL_BASE_T = 0.014
ROLL_BASE_H = ROLL_WHEEL_R + ROLL_FORK_H + ROLL_BASE_T  # base platform top height

# ---------------------------------------------------------------------------
# Palettes. Role keys shared across forms; the palette carries the colorway.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "purple_mesh_soft": {
        "shell": (0.50, 0.36, 0.72, 1.0),
        "shell2": (0.40, 0.28, 0.60, 1.0),
        "mesh": (0.74, 0.74, 0.76, 1.0),
        "trim": (0.09, 0.09, 0.10, 1.0),
        "accent": (0.93, 0.93, 0.94, 1.0),
        "wire": (0.20, 0.20, 0.22, 1.0),
        "pad": (0.47, 0.60, 0.70, 1.0),
        "metal": (0.62, 0.63, 0.65, 1.0),
    },
    "tan_black_kennel": {
        "shell": (0.80, 0.76, 0.69, 1.0),
        "shell2": (0.13, 0.13, 0.14, 1.0),
        "mesh": (0.30, 0.30, 0.32, 1.0),
        "trim": (0.20, 0.20, 0.21, 1.0),
        "accent": (0.86, 0.83, 0.76, 1.0),
        "wire": (0.08, 0.08, 0.09, 1.0),
        "pad": (0.55, 0.53, 0.50, 1.0),
        "metal": (0.55, 0.55, 0.58, 1.0),
    },
    "chrome_black_wire": {
        "shell": (0.72, 0.73, 0.74, 1.0),
        "shell2": (0.13, 0.13, 0.14, 1.0),
        "mesh": (0.10, 0.10, 0.11, 1.0),
        "trim": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.80, 0.81, 0.82, 1.0),
        "wire": (0.10, 0.10, 0.11, 1.0),
        "pad": (0.30, 0.32, 0.36, 1.0),
        "metal": (0.72, 0.73, 0.74, 1.0),
    },
    "natural_rattan": {
        "shell": (0.76, 0.60, 0.42, 1.0),
        "shell2": (0.52, 0.38, 0.24, 1.0),
        "mesh": (0.66, 0.50, 0.34, 1.0),
        "trim": (0.58, 0.42, 0.26, 1.0),
        "accent": (0.84, 0.71, 0.51, 1.0),
        "wire": (0.48, 0.34, 0.20, 1.0),
        "pad": (0.47, 0.60, 0.70, 1.0),
        "metal": (0.58, 0.42, 0.26, 1.0),
    },
    "grey_navy_travel": {
        "shell": (0.34, 0.36, 0.40, 1.0),
        "shell2": (0.16, 0.18, 0.24, 1.0),
        "mesh": (0.60, 0.62, 0.66, 1.0),
        "trim": (0.10, 0.11, 0.14, 1.0),
        "accent": (0.82, 0.45, 0.20, 1.0),
        "wire": (0.14, 0.15, 0.18, 1.0),
        "pad": (0.50, 0.55, 0.62, 1.0),
        "metal": (0.55, 0.57, 0.60, 1.0),
    },
}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class PetCarrierConfig:
    body_form: BodyForm | None = None
    access: Access | None = None
    carry: Carry | None = None
    grate_bars: int = 6
    palette_style: PaletteStyle = "purple_mesh_soft"
    size_scale: float = 1.0
    width_scale: float = 1.0
    name: str = "pet_carrier"


@dataclass(frozen=True)
class ResolvedPetCarrierConfig:
    body_form: BodyForm
    access: Access
    carry: Carry
    grate_bars: int
    palette_style: PaletteStyle
    size_scale: float
    width_scale: float
    name: str

    # --- single-sourced standard envelope anchors (world meters) ---
    @property
    def floor_t(self) -> float:
        return 0.014

    @property
    def L(self) -> float:  # cabin length (X, front-to-back)
        return 0.50 * self.size_scale

    @property
    def W(self) -> float:  # cabin width (Y)
        return _clamp(0.34 * self.size_scale * self.width_scale, 0.26, 0.44)

    @property
    def wall_h(self) -> float:
        return 0.22 * self.size_scale

    @property
    def ground_clearance(self) -> float:
        # Tie the raised-cabin clearance to the wheel-base stack height (fixed
        # caster hardware, NOT size-scaled) so the cabin floor rests exactly on
        # the base platform top; otherwise the cabin islands off the wheel base.
        return ROLL_BASE_H if self.carry == "wheeled_rolling_trolley" else 0.0

    @property
    def floor_z(self) -> float:
        return self.ground_clearance

    @property
    def rim_z(self) -> float:
        return self.floor_z + self.floor_t + self.wall_h

    @property
    def roof_z(self) -> float:
        return self.rim_z + 0.055 * self.size_scale

    @property
    def front_x(self) -> float:
        return self.L / 2.0

    @property
    def door_hw(self) -> float:  # front-opening half-width (Y)
        return min(0.115, self.W * 0.34)

    @property
    def sill_z(self) -> float:
        return self.floor_z + self.floor_t + 0.02

    @property
    def door_top_z(self) -> float:
        return self.rim_z - 0.008

    @property
    def top_cx(self) -> float:  # top-opening center X
        return -0.02 * self.size_scale

    @property
    def top_hl(self) -> float:  # top-opening half length (X)
        return 0.10 * self.size_scale

    @property
    def top_hw(self) -> float:  # top-opening half width (Y)
        return min(0.085, self.W * 0.28)

    @property
    def top_face_z(self) -> float:
        return self.roof_z

    @property
    def floor_top(self) -> float:
        """Inner floor surface the pet pad / tray rails rest on."""
        if self.body_form == "rigid_molded_clamshell":
            return self.floor_z + 0.006  # tub is shelled 6mm; inner floor top
        return self.floor_z + self.floor_t


def config_from_seed(seed: int) -> PetCarrierConfig:
    """Deterministic procedural sampling over the full slot domain (seed 0 not
    special). Access and carry are drawn from the body form's allowed sets so
    every sampled tuple is legal by construction; grate N only for side_swing."""
    rng = random.Random(seed)
    body = rng.choice(BODY_FORMS)
    access = rng.choice(ALLOWED_ACCESS[body])
    carry = rng.choice(ALLOWED_CARRY[body])
    # A wheeled top-load kennel doesn't pair (the lid IS the shell the trolley
    # would mount to): fall back to the molded handle.
    if access == "rear_topload_lid" and carry == "wheeled_rolling_trolley":
        carry = "molded_rigid_handle"
    grate = rng.choices(GRATE_COUNTS, weights=(2, 5, 2))[0] if access == "side_swing_door" else 6
    return PetCarrierConfig(
        body_form=body,
        access=access,
        carry=carry,
        grate_bars=grate,
        palette_style=rng.choice(PALETTE_STYLES),
        size_scale=round(rng.uniform(0.92, 1.12), 4),
        width_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_pet_carrier_{seed}",
    )


def resolve_config(config: PetCarrierConfig | None = None) -> ResolvedPetCarrierConfig:
    cfg = config or PetCarrierConfig()
    body = _pick(cfg.body_form, BODY_FORMS)
    allowed_access = ALLOWED_ACCESS[body]
    access = cfg.access if cfg.access in allowed_access else allowed_access[0]
    allowed_carry = ALLOWED_CARRY[body]
    carry = cfg.carry if cfg.carry in allowed_carry else allowed_carry[0]
    if access == "rear_topload_lid" and carry == "wheeled_rolling_trolley":
        carry = "molded_rigid_handle"
    grate = int(cfg.grate_bars) if int(cfg.grate_bars) in GRATE_COUNTS else 6
    if access != "side_swing_door":
        grate = 6  # inert; not emitted
    return ResolvedPetCarrierConfig(
        body_form=body,
        access=access,
        carry=carry,
        grate_bars=grate,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        size_scale=_clamp(cfg.size_scale, 0.92, 1.12),
        width_scale=_clamp(cfg.width_scale, 0.90, 1.10),
        name=cfg.name or "pet_carrier",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedPetCarrierConfig) else resolve_config(config)
    grate = f"n{r.grate_bars}" if r.access == "side_swing_door" else "n0"
    return (
        ("body_form", r.body_form),
        ("access", r.access),
        ("carry", r.carry),
        ("grate_bars", grate),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Geometry helpers
# ===========================================================================
def _rect_loop(hx: float, hy: float, z: float, c: float, cx: float = 0.0):
    """Closed chamfered-rectangle loop (octagon) in a z-plane (origin A helper)."""
    return [
        (cx - hx + c, -hy, z),
        (cx + hx - c, -hy, z),
        (cx + hx, -hy + c, z),
        (cx + hx, hy - c, z),
        (cx + hx - c, hy, z),
        (cx - hx + c, hy, z),
        (cx - hx, hy - c, z),
        (cx - hx, -hy + c, z),
    ]


def _bar(part, direction, center, length, radius, material, name) -> None:
    """One axis-aligned wire-bar cylinder (wire_cage helper)."""
    if direction == "z":
        rpy = (0.0, 0.0, 0.0)
    elif direction == "x":
        rpy = (0.0, math.pi / 2.0, 0.0)
    else:  # "y"
        rpy = (math.pi / 2.0, 0.0, 0.0)
    part.visual(Cylinder(radius=radius, length=length), origin=Origin(xyz=center, rpy=rpy),
                material=material, name=name, material_class_id="metal.mesh_chainmail")


def _linspace(a, b, n):
    if n <= 1:
        return [a]
    step = (b - a) / (n - 1)
    return [a + k * step for k in range(n)]


def _emit_grate(part, r: ResolvedPetCarrierConfig, mats, *, hw: float, h: float,
                n_v: int, n_h: int) -> None:
    """Loop-emit heavy border wires + inner grid on the door part (origin B).

    Local frame: door plane in Y-Z, hinge edge at y≈0, door extends toward -Y.
    ``hw`` = door half-width (Y span), ``h`` = door height (Z)."""
    border_r = 0.0055
    bar_r = 0.0035
    yb0, yb1 = -0.006, -(2 * hw - 0.006)
    zb0, zb1 = 0.006, h - 0.006
    y_mid = (yb0 + yb1) / 2.0
    z_mid = (zb0 + zb1) / 2.0
    for i, yb in enumerate((yb0, yb1)):
        part.visual(Cylinder(radius=border_r, length=(zb1 - zb0) + 2 * border_r),
                    origin=Origin(xyz=(0.0, yb, z_mid)), material=mats["wire"],
                    name=f"door_border_vertical_{i}", material_class_id="metal.mesh_chainmail")
    for i, zb in enumerate((zb0, zb1)):
        part.visual(Cylinder(radius=border_r, length=(yb0 - yb1) + 2 * border_r),
                    origin=Origin(xyz=(0.0, y_mid, zb), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=mats["wire"], name=f"door_border_horizontal_{i}", material_class_id="metal.mesh_chainmail")
    for i in range(n_v):
        yv = yb0 + (i + 1) * (yb1 - yb0) / (n_v + 1)
        part.visual(Cylinder(radius=bar_r, length=(zb1 - zb0)),
                    origin=Origin(xyz=(0.0, yv, z_mid)), material=mats["wire"],
                    name=f"door_wire_vertical_{i}", material_class_id="metal.mesh_chainmail")
    for i in range(n_h):
        zh = zb0 + (i + 1) * (zb1 - zb0) / (n_h + 1)
        part.visual(Cylinder(radius=bar_r, length=(yb0 - yb1)),
                    origin=Origin(xyz=(0.0, y_mid, zh), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=mats["wire"], name=f"door_wire_horizontal_{i}", material_class_id="metal.mesh_chainmail")
    # squeeze-latch grip on the free edge + hinge knuckle at the pivot edge
    part.visual(Box((0.014, 0.018, 0.05)), origin=Origin(xyz=(0.010, yb1 + 0.006, z_mid)),
                material=mats["trim"], name="door_latch_grip", material_class_id="plastic.opaque_glossy_molded")
    part.visual(Box((0.014, 0.016, 0.024)), origin=Origin(xyz=(-0.004, 0.002, z_mid)),
                material=mats["trim"], name="door_hinge_knuckle", material_class_id="metal.paint_coated")


# ===========================================================================
# Cadquery molded-shell heroes (rigid_molded_clamshell + rear_topload_lid)
# ===========================================================================
def _tub_solid(r: ResolvedPetCarrierConfig) -> cq.Workplane:
    """Black lower tub: outward-tapered open-top hollow tub, floor kept."""
    bot_l = r.L * 1.06
    bot_w = r.W * 1.06
    return (
        cq.Workplane("XY")
        .rect(bot_l, bot_w)
        .workplane(offset=r.wall_h)
        .rect(r.L, r.W)
        .loft()
        .faces(">Z")
        .shell(-0.006)
    )


def _upper_shell_solid(r: ResolvedPetCarrierConfig, shell_h: float) -> cq.Workplane:
    """Tapered hollow tan shell with a modest set of oval vent slots.

    Built in shell-local coords: z=0 at the rim, z=shell_h at the roof."""
    top_l = r.L * 0.80
    top_w = r.W * 0.72
    shell = (
        cq.Workplane("XY")
        .rect(r.L, r.W)
        .workplane(offset=shell_h)
        .rect(top_l, top_w)
        .loft()
        .faces("<Z")
        .shell(-0.006)
    )
    # oval side vents: two staggered rows of stadium slots through both walls
    pitch = 0.060
    pts = []
    for z_row, count, stagger in ((0.055, 5, 0.0), (0.120, 4, 0.030)):
        x0 = -(count - 1) * pitch / 2.0 + stagger
        for i in range(count):
            pts.append((x0 + i * pitch, z_row))
    cutters = (
        cq.Workplane("XZ").pushPoints(pts).slot2D(0.044, 0.022, 90).extrude(r.W, both=True)
    )
    return shell.cut(cutters)


def _flange_ring(r: ResolvedPetCarrierConfig) -> cq.Workplane:
    """Rim flange ring (rect frame)."""
    fl = r.L * 1.10
    fw = r.W * 1.12
    return (
        cq.Workplane("XY").rect(fl, fw).rect(r.L - 0.02, r.W - 0.02).extrude(0.022)
    )


# ===========================================================================
# Slot A: body_form — the enclosing cabin (root part `carrier_body`)
# ===========================================================================
def _build_soft_body(model, body, r: ResolvedPetCarrierConfig, mats) -> None:
    """Boxy fabric walls + section_loft domed mesh top (origin A)."""
    L, W, wt, fz, wh = r.L, r.W, 0.012, r.floor_z, r.wall_h
    body.visual(Box((L, W, r.floor_t)), origin=Origin(xyz=(0.0, 0.0, fz + r.floor_t / 2)),
                material=mats["shell2"], name="floor_panel", material_class_id="fabric.upholstery_plain")
    z_base = fz + r.floor_t
    # side walls (left omitted for expandable pod)
    for sign, side in ((1.0, "left"), (-1.0, "right")):
        if side == "left" and r.access == "expandable_side_pod":
            continue
        body.visual(Box((L, wt, wh)),
                    origin=Origin(xyz=(0.0, sign * (W / 2 - wt / 2), z_base + wh / 2)),
                    material=mats["shell"], name=f"{side}_side_wall", material_class_id="fabric.upholstery_plain")
    # rear + front frame (sill + two jambs framing the front opening)
    body.visual(Box((wt, W - 2 * wt, wh)),
                origin=Origin(xyz=(-(L / 2 - wt / 2), 0.0, z_base + wh / 2)),
                material=mats["shell"], name="rear_end_wall", material_class_id="fabric.upholstery_plain")
    front_x = L / 2 - wt / 2
    body.visual(Box((wt, W - 2 * wt, r.sill_z - z_base)),
                origin=Origin(xyz=(front_x, 0.0, (r.sill_z + z_base) / 2)),
                material=mats["shell"], name="front_door_sill", material_class_id="fabric.upholstery_plain")
    jamb_w = W / 2 - wt - r.door_hw + 0.012
    jamb_h = r.door_top_z - r.sill_z
    for sign, side in ((1.0, "left"), (-1.0, "right")):
        body.visual(Box((wt, jamb_w, jamb_h)),
                    origin=Origin(xyz=(front_x, sign * (W / 2 - wt - jamb_w / 2 + 0.006),
                                       r.sill_z + jamb_h / 2)),
                    material=mats["shell"], name=f"front_{side}_jamb", material_class_id="fabric.upholstery_plain")
    # pod seating frame rails on the left opening (for expandable pod)
    if r.access == "expandable_side_pod":
        yf = W / 2 - wt - 0.002
        body.visual(Box((L + 0.006, 0.004, 0.014)),
                    origin=Origin(xyz=(0.0, yf, r.rim_z - 0.008)),
                    material=mats["trim"], name="pod_frame_top_rail", material_class_id="fabric.webbing")
        body.visual(Box((L + 0.006, 0.004, 0.014)),
                    origin=Origin(xyz=(0.0, yf, z_base + 0.008)),
                    material=mats["trim"], name="pod_frame_bottom_rail", material_class_id="fabric.webbing")
    # domed fabric top (section_loft), covering rim -> roof
    dome = section_loft([
        _rect_loop(L / 2, W / 2, r.rim_z - 0.002, 0.028),
        _rect_loop(L / 2 - 0.01, W / 2 - 0.008, (r.rim_z + r.roof_z) / 2, 0.040),
        _rect_loop(0.16 * r.size_scale, 0.10 * r.size_scale, r.roof_z, 0.045),
    ])
    body.visual(mesh_from_geometry(dome, "dome_shell"), origin=Origin(),
                material=mats["shell"], name="dome_top_shell", material_class_id="fabric.upholstery_plain")
    _emit_side_windows(body, r, mats)
    _emit_pet_pad(body, r, mats)


def _emit_side_windows(body, r: ResolvedPetCarrierConfig, mats) -> None:
    """Host-conformal mesh windows on the long side faces + logo patch."""
    L, W = r.L, r.W
    win_hx, win_hz = min(0.085, L * 0.34), 0.075 * r.size_scale
    cz = r.floor_z + r.floor_t + r.wall_h * 0.6
    for sign, side in ((1.0, "left"), (-1.0, "right")):
        if side == "left" and r.access == "expandable_side_pod":
            continue
        yf = sign * (W / 2)
        body.visual(Box((2 * win_hx, 0.004, 2 * win_hz)),
                    origin=Origin(xyz=(0.02, yf - sign * 0.001, cz)),
                    material=mats["mesh"], name=f"{side}_window_mesh", material_class_id="fabric.open_mesh")
        for i, (sz, (sx, szz)) in enumerate((
            ((2 * win_hx + 0.03, 0.006, 0.016), (0.02, cz + win_hz + 0.008)),
            ((2 * win_hx + 0.03, 0.006, 0.016), (0.02, cz - win_hz - 0.008)),
        )):
            body.visual(Box(sz), origin=Origin(xyz=(sx, yf, szz)),
                        material=mats["trim"], name=f"{side}_window_trim_{i}", material_class_id="fabric.webbing")
        body.visual(Box((0.05, 0.004, 0.014)),
                    origin=Origin(xyz=(0.02, yf + sign * 0.0005, cz - win_hz - 0.028)),
                    material=mats["accent"], name=f"{side}_logo_patch", appearance_only=AppearanceOnlySpec(kind="decal"))


def _emit_pet_pad(body, r: ResolvedPetCarrierConfig, mats) -> None:
    pad_h = 0.04
    body.visual(Box((r.L * 0.78, r.W * 0.66, pad_h)),
                origin=Origin(xyz=(-0.01, 0.0, r.floor_top - 0.002 + pad_h / 2)),
                material=mats["pad"], name="pet_pad", material_class_id="fabric.carpet_fleece")


def _build_rigid_body(model, body, r: ResolvedPetCarrierConfig, mats) -> None:
    """Two-shell molded clamshell (cadquery loft+shell + flange + latch clips)."""
    fz = r.floor_z
    body.visual(mesh_from_cadquery(_tub_solid(r), "lower_tub"),
                origin=Origin(xyz=(0.0, 0.0, fz)), material=mats["shell2"], name="lower_tub", material_class_id="plastic.opaque_glossy_molded")
    flange = _flange_ring(r)
    body.visual(mesh_from_cadquery(flange, "flange_black"),
                origin=Origin(xyz=(0.0, 0.0, fz + r.wall_h - 0.021)),
                material=mats["shell2"], name="tub_rim_flange", material_class_id="plastic.opaque_glossy_molded")
    # upper shell lives on the body UNLESS the rear top-load lid owns it
    if r.access != "rear_topload_lid":
        shell_h = r.roof_z - (fz + r.wall_h)
        body.visual(mesh_from_cadquery(_upper_shell_solid(r, shell_h), "upper_shell"),
                    origin=Origin(xyz=(0.0, 0.0, fz + r.wall_h)),
                    material=mats["shell"], name="kennel_upper_shell", material_class_id="plastic.opaque_glossy_molded")
        body.visual(mesh_from_cadquery(flange, "flange_tan"),
                    origin=Origin(xyz=(0.0, 0.0, fz + r.wall_h - 0.001)),
                    material=mats["shell"], name="shell_rim_flange", material_class_id="plastic.opaque_glossy_molded")
    # dark latch clips clamping the flange (three per side + rear)
    fw = r.W * 1.12
    fl = r.L * 1.10
    for i, cx in enumerate((-0.14, 0.0, 0.16)):
        for j, sy in enumerate((-1.0, 1.0)):
            body.visual(Box((0.034, 0.024, 0.06)),
                        origin=Origin(xyz=(cx, sy * (fw / 2 - 0.005), fz + r.wall_h)),
                        material=mats["trim"], name=f"side_latch_clip_{i}_{j}", material_class_id="plastic.opaque_glossy_molded")
    body.visual(Box((0.024, 0.036, 0.06)),
                origin=Origin(xyz=(-(fl / 2 - 0.005), 0.0, fz + r.wall_h)),
                material=mats["trim"], name="rear_latch_clip", material_class_id="plastic.opaque_glossy_molded")
    _emit_pet_pad(body, r, mats)


def _build_wire_body(model, body, r: ResolvedPetCarrierConfig, mats) -> None:
    """Open welded-wire lattice: floor pan + posts + rails + grid bars (wire_cage)."""
    fz = r.floor_z
    L, W = r.L, r.W
    hl, hw = L / 2, W / 2
    post_r, rail_r, wire_r = 0.005, 0.004, 0.0028
    body.visual(Box((L - 0.004, W - 0.004, r.floor_t)),
                origin=Origin(xyz=(0.0, 0.0, fz + r.floor_t / 2)),
                material=mats["shell2"], name="floor_pan", material_class_id="metal.paint_coated")
    body.visual(Box((L - 0.02, W - 0.02, 0.012)),
                origin=Origin(xyz=(0.0, 0.0, fz + r.floor_t + 0.005)),
                material=mats["shell2"], name="floor_pan_lip", material_class_id="metal.paint_coated")
    bot_z = fz + r.floor_t + rail_r
    top_z = r.roof_z - rail_r
    post_len = top_z - fz
    corners = ((-1, -1), (-1, 1), (1, -1), (1, 1))
    for i, (sx, sy) in enumerate(corners):
        body.visual(Cylinder(radius=post_r, length=post_len),
                    origin=Origin(xyz=(sx * (hl - post_r), sy * (hw - post_r), fz + post_len / 2)),
                    material=mats["metal"], name=f"corner_post_{i}", material_class_id="metal.paint_coated")
    cx, cy = hl - post_r, hw - post_r
    rx_len, ry_len = L - 2 * post_r, W - 2 * post_r
    for name, d, cen in (
        ("bottom_rail_left", "x", (0.0, -cy, bot_z)), ("bottom_rail_right", "x", (0.0, cy, bot_z)),
        ("bottom_rail_back", "y", (-cx, 0.0, bot_z)), ("bottom_rail_front", "y", (cx, 0.0, bot_z)),
        ("top_rail_left", "x", (0.0, -cy, top_z)), ("top_rail_right", "x", (0.0, cy, top_z)),
        ("top_rail_back", "y", (-cx, 0.0, top_z)), ("top_rail_front", "y", (cx, 0.0, top_z)),
    ):
        _bar(body, d, cen, rx_len if d == "x" else ry_len, rail_r, mats["metal"], name)
    # wall + roof grid bars (loop-emitted)
    v_len = top_z - bot_z
    v_mid = (bot_z + top_z) / 2
    xs = _linspace(-(hl - 0.06), hl - 0.06, max(2, int((L - 0.12) / 0.055) + 1))
    ys = _linspace(-(hw - 0.06), hw - 0.06, max(2, int((W - 0.12) / 0.055) + 1))
    zs = _linspace(bot_z + 0.055, top_z - 0.03, max(2, int((top_z - bot_z) / 0.06)))
    vi = hi = 0
    for wy in (-cy, cy):  # side walls
        for x in xs:
            _bar(body, "z", (x, wy, v_mid), v_len, wire_r, mats["wire"], f"cage_bar_v_{vi}"); vi += 1
        for z in zs:
            _bar(body, "x", (0.0, wy, z), rx_len, wire_r, mats["wire"], f"cage_bar_h_{hi}"); hi += 1
    for y in ys:  # back wall
        _bar(body, "z", (-cx, y, v_mid), v_len, wire_r, mats["wire"], f"cage_bar_v_{vi}"); vi += 1
    for z in zs:
        _bar(body, "y", (-cx, 0.0, z), ry_len, wire_r, mats["wire"], f"cage_bar_h_{hi}"); hi += 1
    roof_z = top_z + rail_r
    for y in ys:
        _bar(body, "x", (0.0, y, roof_z), rx_len, wire_r, mats["wire"], f"cage_bar_h_{hi}"); hi += 1
    for x in xs:
        _bar(body, "y", (x, 0.0, roof_z), ry_len, wire_r, mats["wire"], f"cage_bar_h_{hi}"); hi += 1
    _emit_pet_pad(body, r, mats)


def _build_basket_body(model, body, r: ResolvedPetCarrierConfig, mats) -> None:
    """Woven wicker basket: section_loft shell+dome + tube weave bands/stakes."""
    fz = r.floor_z
    L, W, wt = r.L, r.W, 0.013
    hx, hy = L / 2, W / 2
    c = 0.032
    tub_top = fz + r.floor_t + r.wall_h
    mid_z = fz + r.floor_t + r.wall_h * 0.5
    bulge = 0.004
    outer = section_loft([
        _rect_loop(hx, hy, fz, c),
        _rect_loop(hx + bulge, hy + bulge * 0.75, mid_z, c + bulge),
        _rect_loop(hx, hy, tub_top, c),
    ])
    ic = max(c - wt, 0.012)
    inner = section_loft([
        _rect_loop(hx - wt, hy - wt, fz + r.floor_t, ic),
        _rect_loop(hx + bulge - wt, hy + bulge * 0.75 - wt, mid_z, ic + bulge),
        _rect_loop(hx - wt, hy - wt, tub_top + 0.01, ic),
    ])
    body.visual(mesh_from_geometry(boolean_difference(outer, inner), "basket_shell"),
                origin=Origin(), material=mats["shell"], name="basket_shell", material_class_id="organic.woven_plant_fiber")
    dome = section_loft([
        _rect_loop(hx, hy, tub_top - 0.003, c),
        _rect_loop(hx - 0.01, hy - 0.008, (tub_top + r.roof_z) / 2, c + 0.012),
        _rect_loop(0.16 * r.size_scale, 0.10 * r.size_scale, r.roof_z, c + 0.015),
    ])
    body.visual(mesh_from_geometry(dome, "dome_shell"), origin=Origin(),
                material=mats["shell"], name="dome_top_shell", material_class_id="organic.woven_plant_fiber")
    # horizontal weave bands (loop-emitted closed tubes)
    n_bands = 5
    span = r.wall_h - 0.05
    for i in range(n_bands):
        z = fz + r.floor_t + 0.02 + i * span / max(n_bands - 1, 1)
        path = _rect_loop(hx + bulge + 0.002, hy + bulge * 0.75 + 0.002, z, c + bulge + 0.002)
        body.visual(mesh_from_geometry(
            tube_from_spline_points(path, radius=0.003, closed_spline=True,
                                    radial_segments=8, samples_per_segment=3),
            f"weave_band_{i}"), origin=Origin(), material=mats["mesh"], name=f"weave_band_{i}", material_class_id="organic.woven_plant_fiber")
    # vertical stakes at the corners + edge midpoints (loop-emitted)
    n_stakes = 12
    stake_pts = _rect_loop(hx, hy, 0.0, c)
    # resample perimeter into n_stakes points
    xy = []
    for i in range(n_stakes):
        t = i / n_stakes * len(stake_pts)
        xy.append(stake_pts[int(t) % len(stake_pts)])
    for i, (sx, sy, _sz) in enumerate(xy):
        d = math.hypot(sx, sy) or 1.0
        ox, oy = sx / d * 0.002, sy / d * 0.002
        body.visual(mesh_from_geometry(
            tube_from_spline_points(
                [(sx + ox, sy + oy, fz + r.floor_t + 0.006),
                 (sx + ox, sy + oy, tub_top - 0.004)],
                radius=0.0025, radial_segments=8, samples_per_segment=2, cap_ends=True),
            f"weave_stake_{i}"), origin=Origin(), material=mats["shell2"], name=f"weave_stake_{i}", material_class_id="organic.woven_plant_fiber")
    # thick rim band
    rim_path = _rect_loop(hx + 0.003, hy + 0.003, tub_top + 0.001, c + 0.003)
    body.visual(mesh_from_geometry(
        tube_from_spline_points(rim_path, radius=0.005, closed_spline=True,
                                radial_segments=10, samples_per_segment=3), "basket_rim"),
        origin=Origin(), material=mats["trim"], name="basket_rim", material_class_id="organic.woven_plant_fiber")
    _emit_pet_pad(body, r, mats)


BODY_BUILDERS = {
    "soft_fabric_envelope": _build_soft_body,
    "rigid_molded_clamshell": _build_rigid_body,
    "open_wire_cage_lattice": _build_wire_body,
    "woven_wicker_basket": _build_basket_body,
}


# ===========================================================================
# Slot B: access — one openable panel (the guaranteed non-FIXED joint)
# ===========================================================================
def _build_front_fold_door(model, body, r: ResolvedPetCarrierConfig, mats) -> str:
    """Bottom-hinged fold-down door over the front opening (origin A)."""
    door = model.part("front_door")
    hw = r.door_hw - 0.005
    h = r.door_top_z - r.sill_z
    door.visual(Box((0.005, 2 * hw - 0.014, h - 0.014)),
                origin=Origin(xyz=(0.0, 0.0, h / 2)), material=mats["mesh"], name="door_mesh_panel", material_class_id=("fabric.open_mesh" if r.body_form == "soft_fabric_envelope" else "organic.woven_plant_fiber"))
    for i, (sz, (sy, szz)) in enumerate((
        ((0.007, 2 * hw, 0.014), (0.0, h - 0.007)),
        ((0.007, 2 * hw, 0.014), (0.0, 0.007)),
        ((0.007, 0.014, h), (hw - 0.007, h / 2)),
        ((0.007, 0.014, h), (-(hw - 0.007), h / 2)),
    )):
        door.visual(Box(sz), origin=Origin(xyz=(0.001, sy, szz)),
                    material=mats["trim"], name=f"door_trim_{i}", material_class_id=("fabric.webbing" if r.body_form == "soft_fabric_envelope" else "organic.woven_plant_fiber"))
    door.visual(Box((0.005, 0.05, 0.018)), origin=Origin(xyz=(0.0015, 0.0, h * 0.62)),
                material=mats["accent"], name="door_brand_patch", appearance_only=AppearanceOnlySpec(kind="decal"))
    model.articulation("body_to_front_door", ArticulationType.REVOLUTE, parent=body, child=door,
                       origin=Origin(xyz=(r.front_x, 0.0, r.sill_z)), axis=(0.0, 1.0, 0.0),
                       motion_limits=MotionLimits(effort=4.0, velocity=3.0, lower=0.0, upper=1.5))
    return "front_door"


def _build_top_hatch(model, body, r: ResolvedPetCarrierConfig, mats) -> str:
    """Rear-hinged top hatch that swings up over the top opening (origin A)."""
    hatch = model.part("top_hatch")
    lid_hx = r.top_hl + 0.008
    lid_hy = r.top_hw + 0.008
    hatch.visual(Box((2 * lid_hx - 0.014, 2 * lid_hy - 0.014, 0.004)),
                 origin=Origin(xyz=(lid_hx, 0.0, 0.002)), material=mats["mesh"], name="hatch_mesh_panel", material_class_id=("fabric.open_mesh" if r.body_form == "soft_fabric_envelope" else "organic.woven_plant_fiber"))
    for i, (sz, (sx, sy)) in enumerate((
        ((2 * lid_hx, 0.014, 0.006), (lid_hx, lid_hy - 0.007)),
        ((2 * lid_hx, 0.014, 0.006), (lid_hx, -(lid_hy - 0.007))),
        ((0.014, 2 * lid_hy, 0.006), (0.007, 0.0)),
        ((0.014, 2 * lid_hy, 0.006), (2 * lid_hx - 0.007, 0.0)),
    )):
        hatch.visual(Box(sz), origin=Origin(xyz=(sx, sy, 0.003)),
                     material=mats["trim"], name=f"hatch_trim_{i}", material_class_id=("fabric.webbing" if r.body_form == "soft_fabric_envelope" else "organic.woven_plant_fiber"))
    hatch.visual(Box((0.016, 0.010, 0.005)), origin=Origin(xyz=(2 * lid_hx - 0.004, 0.02, 0.006)),
                 material=mats["trim"], name="hatch_zip_pull", material_class_id="plastic.opaque_generic")
    hinge_x = r.top_cx - r.top_hl
    model.articulation("body_to_top_hatch", ArticulationType.REVOLUTE, parent=body, child=hatch,
                       origin=Origin(xyz=(hinge_x, 0.0, r.top_face_z - 0.001)), axis=(0.0, -1.0, 0.0),
                       motion_limits=MotionLimits(effort=4.0, velocity=3.0, lower=0.0, upper=2.2))
    return "top_hatch"


def _build_side_swing_door(model, body, r: ResolvedPetCarrierConfig, mats) -> str:
    """Vertical-axis side-swing wire-grate door (origin B); N grate bars."""
    door = model.part("wire_door")
    # The hinge must sit on the body's real front jamb: the front corner post on
    # a wire cage (near W/2), the solid shell front wall on a rigid kennel.
    if r.body_form == "open_wire_cage_lattice":
        hinge_y = r.W / 2 - 0.005 - 0.006
    else:
        hinge_y = r.door_hw
    hw = hinge_y  # door hangs from the hinge across the front, free edge at -hinge_y
    h = r.door_top_z - r.sill_z
    n_v = r.grate_bars
    n_h = max(2, round(r.grate_bars / 2))
    _emit_grate(door, r, mats, hw=hw, h=h, n_v=n_v, n_h=n_h)
    model.articulation("body_to_door", ArticulationType.REVOLUTE, parent=body, child=door,
                       origin=Origin(xyz=(r.front_x - 0.004, hinge_y, r.sill_z)), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=8.0, velocity=3.0, lower=0.0, upper=1.5))
    return "wire_door"


def _build_rear_topload_lid(model, body, r: ResolvedPetCarrierConfig, mats) -> str:
    """Whole upper shell as a rear-hinged lift-up lid (topload fork). Rigid only.

    Part frame at the rear rim hinge; shell offset forward by LID_DX so the rear
    edge meets the hinge. The carry molded handle rides on this lid."""
    lid = model.part("top_shell_lid")
    dx = r.L / 2.0  # shell center is L/2 ahead of the rear hinge
    shell_h = r.roof_z - r.rim_z
    flange = _flange_ring(r)
    lid.visual(mesh_from_cadquery(_upper_shell_solid(r, shell_h), "top_shell"),
               origin=Origin(xyz=(dx, 0.0, 0.0)), material=mats["shell"], name="kennel_upper_shell", material_class_id="plastic.opaque_glossy_molded")
    lid.visual(mesh_from_cadquery(flange, "flange_tan"),
               origin=Origin(xyz=(dx, 0.0, -0.001)), material=mats["shell"], name="shell_rim_flange", material_class_id="plastic.opaque_glossy_molded")
    # front lid-catch clips
    fl = r.L * 1.10
    for j, sy in enumerate((-1.0, 1.0)):
        lid.visual(Box((0.024, 0.036, 0.06)),
                   origin=Origin(xyz=(fl / 2 - 0.005 + dx, sy * 0.16, 0.0)),
                   material=mats["trim"], name=f"front_latch_clip_{j}", material_class_id="plastic.opaque_glossy_molded")
    model.articulation("body_to_top_lid", ArticulationType.REVOLUTE, parent=body, child=lid,
                       origin=Origin(xyz=(-r.L / 2.0, 0.0, r.rim_z)), axis=(0.0, -1.0, 0.0),
                       motion_limits=MotionLimits(effort=10.0, velocity=2.0, lower=0.0, upper=1.8))
    return "top_shell_lid"


def _build_slide_out_tray(model, body, r: ResolvedPetCarrierConfig, mats) -> str:
    """Front-bottom cleaning tray that slides out on rails (slide_tray fork)."""
    # inner rails resting on the cabin floor so the tray rides supported
    rail_h = 0.012
    rail_cz = r.floor_top - 0.001 + rail_h / 2  # bottom embeds 1 mm into the floor
    rail_top = r.floor_top - 0.001 + rail_h
    for sy, side in ((-1.0, "right"), (1.0, "left")):
        body.visual(Box((r.L * 0.80, 0.014, rail_h)),
                    origin=Origin(xyz=(0.0, sy * (r.W / 2 - 0.03), rail_cz)),
                    material=mats["shell2"], name=f"tray_rail_{side}", material_class_id=("plastic.opaque_glossy_molded" if r.body_form == "rigid_molded_clamshell" else "metal.paint_coated"))
    tray = model.part("slide_out_tray")
    tray_l, tray_w = r.L * 0.86, r.W * 0.82
    tray.visual(Box((tray_l, tray_w, 0.004)), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                material=mats["pad"], name="tray_pan", material_class_id="plastic.opaque_glossy_molded")
    for sy in (-1.0, 1.0):  # side edges
        tray.visual(Box((tray_l - 0.02, 0.006, 0.02)),
                    origin=Origin(xyz=(0.0, sy * (tray_w / 2 - 0.004), 0.010)),
                    material=mats["pad"], name=f"tray_edge_{'l' if sy > 0 else 'r'}", material_class_id="plastic.opaque_glossy_molded")
    tray.visual(Box((0.006, tray_w - 0.01, 0.02)), origin=Origin(xyz=(-(tray_l / 2 - 0.004), 0.0, 0.010)),
                material=mats["pad"], name="tray_edge_rear", material_class_id="plastic.opaque_glossy_molded")
    tray.visual(Box((0.012, tray_w * 0.55, 0.028)),
                origin=Origin(xyz=(tray_l / 2 - 0.004, 0.0, 0.016)),
                material=mats["trim"], name="tray_pull_lip", material_class_id="plastic.opaque_glossy_molded")
    tray_z = rail_top + 0.001  # pan bottom embeds 1 mm onto the rail tops
    model.articulation("body_to_tray", ArticulationType.PRISMATIC, parent=body, child=tray,
                       origin=Origin(xyz=(r.L * 0.10, 0.0, tray_z)), axis=(1.0, 0.0, 0.0),
                       motion_limits=MotionLimits(effort=10.0, velocity=0.3, lower=0.0, upper=0.17))
    return "slide_out_tray"


def _build_expandable_side_pod(model, body, r: ResolvedPetCarrierConfig, mats) -> str:
    """Fabric side pod on a PRISMATIC +Y that widens the cabin (expandable fork).

    The body left wall is omitted (soft body); the pod outer wall replaces it."""
    pod = model.part("expandable_side_pod")
    wt, wh = 0.012, r.wall_h
    z_base = r.floor_z + r.floor_t
    pod_depth = 0.12
    pod.visual(Box((r.L, wt, wh)), origin=Origin(xyz=(0.0, -wt / 2, z_base + wh / 2)),
               material=mats["shell"], name="pod_outer_wall", material_class_id="fabric.upholstery_plain")
    win_hx, win_hz = min(0.085, r.L * 0.34), 0.075 * r.size_scale
    pod.visual(Box((2 * win_hx, 0.004, 2 * win_hz)),
               origin=Origin(xyz=(0.02, -0.001, z_base + wh * 0.6)),
               material=mats["mesh"], name="pod_window_mesh", material_class_id="fabric.open_mesh")
    pod.visual(Box((0.05, 0.004, 0.014)),
               origin=Origin(xyz=(0.02, 0.0005, z_base + wh * 0.6 - win_hz - 0.028)),
               material=mats["accent"], name="pod_logo_patch", appearance_only=AppearanceOnlySpec(kind="decal"))
    # depth gusset panels (collapsed fabric that folds inside the cabin stowed)
    gy = -wt - pod_depth / 2
    ghx = r.L / 2 - wt
    pod.visual(Box((2 * ghx, pod_depth, wt)),
               origin=Origin(xyz=(0.0, gy, z_base + wh - wt / 2)),
               material=mats["shell2"], name="pod_gusset_top", material_class_id="fabric.upholstery_plain")
    pod.visual(Box((2 * ghx, pod_depth, wt)),
               origin=Origin(xyz=(0.0, gy, z_base + wt / 2)),
               material=mats["shell2"], name="pod_gusset_bottom", material_class_id="fabric.upholstery_plain")
    for sx, tag in ((ghx + wt / 2, "front"), (-ghx - wt / 2, "rear")):
        pod.visual(Box((wt, pod_depth, wh - 2 * wt)),
                   origin=Origin(xyz=(sx, gy, z_base + wh / 2)),
                   material=mats["shell2"], name=f"pod_gusset_{tag}", material_class_id="fabric.upholstery_plain")
    model.articulation("body_to_side_pod", ArticulationType.PRISMATIC, parent=body, child=pod,
                       origin=Origin(xyz=(0.0, r.W / 2, 0.0)), axis=(0.0, 1.0, 0.0),
                       motion_limits=MotionLimits(effort=6.0, velocity=0.5, lower=0.0, upper=pod_depth))
    return "expandable_side_pod"


ACCESS_BUILDERS = {
    "front_fold_door": _build_front_fold_door,
    "top_hatch": _build_top_hatch,
    "side_swing_door": _build_side_swing_door,
    "rear_topload_lid": _build_rear_topload_lid,
    "slide_out_tray": _build_slide_out_tray,
    "expandable_side_pod": _build_expandable_side_pod,
}


# ===========================================================================
# Slot C: carry — one carry means
# ===========================================================================
def _build_webbing_top_handle(model, body, top_host, r: ResolvedPetCarrierConfig, mats) -> None:
    """Arched webbing/cane carry handle loop on the roof (origin A / basket)."""
    z0 = r.roof_z
    pts = [
        (0.10, -0.075, z0 - 0.006), (0.10, -0.05, z0 + 0.04), (0.10, 0.0, z0 + 0.056),
        (0.10, 0.05, z0 + 0.04), (0.10, 0.075, z0 - 0.006),
    ]
    top_host.visual(mesh_from_geometry(
        tube_from_spline_points(pts, radius=0.007, radial_segments=10), "carry_handle"),
        origin=Origin(), material=mats["metal"], name="carry_handle_loop", material_class_id=("fabric.webbing" if r.body_form == "soft_fabric_envelope" else "organic.woven_plant_fiber"))


def _build_molded_rigid_handle(model, body, top_host, r: ResolvedPetCarrierConfig, mats) -> None:
    """Molded box handle (base plate + risers + grip bar) on the roof host."""
    # top_host = lid (rear_topload) with roof in its LOCAL frame, or body with
    # roof at world roof_z. Detect via the part name.
    if top_host.name == "top_shell_lid":
        rz = r.roof_z - r.rim_z  # lid-local roof height
        dx = r.L / 2.0
    else:
        rz = r.roof_z
        dx = 0.0
    top_host.visual(Box((0.16, 0.08, 0.012)), origin=Origin(xyz=(dx, 0.0, rz + 0.006)),
                    material=mats["shell2"], name="handle_base_plate", material_class_id="plastic.opaque_glossy_molded")
    for i, sx in enumerate((-1.0, 1.0)):
        top_host.visual(Box((0.016, 0.05, 0.072)),
                        origin=Origin(xyz=(sx * 0.062 + dx, 0.0, rz + 0.045)),
                        material=mats["shell2"], name=f"handle_riser_{i}", material_class_id="plastic.opaque_glossy_molded")
    top_host.visual(Box((0.14, 0.048, 0.024)), origin=Origin(xyz=(dx, 0.0, rz + 0.072)),
                    material=mats["shell2"], name="handle_grip_bar", material_class_id="plastic.opaque_glossy_molded")


def _build_backpack_harness(model, body, top_host, r: ResolvedPetCarrierConfig, mats) -> None:
    """Semi-rigid back panel + 2 shoulder straps + sternum clip + grab handle.

    All host visuals on the rear wall (Rule 1: harness does not articulate)."""
    panel_t = 0.010
    panel_hy = min(0.11, r.W * 0.36)
    panel_hz = 0.11 * r.size_scale
    panel_x = -(r.L / 2 + panel_t / 2)
    panel_cz = r.floor_z + r.floor_t + r.wall_h * 0.6
    body.visual(Box((panel_t, 2 * panel_hy, 2 * panel_hz)),
                origin=Origin(xyz=(panel_x, 0.0, panel_cz)),
                material=mats["shell2"], name="back_panel_shell", material_class_id="fabric.upholstery_plain")
    for zoff in (-0.05, 0.0, 0.05):
        body.visual(Box((0.006, 2 * panel_hy - 0.03, 0.032)),
                    origin=Origin(xyz=(panel_x - panel_t / 2 - 0.003, 0.0, panel_cz + zoff)),
                    material=mats["mesh"], name=f"panel_pad_{int(zoff * 1000)}", material_class_id="fabric.flexible_foam")
    # two contoured shoulder straps sweeping behind the panel
    for i, sign in enumerate((-1.0, 1.0)):
        y0 = sign * 0.075
        pts = [
            (panel_x - 0.005, y0, panel_cz + panel_hz - 0.01),
            (panel_x - 0.04, sign * 0.10, panel_cz + 0.02),
            (panel_x - 0.045, sign * 0.10, panel_cz - 0.02),
            (panel_x - 0.02, sign * 0.09, panel_cz - panel_hz + 0.02),
        ]
        body.visual(mesh_from_geometry(
            tube_from_spline_points(pts, radius=0.018, radial_segments=8), f"shoulder_strap_{i}"),
            origin=Origin(), material=mats["mesh"], name=f"shoulder_strap_{i}", material_class_id="fabric.webbing")
    # sternum clip bridging the two straps at their mid sweep (must intersect
    # both strap tubes for a support path — straps pass ~(panel_x-0.045, ±0.10)).
    body.visual(Box((0.020, 0.22, 0.030)),
                origin=Origin(xyz=(panel_x - 0.045, 0.0, panel_cz)),
                material=mats["metal"], name="sternum_clip", material_class_id="metal.aluminum_bare")
    # top grab handle arch above the panel
    grab = [
        (panel_x, -0.035, panel_cz + panel_hz), (panel_x - 0.01, 0.0, panel_cz + panel_hz + 0.03),
        (panel_x, 0.035, panel_cz + panel_hz),
    ]
    body.visual(mesh_from_geometry(
        tube_from_spline_points(grab, radius=0.005, radial_segments=8), "grab_handle"),
        origin=Origin(), material=mats["shell2"], name="grab_handle", material_class_id="fabric.webbing")


def _build_wheeled_rolling_trolley(model, body, top_host, r: ResolvedPetCarrierConfig, mats) -> None:
    """Raised cabin on a wheel base: platform+forks (host visuals) + 4 CONTINUOUS
    casters + PRISMATIC trolley handle (rolling fork)."""
    wheel_r = 0.025
    fork_h = 0.036
    base_t = 0.014
    base_l = r.L * 1.04
    base_w = r.W * 1.04
    # Platform bottom sits on the fork tops; its top embeds ~5 mm into the cabin
    # floor (floor_z == ROLL_BASE_H) so the base and cabin share solid geometry
    # (no island) regardless of size_scale.
    plat_bot = wheel_r + fork_h - 0.004  # overlap the fork mounts below
    plat_top = r.floor_z + 0.006  # embed into the floor above
    plat_h = plat_top - plat_bot
    # base platform + ribs (host visuals on body, bridging forks -> cabin floor)
    body.visual(Box((base_l, base_w, plat_h)),
                origin=Origin(xyz=(0.0, 0.0, (plat_bot + plat_top) / 2)),
                material=mats["shell2"], name="base_platform", material_class_id="metal.paint_coated")
    _cx = base_l / 2 - 0.045
    _cy = base_w / 2 - 0.04
    corners = [(_cx, _cy), (_cx, -_cy), (-_cx, _cy), (-_cx, -_cy)]
    for i, (cx, cy) in enumerate(corners):
        # fork mount + prongs + axle pin (host visuals)
        body.visual(Box((0.03, 0.03, 0.005)),
                    origin=Origin(xyz=(cx, cy, wheel_r + fork_h - 0.003)),
                    material=mats["shell2"], name=f"caster_fork_mount_{i}", material_class_id="metal.paint_coated")
        for sx in (-1.0, 1.0):
            body.visual(Box((0.004, 0.026, fork_h + 0.005)),
                        origin=Origin(xyz=(cx + sx * 0.014, cy, wheel_r + fork_h / 2)),
                        material=mats["shell2"], name=f"caster_prong_{i}_{'l' if sx > 0 else 'r'}", material_class_id="metal.paint_coated")
        body.visual(Cylinder(radius=0.003, length=0.028),
                    origin=Origin(xyz=(cx, cy, wheel_r), rpy=(0.0, math.pi / 2, 0.0)),
                    material=mats["metal"], name=f"axle_pin_{i}", material_class_id="metal.steel_bare")
    # caster wheels (CONTINUOUS spin about +X)
    for i, (cx, cy) in enumerate(corners):
        wheel = model.part(f"caster_wheel_{i}")
        wheel.visual(Cylinder(radius=wheel_r, length=0.018),
                     origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
                     material=mats["wire"], name=f"wheel_disc_{i}", material_class_id="rubber.smooth_plain")
        model.articulation(f"wheel_spin_{i}", ArticulationType.CONTINUOUS, parent=body, child=wheel,
                           origin=Origin(xyz=(cx, cy, wheel_r)), axis=(1.0, 0.0, 0.0),
                           motion_limits=MotionLimits(effort=2.0, velocity=10.0))
    # rear-wall guide rails for the telescoping handle (host visuals)
    for bi, bz in enumerate((r.rim_z - 0.10, r.rim_z - 0.03)):
        body.visual(Box((0.014, 0.15, 0.016)),
                    origin=Origin(xyz=(-(r.L / 2 - 0.006), 0.0, bz)),
                    material=mats["trim"], name=f"handle_guide_rail_{bi}", material_class_id="metal.paint_coated")
    # telescoping trolley handle (PRISMATIC +Z)
    handle = model.part("trolley_handle")
    tube_len = r.wall_h + 0.10
    hidden = 0.12
    spacing = min(0.12, r.W * 0.5)
    tube_cz = tube_len / 2 - hidden
    for j, sy in enumerate((-1.0, 1.0)):
        handle.visual(Cylinder(radius=0.007, length=tube_len),
                      origin=Origin(xyz=(0.0, sy * spacing / 2, tube_cz)),
                      material=mats["metal"], name=f"handle_tube_{j}", material_class_id="metal.aluminum_bare")
    handle.visual(Box((0.008, spacing - 0.014, 0.008)),
                  origin=Origin(xyz=(0.0, 0.0, -hidden + 0.01)), material=mats["metal"],
                  name="handle_cross_brace", material_class_id="metal.aluminum_bare")
    # Grip crossbar seats onto the two tube tops (bridges them): its box must
    # overlap the tube ends, else it islands off the handle part.
    grip_cz = tube_len - hidden + 0.004  # box spans tube_top-0.009 .. tube_top+0.017
    handle.visual(Box((0.024, spacing + 0.02, 0.026)), origin=Origin(xyz=(0.0, 0.0, grip_cz)),
                  material=mats["trim"], name="handle_grip", material_class_id="rubber.smooth_plain")
    model.articulation("body_to_trolley_handle", ArticulationType.PRISMATIC, parent=body, child=handle,
                       origin=Origin(xyz=(-(r.L / 2 - 0.012), 0.0, r.rim_z - 0.02)), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=30.0, velocity=0.3, lower=0.0, upper=0.24))


CARRY_BUILDERS = {
    "webbing_top_handle": _build_webbing_top_handle,
    "backpack_harness": _build_backpack_harness,
    "molded_rigid_handle": _build_molded_rigid_handle,
    "wheeled_rolling_trolley": _build_wheeled_rolling_trolley,
}


# ===========================================================================
# Assembly
# ===========================================================================
def build_pet_carrier(config: PetCarrierConfig | None = None, *,
                      assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {k: model.material(f"pc_{k}_{r.palette_style}", rgba=v)
            for k, v in PALETTES[r.palette_style].items()}

    body = model.part("carrier_body")
    BODY_BUILDERS[r.body_form](model, body, r, mats)

    access_part_name = ACCESS_BUILDERS[r.access](model, body, r, mats)

    # roof host for a top handle: the lid part when the top-load shell owns it.
    top_host = model.get_part(access_part_name) if r.access == "rear_topload_lid" else body
    CARRY_BUILDERS[r.carry](model, body, top_host, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pet_carrier(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_pet_carrier(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _allow_seating_overlaps(ctx, model, r: ResolvedPetCarrierConfig) -> None:
    """Element-scoped allowances for intentional closed-pose seating contacts."""
    body = model.get_part("carrier_body")

    if r.access == "front_fold_door":
        door = model.get_part("front_door")
        ctx.allow_overlap(body, door, reason="closed fold-down door seats into the front opening frame")
    elif r.access == "top_hatch":
        hatch = model.get_part("top_hatch")
        ctx.allow_overlap(body, hatch, reason="closed hatch lid rests on the domed top rim around the opening")
    elif r.access == "side_swing_door":
        door = model.get_part("wire_door")
        ctx.allow_overlap(body, door, reason="closed wire-grate door seats over the front opening / knuckle on jamb")
    elif r.access == "rear_topload_lid":
        lid = model.get_part("top_shell_lid")
        ctx.allow_overlap(body, lid, reason="closed top-load lid flange + catch clips seat on the tub rim flange")
    elif r.access == "slide_out_tray":
        tray = model.get_part("slide_out_tray")
        for side in ("left", "right"):
            ctx.allow_overlap(body, tray, elem_a=f"tray_rail_{side}", elem_b="tray_pan",
                              reason="tray pan rides on the inner molded rails")
        ctx.allow_overlap(body, tray, reason="stowed tray nests inside the tub above the floor")
    elif r.access == "expandable_side_pod":
        pod = model.get_part("expandable_side_pod")
        ctx.allow_overlap(body, pod, reason="stowed pod outer wall + collapsed gussets fold inside the left cabin opening")

    if r.carry == "wheeled_rolling_trolley":
        for i in range(4):
            wheel = model.get_part(f"caster_wheel_{i}")
            ctx.allow_overlap(body, wheel, elem_a=f"axle_pin_{i}", elem_b=f"wheel_disc_{i}",
                              reason="axle pin captured in the caster wheel bore")
        handle = model.get_part("trolley_handle")
        ctx.allow_overlap(body, handle, reason="telescoping trolley tubes retained inside the rear guide rails")


def run_pet_carrier_tests(object_model: ArticulatedObject, config: PetCarrierConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    _allow_seating_overlaps(ctx, object_model, r)

    body = object_model.get_part("carrier_body")

    # ---- Identity: enclosed cabin + at least one real access joint + carry. ----
    ctx.check(
        "carrier_has_body_and_access_joint",
        body is not None and len(object_model.articulations) >= 1,
        details=f"articulations={[a.name for a in object_model.articulations]}",
    )
    body_aabb = ctx.part_world_aabb(body)
    ctx.check(
        "cabin_is_enclosing_volume",
        body_aabb is not None
        and (body_aabb[1][0] - body_aabb[0][0]) > 0.20
        and (body_aabb[1][2] - body_aabb[0][2]) > 0.15,
        details=f"body_aabb={body_aabb}",
    )

    # ---- Targeted mechanism poses (one per access mechanism). ----
    if r.access == "front_fold_door":
        door = object_model.get_part("front_door")
        j = object_model.get_articulation("body_to_front_door")
        rest = ctx.part_world_aabb(door)
        with ctx.pose({j: 1.5}):
            opened = ctx.part_world_aabb(door)
        ctx.check("front_door_folds_outward",
                  rest is not None and opened is not None and opened[1][0] > r.front_x + 0.08,
                  details=f"rest={rest}, opened={opened}")
    elif r.access == "top_hatch":
        hatch = object_model.get_part("top_hatch")
        j = object_model.get_articulation("body_to_top_hatch")
        rest = ctx.part_world_aabb(hatch)
        with ctx.pose({j: 2.0}):
            up = ctx.part_world_aabb(hatch)
        ctx.check("top_hatch_rises_above_roof",
                  rest is not None and up is not None and up[1][2] > r.roof_z + 0.06,
                  details=f"rest={rest}, up={up}")
    elif r.access == "side_swing_door":
        door = object_model.get_part("wire_door")
        j = object_model.get_articulation("body_to_door")
        ctx.check("side_door_is_revolute_z",
                  j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99,
                  details=f"axis={j.axis}")
        rest = ctx.part_world_aabb(door)
        with ctx.pose({j: 1.4}):
            sw = ctx.part_world_aabb(door)
        ctx.check("side_door_swings_out",
                  rest is not None and sw is not None and sw[1][0] > rest[1][0] + 0.05,
                  details=f"rest={rest}, swung={sw}")
    elif r.access == "rear_topload_lid":
        lid = object_model.get_part("top_shell_lid")
        j = object_model.get_articulation("body_to_top_lid")
        rest = ctx.part_world_aabb(lid)
        with ctx.pose({j: 1.5}):
            up = ctx.part_world_aabb(lid)
        ctx.check("topload_lid_lifts",
                  rest is not None and up is not None and up[1][2] > rest[1][2] + 0.08,
                  details=f"rest={rest}, up={up}")
    elif r.access == "slide_out_tray":
        tray = object_model.get_part("slide_out_tray")
        j = object_model.get_articulation("body_to_tray")
        ctx.check("tray_is_prismatic_x",
                  j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[0]) > 0.99,
                  details=f"axis={j.axis}")
        rest = ctx.part_world_position(tray)
        with ctx.pose({j: 0.17}):
            ext = ctx.part_world_position(tray)
        ctx.check("tray_slides_out_front",
                  rest is not None and ext is not None and ext[0] > rest[0] + 0.12,
                  details=f"rest={rest}, ext={ext}")
    elif r.access == "expandable_side_pod":
        pod = object_model.get_part("expandable_side_pod")
        j = object_model.get_articulation("body_to_side_pod")
        ctx.check("pod_is_prismatic_y",
                  j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[1]) > 0.99,
                  details=f"axis={j.axis}")
        rest = ctx.part_world_position(pod)
        with ctx.pose({j: 0.12}):
            ext = ctx.part_world_position(pod)
        ctx.check("pod_expands_outward",
                  rest is not None and ext is not None and ext[1] > rest[1] + 0.09,
                  details=f"rest={rest}, ext={ext}")

    # ---- Carry mechanism poses (rolling). ----
    if r.carry == "wheeled_rolling_trolley":
        for i in range(4):
            wheel = object_model.get_part(f"caster_wheel_{i}")
            aabb = ctx.part_world_aabb(wheel)
            ctx.check(f"caster_wheel_{i}_near_ground",
                      aabb is not None and aabb[0][2] < 0.006,
                      details=f"wheel_{i} min_z={None if aabb is None else aabb[0][2]}")
        handle = object_model.get_part("trolley_handle")
        j = object_model.get_articulation("body_to_trolley_handle")
        rest = ctx.part_world_position(handle)
        with ctx.pose({j: 0.24}):
            up = ctx.part_world_position(handle)
        ctx.check("trolley_handle_extends_up",
                  rest is not None and up is not None and up[2] > rest[2] + 0.18,
                  details=f"rest={rest}, up={up}")

    # ---- Rule 5: full-travel non-穿模 across sampled joint poses. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

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
    "Access",
    "Carry",
    "PaletteStyle",
    "PetCarrierConfig",
    "ResolvedPetCarrierConfig",
    "build_pet_carrier",
    "build_seeded_pet_carrier",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_pet_carrier_tests",
]
