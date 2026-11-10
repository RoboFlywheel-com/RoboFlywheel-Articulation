# SPDX-License-Identifier: Apache-2.0

"""Pet_Animal related / Pet stroller procedural template (modular).

Spec: articraft_template_authoring/specs_modular_v1/pet_stroller.md

A wheeled, human-pushed pet carriage: a fabric or rigid pet cabin on a rolling
tubular frame, a rear push handle, a fold-open canopy/top, and >=3 spinning
ground wheels. Pattern = mixed (parallel_children + wheel-count multiplicity):
one ``frame`` root carries every fixed chassis/undercarriage ``.visual(...)`` and
each subsystem (wheels + caster yokes, cabin body / carrier pod, canopy/dome +
optional front door, push handle) is a parallel child of the frame.

Coordinate frame (origin-A convention): X = left/right width, +Y = front /
-Y = rear, Z = up. Origin-B (jogger / swing / reversible) structure is
re-expressed in this frame (Rule 3 adaptation: part tree + joint semantics +
primitive family preserved).

Slots (all parallel children of ``frame``):
  * Slot A chassis (①/②/N): four_wheel_fixed / four_wheel_swivel / three_wheel_jogger
  * Slot B cabin_form (③ Primary Form Family): soft_fabric_cabin / rigid_carrier_pod
  * Slot C top_access (②/③): fold_back_canopy / enclosed_mesh_dome / front_door_canopy
  * Slot D push_handle (②): u_fold_handle / swing_bar_handle / telescoping_handle / reversible_handle

Rules:
  Rule 1 — non-articulating detail (mesh windows, storage basket, trim tubes,
    springs, fenders, cup ring, vent grilles) is a host ``.visual(...)``; the sole
    FIXED articulation is ``frame_to_pod`` (a rigid molded carrier sub-assembly that
    needs its own reference frame — fusing it into the tubular frame part would lose
    the detachable-shell identity; anchored on a real saddle-cradle contact).
  Rule 2 — every moving child is a captured pin-through-sleeve / turntable /
    prismatic-sleeve pivot; ``MatingContract`` cannot express it, so joints are
    grandfathered (omit ``mating=``) and kept honest with element-scoped
    ``allow_overlap`` + ``expect_overlap`` mirroring each source's run_tests.
  Rule 3 — structure derives from declared 5-star sources; Tire/Wheel/canopy/dome/
    pod Mesh heroes preserved (no Box downgrade).
  Rule 5 — ``fail_if_parts_overlap_in_sampled_poses`` + one targeted ``ctx.pose``
    per mechanism.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import pi
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BoltPattern,
    Box,
    Cylinder,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    Inertial,
    MeshGeometry,
    MotionLimits,
    Origin,
    PerforatedPanelGeometry,
    TestContext,
    TestReport,
    TireGeometry,
    TireGroove,
    TireSidewall,
    TireTread,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
Chassis = Literal["four_wheel_fixed", "four_wheel_swivel", "three_wheel_jogger"]
CabinForm = Literal["soft_fabric_cabin", "rigid_carrier_pod"]
TopAccess = Literal["fold_back_canopy", "enclosed_mesh_dome", "front_door_canopy"]
PushHandle = Literal[
    "u_fold_handle", "swing_bar_handle", "telescoping_handle", "reversible_handle"
]
PaletteStyle = Literal["champagne_black", "navy_jogger", "charcoal_grey", "sand_tan"]

CHASSIS: tuple[Chassis, ...] = ("four_wheel_fixed", "four_wheel_swivel", "three_wheel_jogger")
CABIN_FORMS: tuple[CabinForm, ...] = ("soft_fabric_cabin", "rigid_carrier_pod")
PUSH_HANDLES: tuple[PushHandle, ...] = (
    "u_fold_handle",
    "swing_bar_handle",
    "telescoping_handle",
    "reversible_handle",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "champagne_black",
    "navy_jogger",
    "charcoal_grey",
    "sand_tan",
)

# Compatibility matrix (§9): dome + front-door only on the soft fabric cabin (both
# forks are on soft-fabric single-tier bases; a dome/drop-door on a rigid closed
# tub is not source-faithful).
ALLOWED_TOPS: dict[CabinForm, tuple[TopAccess, ...]] = {
    "soft_fabric_cabin": ("fold_back_canopy", "enclosed_mesh_dome", "front_door_canopy"),
    "rigid_carrier_pod": ("fold_back_canopy",),
}

# ---------------------------------------------------------------------------
# Palettes. `fabric` + `frame_tube` carry the recognizable colorway; tires /
# plastic hardware are near-constant. 4 colorways.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "champagne_black": {
        "fabric": (0.015, 0.015, 0.016, 1.0),
        "frame_tube": (0.92, 0.62, 0.31, 1.0),
        "mesh_window": (0.70, 0.60, 0.43, 0.78),
        "storage": (0.025, 0.027, 0.026, 0.72),
        "plastic": (0.035, 0.036, 0.038, 1.0),
        "rubber": (0.015, 0.015, 0.014, 1.0),
        "rim": (0.035, 0.035, 0.037, 1.0),
        "silver": (0.78, 0.76, 0.70, 1.0),
        "spring": (0.90, 0.05, 0.03, 1.0),
        "grip": (0.96, 0.56, 0.27, 1.0),
        "pod": (0.82, 0.80, 0.76, 1.0),
    },
    "navy_jogger": {
        "fabric": (0.02, 0.06, 0.30, 1.0),
        "frame_tube": (0.06, 0.06, 0.07, 1.0),
        "mesh_window": (0.0, 0.0, 0.0, 0.46),
        "storage": (0.02, 0.02, 0.03, 0.66),
        "plastic": (0.05, 0.05, 0.06, 1.0),
        "rubber": (0.015, 0.014, 0.012, 1.0),
        "rim": (0.86, 0.88, 0.86, 1.0),
        "silver": (0.72, 0.74, 0.72, 1.0),
        "spring": (0.85, 0.12, 0.10, 1.0),
        "grip": (0.10, 0.10, 0.11, 1.0),
        "pod": (0.20, 0.28, 0.46, 1.0),
    },
    "charcoal_grey": {
        "fabric": (0.14, 0.15, 0.17, 1.0),
        "frame_tube": (0.55, 0.57, 0.60, 1.0),
        "mesh_window": (0.05, 0.05, 0.06, 0.55),
        "storage": (0.10, 0.10, 0.11, 0.68),
        "plastic": (0.06, 0.06, 0.07, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "rim": (0.30, 0.31, 0.33, 1.0),
        "silver": (0.80, 0.82, 0.84, 1.0),
        "spring": (0.90, 0.42, 0.10, 1.0),
        "grip": (0.20, 0.21, 0.23, 1.0),
        "pod": (0.40, 0.42, 0.45, 1.0),
    },
    "sand_tan": {
        "fabric": (0.60, 0.50, 0.36, 1.0),
        "frame_tube": (0.50, 0.34, 0.20, 1.0),
        "mesh_window": (0.30, 0.24, 0.16, 0.62),
        "storage": (0.34, 0.28, 0.20, 0.70),
        "plastic": (0.12, 0.10, 0.07, 1.0),
        "rubber": (0.02, 0.018, 0.015, 1.0),
        "rim": (0.78, 0.62, 0.40, 1.0),
        "silver": (0.86, 0.82, 0.70, 1.0),
        "spring": (0.86, 0.32, 0.10, 1.0),
        "grip": (0.86, 0.72, 0.48, 1.0),
        "pod": (0.80, 0.72, 0.55, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Single-sourced geometry constants (world meters; origin-A frame).
# ---------------------------------------------------------------------------
HALF_W = 0.36            # cabin half-width (× cabin_width_scale)
FRONT_Y = 0.44           # cabin front edge
REAR_Y = -0.44           # cabin rear edge
FLOOR_Z = 0.435          # cabin floor center z
CABIN_TOP_Z = 0.68       # cabin rim height
CANOPY_HINGE = (0.0, -0.50, 0.735)   # axis X
HANDLE_HINGE = (0.0, -0.82, 0.720)   # axis X (u_fold / swing_bar)
REAR_AXLE_Y = -0.565
FRONT_AXLE_Y = 0.630
CASTER_Y = 0.720         # swivel casters sit forward of the frame so their swept circle clears it
REAR_WHEEL_X = 0.385     # × cabin_width_scale
FRONT_WHEEL_X = 0.360    # × cabin_width_scale
CASTER_DROP = 0.150      # kingpin socket -> front wheel axle drop (swivel)
CASTER_WHEEL_R = 0.075   # compact swivel-caster wheel (small so its swivel-swept circle clears the frame)
CASTER_TRAIL = 0.030     # kingpin -> axle forward offset (caster trail)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class PetStrollerConfig:
    chassis: Chassis | None = None
    cabin_form: CabinForm | None = None
    top_access: TopAccess | None = None
    push_handle: PushHandle | None = None
    palette_style: PaletteStyle = "champagne_black"
    rear_radius: float = 0.160
    front_radius: float = 0.110
    cabin_width_scale: float = 1.0
    name: str = "pet_stroller"


@dataclass(frozen=True)
class ResolvedPetStrollerConfig:
    chassis: Chassis
    cabin_form: CabinForm
    top_access: TopAccess
    push_handle: PushHandle
    palette_style: PaletteStyle
    rear_radius: float
    front_radius: float
    cabin_width_scale: float
    name: str

    @property
    def wheel_count(self) -> int:
        return 3 if self.chassis == "three_wheel_jogger" else 4

    @property
    def half_w(self) -> float:
        return HALF_W * self.cabin_width_scale

    @property
    def rear_wheel_x(self) -> float:
        return REAR_WHEEL_X * self.cabin_width_scale

    @property
    def front_wheel_x(self) -> float:
        return FRONT_WHEEL_X * self.cabin_width_scale


def config_from_seed(seed: int) -> PetStrollerConfig:
    """Deterministic procedural sampling over the full slot domain (seed 0 not
    special). ``top_access`` is drawn from the cabin_form-allowed set."""
    rng = random.Random(seed)
    chassis = rng.choice(CHASSIS)
    cabin_form = rng.choice(CABIN_FORMS)
    top_access = rng.choice(ALLOWED_TOPS[cabin_form])
    push_handle = rng.choice(PUSH_HANDLES)
    rear_radius = round(rng.uniform(0.145, 0.190), 4)
    front_radius = round(rng.uniform(0.096, 0.130), 4)
    return PetStrollerConfig(
        chassis=chassis,
        cabin_form=cabin_form,
        top_access=top_access,
        push_handle=push_handle,
        palette_style=rng.choice(PALETTE_STYLES),
        rear_radius=rear_radius,
        front_radius=front_radius,
        cabin_width_scale=round(rng.uniform(0.92, 1.08), 4),
        name=f"seeded_pet_stroller_{seed}",
    )


def resolve_config(config: PetStrollerConfig | None = None) -> ResolvedPetStrollerConfig:
    cfg = config or PetStrollerConfig()
    chassis = _pick(cfg.chassis, CHASSIS)
    cabin_form = _pick(cfg.cabin_form, CABIN_FORMS)
    allowed_tops = ALLOWED_TOPS[cabin_form]
    top_access = cfg.top_access if cfg.top_access in allowed_tops else allowed_tops[0]
    push_handle = _pick(cfg.push_handle, PUSH_HANDLES)
    # §9 compatibility gate: the reversible swing-over handle sweeps its arms up and
    # forward over the cabin top; a fully enclosed mesh dome occupies that swing
    # volume, so the two are incompatible. Fall back to the swing-bar fold handle
    # (the dome fork's own origin-B handle) when they would combine.
    if push_handle == "reversible_handle" and top_access == "enclosed_mesh_dome":
        push_handle = "swing_bar_handle"
    rear_radius = _clamp(cfg.rear_radius, 0.145, 0.190)
    # front wheel must stay visibly smaller than the rear (inequality).
    front_radius = _clamp(cfg.front_radius, 0.096, min(0.130, rear_radius - 0.02))
    return ResolvedPetStrollerConfig(
        chassis=chassis,
        cabin_form=cabin_form,
        top_access=top_access,
        push_handle=push_handle,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        rear_radius=rear_radius,
        front_radius=front_radius,
        cabin_width_scale=_clamp(cfg.cabin_width_scale, 0.92, 1.08),
        name=cfg.name or "pet_stroller",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedPetStrollerConfig) else resolve_config(config)
    return (
        ("chassis", r.chassis),
        ("cabin_form", r.cabin_form),
        ("top_access", r.top_access),
        ("push_handle", r.push_handle),
        ("wheel_count", f"n{r.wheel_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


SIDES: tuple[tuple[str, float], ...] = (("0", -1.0), ("1", 1.0))


# ===========================================================================
# Geometry helpers (origin-A / origin-B, preserved primitives)
# ===========================================================================
def _mesh(geometry, name: str):
    return mesh_from_geometry(geometry, name)


def _tube(part, name, points, radius, material):
    # Thin structural tubes: modest tessellation keeps the (many) frame tubes cheap
    # to compile under heavy parallel load without any visible faceting.
    part.visual(
        _mesh(
            tube_from_spline_points(
                points, radius=radius, samples_per_segment=7, radial_segments=12, cap_ends=True
            ),
            name,
        ),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _canopy_shell_from_side_path(path, *, width: float, thickness: float) -> MeshGeometry:
    """Thin canopy sheet whose side edges share the (y, z) rib path (origin A)."""
    geom = MeshGeometry()
    half = width / 2.0
    rows = []
    for y, z in path:
        rows.append(
            (
                geom.add_vertex(-half, y, z),
                geom.add_vertex(half, y, z),
                geom.add_vertex(-half, y, z - thickness),
                geom.add_vertex(half, y, z - thickness),
            )
        )
    for i in range(len(rows) - 1):
        a0, a1, a2, a3 = rows[i]
        b0, b1, b2, b3 = rows[i + 1]
        geom.add_face(a0, b0, b1)
        geom.add_face(a0, b1, a1)
        geom.add_face(a2, a3, b3)
        geom.add_face(a2, b3, b2)
        geom.add_face(a0, a2, b2)
        geom.add_face(a0, b2, b0)
        geom.add_face(a1, b1, b3)
        geom.add_face(a1, b3, a3)
    for row in (rows[0], rows[-1]):
        a0, a1, a2, a3 = row
        geom.add_face(a0, a1, a3)
        geom.add_face(a0, a3, a2)
    return geom


def _dome_side_wall(path, x, bottom_z, thickness=0.004) -> MeshGeometry:
    """Vertical mesh wall at fixed X following the arch (y, z) path down to a flat
    bottom (origin-B dome adapted to A's axes). Thickness toward the dome center."""
    sign = -1.0 if x > 0 else 1.0
    x2 = x + sign * thickness
    geom = MeshGeometry()
    ot, it, ob, ib = [], [], [], []
    for y, z in path:
        ot.append(geom.add_vertex(x, y, z))
        it.append(geom.add_vertex(x2, y, z))
        ob.append(geom.add_vertex(x, y, bottom_z))
        ib.append(geom.add_vertex(x2, y, bottom_z))
    for i in range(len(path) - 1):
        geom.add_face(ot[i], ot[i + 1], ob[i + 1])
        geom.add_face(ot[i], ob[i + 1], ob[i])
        geom.add_face(it[i], ib[i + 1], it[i + 1])
        geom.add_face(it[i], ib[i], ib[i + 1])
        geom.add_face(ot[i], it[i], it[i + 1])
        geom.add_face(ot[i], it[i + 1], ot[i + 1])
        geom.add_face(ob[i], ob[i + 1], ib[i + 1])
        geom.add_face(ob[i], ib[i + 1], ib[i])
    geom.add_face(ot[0], ob[0], ib[0])
    geom.add_face(ot[0], ib[0], it[0])
    geom.add_face(ot[-1], it[-1], ib[-1])
    geom.add_face(ot[-1], ib[-1], ob[-1])
    return geom


def _dome_front_wall(y, z_top, z_bottom, half_width, thickness=0.004) -> MeshGeometry:
    """Flat mesh panel at fixed Y (dome front) from z_top down to z_bottom."""
    y2 = y - thickness
    geom = MeshGeometry()
    otl = geom.add_vertex(-half_width, y, z_top)
    otr = geom.add_vertex(half_width, y, z_top)
    obl = geom.add_vertex(-half_width, y, z_bottom)
    obr = geom.add_vertex(half_width, y, z_bottom)
    itl = geom.add_vertex(-half_width, y2, z_top)
    itr = geom.add_vertex(half_width, y2, z_top)
    ibl = geom.add_vertex(-half_width, y2, z_bottom)
    ibr = geom.add_vertex(half_width, y2, z_bottom)
    for a, b, c, d in (
        (otl, otr, obr, obl),
        (itl, ibl, ibr, itr),
        (otl, itl, itr, otr),
        (obl, obr, ibr, ibl),
        (otl, obl, ibl, itl),
        (otr, itr, ibr, obr),
    ):
        geom.add_face(a, b, c)
        geom.add_face(a, c, d)
    return geom


def _add_wheel(part, prefix, *, tire_radius, tire_width, mats) -> None:
    """Tire + spoked rim + hub cap (origin A `_add_wheel`, primitives preserved)."""
    rim_radius = tire_radius * 0.72
    part.visual(
        _mesh(
            TireGeometry(
                tire_radius,
                tire_width,
                inner_radius=rim_radius * 0.98,
                tread=TireTread(style="circumferential", depth=tire_radius * 0.030, count=4),
                grooves=(TireGroove(center_offset=0.0, width=tire_width * 0.11, depth=tire_radius * 0.012),),
                sidewall=TireSidewall(style="rounded", bulge=0.05),
            ),
            f"{prefix}_tire",
        ),
        material=mats["rubber"],
        name="tire", material_class_id="rubber.directional_grooved",
    )
    part.visual(
        _mesh(
            WheelGeometry(
                rim_radius,
                tire_width * 0.72,
                rim=WheelRim(
                    inner_radius=rim_radius * 0.62,
                    flange_height=tire_radius * 0.035,
                    flange_thickness=tire_width * 0.06,
                ),
                hub=WheelHub(
                    radius=rim_radius * 0.30,
                    width=tire_width * 0.62,
                    cap_style="domed",
                    bolt_pattern=BoltPattern(count=4, circle_diameter=rim_radius * 0.38, hole_diameter=tire_radius * 0.025),
                ),
                face=WheelFace(dish_depth=tire_width * 0.10, front_inset=tire_width * 0.04),
                spokes=WheelSpokes(style="straight", count=6, thickness=tire_radius * 0.020, window_radius=tire_radius * 0.045),
                bore=WheelBore(style="round", diameter=tire_radius * 0.10),
            ),
            f"{prefix}_wheel",
        ),
        material=mats["rim"],
        name="rim", material_class_id="metal.paint_coated",
    )
    part.visual(
        Cylinder(radius=rim_radius * 0.18, length=tire_width * 1.05),
        origin=Origin(rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["frame_tube"],
        name="hub_cap", material_class_id="metal.paint_coated",
    )


def _make_wheel(model, name, *, radius, width, mats):
    wheel = model.part(name)
    wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=radius, length=width), mass=0.5, origin=Origin(rpy=(0.0, pi / 2.0, 0.0))
    )
    _add_wheel(wheel, name, tire_radius=radius, tire_width=width, mats=mats)
    return wheel


def _add_caster_yoke(part, prefix, *, drop, mats) -> None:
    """Swivel-caster fork: kingpin + bearing housing + fork legs + axle (fork source
    `_add_caster_yoke`, adapted so the axle sits `drop` below the pivot)."""
    part.visual(Cylinder(radius=0.009, length=0.060), origin=Origin(xyz=(0.0, 0.0, 0.030)), material=mats["silver"], name="kingpin", material_class_id="metal.stainless_matte")
    part.visual(Cylinder(radius=0.024, length=0.028), origin=Origin(xyz=(0.0, 0.0, 0.0)), material=mats["plastic"], name="bearing_housing", material_class_id="plastic.opaque_glossy_molded")
    part.visual(Box((0.058, 0.030, 0.040)), origin=Origin(xyz=(0.0, 0.010, -0.024)), material=mats["plastic"], name="fork_crown", material_class_id="plastic.opaque_glossy_molded")
    for label, side in SIDES:
        _tube(
            part,
            f"fork_leg_{label}",
            [(side * 0.028, 0.008, -0.040), (side * 0.040, 0.020, -drop * 0.63), (side * 0.040, 0.030, -drop)],
            0.007,
            mats["plastic"],
        )
    part.visual(
        Cylinder(radius=0.005, length=0.100),
        origin=Origin(xyz=(0.0, 0.030, -drop), rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["silver"],
        name="axle", material_class_id="metal.stainless_matte",
    )


# ===========================================================================
# Frame root (universal fixed champagne tubular skeleton + storage basket).
# ===========================================================================
def _build_frame(model, r: ResolvedPetStrollerConfig, mats):
    frame = model.part("frame")
    frame.inertial = Inertial.from_geometry(
        Box((0.88, 1.35, 1.05)), mass=11.0, origin=Origin(xyz=(0.0, 0.0, 0.52))
    )
    hw = r.half_w

    # Top rim loop + side rails (champagne tubes) at the cabin mouth.
    top_rim_points = [
        (hw - 0.01, 0.43, 0.675), (hw + 0.01, 0.18, 0.690), (hw - 0.01, -0.42, 0.685),
        (0.00, -0.48, 0.690), (-hw + 0.01, -0.42, 0.685), (-hw - 0.01, 0.18, 0.690),
        (-hw + 0.01, 0.43, 0.675), (0.00, 0.48, 0.675), (hw - 0.01, 0.43, 0.675),
    ]
    frame.visual(
        _mesh(tube_from_spline_points(top_rim_points, radius=0.018, samples_per_segment=10, radial_segments=14, closed_spline=True), "top_rim"),
        material=mats["frame_tube"], name="top_rim", material_class_id="metal.paint_coated",
    )
    for label, side in SIDES:
        x = side * (hw - 0.02)
        _tube(frame, f"side_rail_{label}", [(x, 0.43, 0.67), (x, 0.08, 0.66), (x, -0.32, 0.71), (x, -0.47, 0.86)], 0.014, mats["frame_tube"])

    # Lower storage basket. The side panels reach inboard onto the lower side loops
    # (x=±0.28·scale) so the whole basket welds into the frame island.
    frame.visual(Box((0.54 * r.cabin_width_scale, 0.55, 0.026)), origin=Origin(xyz=(0.0, -0.02, 0.285)), material=mats["storage"], name="storage_base", material_class_id="fabric.open_mesh")
    for label, side in SIDES:
        frame.visual(Box((0.055, 0.55, 0.120)), origin=Origin(xyz=(side * 0.29 * r.cabin_width_scale, -0.02, 0.335)), material=mats["storage"], name=f"storage_side_{label}", material_class_id="fabric.open_mesh")
        frame.visual(Box((0.030, 0.035, 0.100)), origin=Origin(xyz=(side * 0.24, -0.02, 0.330)), material=mats["fabric"], name=f"storage_hanger_{label}", material_class_id="fabric.canvas")

    # Tubular undercarriage: lower side loops, folding diagonals, rear uprights, fold hinges.
    # Front ends kept inboard + rearward (y<=0.50) so they clear the front wheels /
    # the swivel casters' swept circle.
    for label, side in SIDES:
        x = side * 0.28 * r.cabin_width_scale
        _tube(frame, f"lower_side_loop_{label}", [(x, 0.50, 0.16), (x, 0.30, 0.36), (x, 0.02, 0.46), (x, -0.56, 0.18)], 0.016, mats["frame_tube"])
        _tube(frame, f"folding_diagonal_{label}", [(x, 0.48, 0.28), (x, 0.12, 0.67), (x, -0.38, 0.64)], 0.013, mats["frame_tube"])
        _tube(frame, f"rear_upright_{label}", [(x, -0.54, 0.18), (x, -0.38, 0.62), (x, -0.18, 0.86)], 0.015, mats["frame_tube"])
        frame.visual(Box((0.055, 0.080, 0.080)), origin=Origin(xyz=(x, -0.38, 0.625)), material=mats["plastic"], name=f"fold_hinge_{label}", material_class_id="plastic.opaque_glossy_molded")
        frame.visual(Cylinder(radius=0.028, length=0.030), origin=Origin(xyz=(x, -0.38, 0.625), rpy=(0.0, pi / 2.0, 0.0)), material=mats["silver"], name=f"hinge_disc_{label}", material_class_id="metal.stainless_matte")
        # Rim strut: welds the high cabin-mouth loop (top_rim + side_rail) down to
        # the folding diagonal so the mouth ring is part of the frame island.
        _tube(frame, f"rim_strut_{label}", [(x, 0.12, 0.67), (side * (hw - 0.02), 0.08, 0.66)], 0.013, mats["frame_tube"])

    # Front cross tie: welds the two undercarriage sides at the front (through the
    # folding-diagonal front nodes) and provides the single mount node every chassis
    # front (fixed fork / jogger fork / swivel caster mount) anchors to.
    _tube(frame, "front_cross_tube", [(-0.28 * r.cabin_width_scale, 0.48, 0.28), (0.0, 0.50, 0.27), (0.28 * r.cabin_width_scale, 0.48, 0.28)], 0.014, mats["frame_tube"])

    # Rear axle tube (shared by every chassis).
    _tube(frame, "rear_axle_tube", [(-hw + 0.02, REAR_AXLE_Y, r.rear_radius), (hw - 0.02, REAR_AXLE_Y, r.rear_radius)], 0.015, mats["plastic"])
    for label, side in SIDES:
        # Bracket enlarged to bridge the rear axle tube up to the rear upright for all
        # rear-radius values (welds the axle assembly + both sides into the island).
        frame.visual(Box((0.060, 0.14, 0.160)), origin=Origin(xyz=(side * 0.30 * r.cabin_width_scale, REAR_AXLE_Y + 0.015, r.rear_radius + 0.05)), material=mats["plastic"], name=f"rear_axle_bracket_{label}", material_class_id="plastic.opaque_glossy_molded")
        frame.visual(Cylinder(radius=0.006, length=0.130), origin=Origin(xyz=(side * r.rear_wheel_x, REAR_AXLE_Y, r.rear_radius), rpy=(0.0, pi / 2.0, 0.0)), material=mats["silver"], name=f"rear_axle_stub_{label}", material_class_id="metal.stainless_matte")
    return frame


# ===========================================================================
# Slot A: chassis
# ===========================================================================
def _spin_joint(model, frame, name, wheel, xyz, *, parent=None):
    model.articulation(
        name, ArticulationType.CONTINUOUS, parent=(parent or frame), child=wheel,
        origin=Origin(xyz=xyz), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=25.0),
    )


def _build_rear_wheels(model, frame, r, mats):
    for label, side in SIDES:
        w = _make_wheel(model, f"rear_wheel_{label}", radius=r.rear_radius, width=0.060, mats=mats)
        _spin_joint(model, frame, f"rear_wheel_spin_{label}", w, (side * r.rear_wheel_x, REAR_AXLE_Y, r.rear_radius))


def _build_chassis_four_wheel_fixed(model, frame, r, mats):
    _build_rear_wheels(model, frame, r, mats)
    # Front axle hardware + springs + fenders + fixed forks.
    _tube(frame, "front_axle_tube", [(-0.31 * r.cabin_width_scale, FRONT_AXLE_Y, r.front_radius), (0.31 * r.cabin_width_scale, FRONT_AXLE_Y, r.front_radius)], 0.013, mats["plastic"])
    for label, side in SIDES:
        x = side * 0.30 * r.cabin_width_scale
        # Fork top routes back onto the front cross tie so the front assembly welds
        # into the frame island.
        _tube(frame, f"front_fork_{label}", [(x, FRONT_AXLE_Y, r.front_radius), (x, 0.62, r.front_radius + 0.15), (x, 0.55, r.front_radius + 0.24), (side * 0.28 * r.cabin_width_scale, 0.49, 0.29)], 0.018, mats["plastic"])
        # Straight tie whose ends sit ON the axle-tube and folding-diagonal centerlines
        # (deep overlap, not a flaky spline cap-to-cap contact) so the whole front
        # assembly welds into the frame island even without the soft-cabin floor.
        _tube(frame, f"front_axle_tie_{label}", [(side * 0.29 * r.cabin_width_scale, FRONT_AXLE_Y, r.front_radius), (side * 0.28 * r.cabin_width_scale, 0.40, 0.367)], 0.013, mats["plastic"])
        frame.visual(Cylinder(radius=0.012, length=0.16), origin=Origin(xyz=(x, 0.61, r.front_radius + 0.09)), material=mats["spring"], name=f"front_spring_{label}", material_class_id="metal.paint_coated")
        # Mudguard hovering just above the tire top (z=2·front_radius) for every
        # radius, so it never interpenetrates the wheel; still overlaps the fork/spring
        # cluster for connectivity.
        frame.visual(Box((0.10, 0.11, 0.030)), origin=Origin(xyz=(side * 0.32 * r.cabin_width_scale, 0.62, 2.0 * r.front_radius + 0.02)), material=mats["plastic"], name=f"front_fender_{label}", material_class_id="plastic.opaque_glossy_molded")
        frame.visual(Cylinder(radius=0.004, length=0.130), origin=Origin(xyz=(side * r.front_wheel_x, FRONT_AXLE_Y, r.front_radius), rpy=(0.0, pi / 2.0, 0.0)), material=mats["silver"], name=f"front_axle_stub_{label}", material_class_id="metal.stainless_matte")
        w = _make_wheel(model, f"front_wheel_{label}", radius=r.front_radius, width=0.050, mats=mats)
        _spin_joint(model, frame, f"front_wheel_spin_{label}", w, (side * r.front_wheel_x, FRONT_AXLE_Y, r.front_radius))


def _build_chassis_four_wheel_swivel(model, frame, r, mats):
    _build_rear_wheels(model, frame, r, mats)
    # Compact casters mounted forward of the frame; each swivels 360° so its wheel,
    # even reversed, sweeps a small circle that clears the frame tubes.
    socket_z = CASTER_WHEEL_R + CASTER_DROP
    for label, side in SIDES:
        x = side * r.front_wheel_x
        # Caster mount tube (from the front cross tie down/forward to the socket).
        _tube(frame, f"caster_mount_{label}", [(side * 0.28 * r.cabin_width_scale, 0.48, 0.29), (side * 0.28 * r.cabin_width_scale, 0.52, 0.42), (x, 0.60, socket_z + 0.06), (x, CASTER_Y, socket_z)], 0.016, mats["plastic"])
        frame.visual(Cylinder(radius=0.025, length=0.022), origin=Origin(xyz=(x, CASTER_Y, socket_z + 0.004)), material=mats["plastic"], name=f"caster_socket_{label}", material_class_id="plastic.opaque_glossy_molded")
        # Caster yoke (swivel about +Z) and its front wheel (spin about X).
        yoke = model.part(f"caster_yoke_{label}")
        yoke.inertial = Inertial.from_geometry(Box((0.08, 0.06, 0.18)), mass=0.22, origin=Origin(xyz=(0.0, CASTER_TRAIL * 0.5, -CASTER_DROP * 0.5)))
        _add_caster_yoke(yoke, f"caster_yoke_{label}", drop=CASTER_DROP, mats=mats)
        model.articulation(
            f"front_caster_swivel_{label}", ArticulationType.CONTINUOUS, parent=frame, child=yoke,
            origin=Origin(xyz=(x, CASTER_Y, socket_z)), axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=3.0, velocity=8.0),
        )
        w = _make_wheel(model, f"front_wheel_{label}", radius=CASTER_WHEEL_R, width=0.046, mats=mats)
        _spin_joint(model, frame, f"front_wheel_spin_{label}", w, (0.0, CASTER_TRAIL, -CASTER_DROP), parent=yoke)


def _build_chassis_three_wheel_jogger(model, frame, r, mats):
    _build_rear_wheels(model, frame, r, mats)
    # Single centered front wheel on a fork (origin B, adapted). The fork legs start
    # from the front cross tie node so the jogger front welds into the frame island.
    for label, side in SIDES:
        _tube(frame, f"front_fork_{label}", [(0.0, 0.49, 0.28), (side * 0.055, FRONT_AXLE_Y - 0.12, r.front_radius + 0.20), (side * 0.055, FRONT_AXLE_Y - 0.02, r.front_radius + 0.09), (side * 0.055, FRONT_AXLE_Y, r.front_radius)], 0.012, mats["plastic"])
    frame.visual(Cylinder(radius=0.010, length=0.120), origin=Origin(xyz=(0.0, FRONT_AXLE_Y, r.front_radius), rpy=(0.0, pi / 2.0, 0.0)), material=mats["silver"], name="front_axle_stub_0", material_class_id="metal.stainless_matte")
    # Fender enlarged/lowered so it straddles both fork legs (welds into the island).
    frame.visual(Box((0.16, 0.16, 0.050)), origin=Origin(xyz=(0.0, FRONT_AXLE_Y - 0.05, r.front_radius + 0.16)), material=mats["plastic"], name="front_fender_0", material_class_id="plastic.opaque_glossy_molded")
    w = _make_wheel(model, "front_wheel_0", radius=r.front_radius, width=0.052, mats=mats)
    _spin_joint(model, frame, "front_wheel_spin_0", w, (0.0, FRONT_AXLE_Y, r.front_radius))


def _build_chassis(model, frame, r, mats):
    {
        "four_wheel_fixed": _build_chassis_four_wheel_fixed,
        "four_wheel_swivel": _build_chassis_four_wheel_swivel,
        "three_wheel_jogger": _build_chassis_three_wheel_jogger,
    }[r.chassis](model, frame, r, mats)


# ===========================================================================
# Slot B: cabin_form
# ===========================================================================
def _build_cabin_soft_fabric(model, frame, r, mats):
    hw = r.half_w
    frame.visual(Box((2 * hw - 0.06, 0.88, 0.035)), origin=Origin(xyz=(0.0, 0.0, FLOOR_Z)), material=mats["fabric"], name="basket_floor", material_class_id="fabric.canvas")
    for label, side in SIDES:
        frame.visual(Box((0.026, 0.91, 0.245)), origin=Origin(xyz=(side * hw, 0.0, 0.555)), material=mats["fabric"], name=f"side_wall_{label}", material_class_id="fabric.canvas")
    frame.visual(Box((2 * hw - 0.06, 0.050, 0.180)), origin=Origin(xyz=(0.0, FRONT_Y - 0.025, 0.530)), material=mats["fabric"], name="front_lip", material_class_id="fabric.canvas")
    frame.visual(Box((2 * hw - 0.06, 0.034, 0.305)), origin=Origin(xyz=(0.0, REAR_Y + 0.005, 0.595)), material=mats["fabric"], name="rear_panel", material_class_id="fabric.canvas")
    # Perforated mesh windows (host-conformal, sit in the wall faces).
    side_panel = _mesh(PerforatedPanelGeometry((0.18, 0.32), 0.004, hole_diameter=0.010, pitch=(0.030, 0.030), frame=0.010, stagger=True), "side_mesh_window")
    for label, side in SIDES:
        frame.visual(side_panel, origin=Origin(xyz=(side * (hw + 0.014), 0.10, 0.555), rpy=(0.0, pi / 2.0, 0.0)), material=mats["mesh_window"], name=f"mesh_window_{label}", material_class_id="fabric.open_mesh")
    front_panel = _mesh(PerforatedPanelGeometry((0.30, 0.16), 0.004, hole_diameter=0.009, pitch=(0.028, 0.028), frame=0.010, stagger=True), "front_mesh_window")
    frame.visual(front_panel, origin=Origin(xyz=(0.0, FRONT_Y - 0.002, 0.545), rpy=(pi / 2.0, 0.0, 0.0)), material=mats["mesh_window"], name="front_mesh_window", material_class_id="fabric.open_mesh")


def _build_cabin_rigid_pod(model, frame, r, mats):
    """Rigid molded carrier pod: hollow rounded-rect tub (ExtrudeWithHoles Mesh,
    Volumetric Envelope Form) seated FIXED in a frame saddle cradle. cadquery is
    unavailable in this environment, so the tub is a mesh envelope, NOT a Box
    downgrade (Rule 3: primitive family = curved-corner extruded shell preserved)."""
    # Pod fits INSIDE the frame's lower side loops / folding diagonals (x=±0.28·scale)
    # for EVERY cabin_width_scale: the outer rim (pod_w+0.024)/2 must clear 0.28·scale,
    # so pod width scales with the frame (not a fixed 0.50 that collides when narrow).
    pod_w = min(0.56 * r.cabin_width_scale - 0.09, 2 * r.half_w - 0.10)
    pod_l = 0.56
    # Frame saddle cradle: a central mount pad (FIXED origin sits on its top face at
    # z=FLOOR_Z), a cradle crossbar, and two clip saddle brackets.
    frame.visual(Box((0.16, 0.16, 0.030)), origin=Origin(xyz=(0.0, 0.0, FLOOR_Z - 0.015)), material=mats["plastic"], name="pod_mount_pad", material_class_id="plastic.opaque_glossy_molded")
    _tube(frame, "pod_cradle_bar", [(-pod_w * 0.45, 0.0, FLOOR_Z - 0.006), (pod_w * 0.45, 0.0, FLOOR_Z - 0.006)], 0.014, mats["plastic"])
    for label, side in SIDES:
        frame.visual(Box((0.065, 0.100, 0.035)), origin=Origin(xyz=(side * 0.18, 0.0, FLOOR_Z - 0.012)), material=mats["plastic"], name=f"pod_saddle_{label}", material_class_id="plastic.opaque_glossy_molded")
        frame.visual(Box((0.040, 0.075, 0.018)), origin=Origin(xyz=(side * 0.18, 0.0, FLOOR_Z + 0.007)), material=mats["silver"], name=f"pod_clip_tab_{label}", material_class_id="metal.stainless_matte")
        # Cradle leg: welds the pod mount cluster out to the lower side loop. Runs
        # inboard+rearward first, then crosses the pod-wall x-band LOW (z<=0.41, below
        # the pod wall/vent which start at world z~0.447) and lands on the loop at
        # z=0.344 — so it clears the pod side vent and wall entirely, for all scales.
        _tube(frame, f"pod_cradle_leg_{label}", [(side * pod_w * 0.45, 0.0, FLOOR_Z - 0.006), (side * pod_w * 0.45, -0.20, 0.41), (side * 0.28 * r.cabin_width_scale, -0.22, 0.344)], 0.012, mats["plastic"])

    pod = model.part("pod")
    pod.inertial = Inertial.from_geometry(Box((pod_w, pod_l, 0.17)), mass=2.8, origin=Origin(xyz=(0.0, 0.0, 0.085)))
    pod_h = 0.16
    wall = 0.012
    corner_r = 0.030
    floor_thk = 0.012
    outer = rounded_rect_profile(pod_w, pod_l, corner_r, corner_segments=8)
    inner = rounded_rect_profile(pod_w - 2 * wall, pod_l - 2 * wall, max(corner_r - wall, 0.008), corner_segments=8)
    wall_ring = ExtrudeWithHolesGeometry(outer, [inner], pod_h - floor_thk, center=True).translate(0.0, 0.0, floor_thk + (pod_h - floor_thk) * 0.5)
    floor = ExtrudeGeometry(outer, floor_thk, center=True).translate(0.0, 0.0, floor_thk * 0.5)
    pod.visual(_mesh(wall_ring, "pod_wall"), material=mats["pod"], name="pod_wall", material_class_id="plastic.opaque_glossy_molded")
    pod.visual(_mesh(floor, "pod_floor"), material=mats["pod"], name="pod_floor", material_class_id="plastic.opaque_glossy_molded")
    # Integral top rim lip (a slightly wider thin ring at the mouth).
    rim_outer = rounded_rect_profile(pod_w + 0.024, pod_l + 0.024, corner_r + 0.012, corner_segments=8)
    rim = ExtrudeWithHolesGeometry(rim_outer, [inner], 0.012, center=True).translate(0.0, 0.0, pod_h - 0.006)
    pod.visual(_mesh(rim, "pod_top_rim"), material=mats["plastic"], name="pod_top_rim", material_class_id="plastic.opaque_glossy_molded")
    # Ventilation grilles on the two long sides and the front.
    side_vent = _mesh(PerforatedPanelGeometry((0.24, 0.10), 0.005, hole_diameter=0.010, pitch=(0.030, 0.030), frame=0.010, stagger=True), "pod_side_vent")
    for label, side in SIDES:
        pod.visual(side_vent, origin=Origin(xyz=(side * (pod_w / 2.0 + 0.003), 0.0, 0.08), rpy=(0.0, pi / 2.0, 0.0)), material=mats["mesh_window"], name=f"pod_vent_{label}", material_class_id="fabric.open_mesh")
    front_vent = _mesh(PerforatedPanelGeometry((0.30, 0.10), 0.016, hole_diameter=0.010, pitch=(0.030, 0.030), frame=0.010, stagger=True), "pod_front_vent")
    pod.visual(front_vent, origin=Origin(xyz=(0.0, pod_l / 2.0 - 0.006, 0.08), rpy=(pi / 2.0, 0.0, 0.0)), material=mats["mesh_window"], name="pod_front_vent", material_class_id="fabric.open_mesh")
    # Clip receivers mate with the frame saddle clip tabs.
    for label, side in SIDES:
        pod.visual(Box((0.050, 0.080, 0.020)), origin=Origin(xyz=(side * 0.18, 0.0, 0.008)), material=mats["plastic"], name=f"pod_clip_receiver_{label}", material_class_id="plastic.opaque_glossy_molded")
    # FIXED weld: pod local (0,0,0) (floor bottom center) lands on the cradle bar.
    model.articulation("frame_to_pod", ArticulationType.FIXED, parent=frame, child=pod, origin=Origin(xyz=(0.0, 0.0, FLOOR_Z)))


def _build_cabin_form(model, frame, r, mats):
    {
        "soft_fabric_cabin": _build_cabin_soft_fabric,
        "rigid_carrier_pod": _build_cabin_rigid_pod,
    }[r.cabin_form](model, frame, r, mats)


# ===========================================================================
# Slot C: top_access
# ===========================================================================
def _frame_canopy_hardware(frame, r, mats):
    for label, side in SIDES:
        frame.visual(Box((0.035, 0.085, 0.100)), origin=Origin(xyz=(side * (r.half_w + 0.03), -0.485, 0.705)), material=mats["plastic"], name=f"canopy_hinge_bracket_{label}", material_class_id="plastic.opaque_glossy_molded")
        frame.visual(Cylinder(radius=0.006, length=0.100), origin=Origin(xyz=(side * (r.half_w - 0.01), -0.520, 0.735), rpy=(0.0, pi / 2.0, 0.0)), material=mats["silver"], name=f"canopy_hinge_pin_{label}", material_class_id="metal.stainless_matte")
        # Tie the outboard hinge bracket (+ its captured pin) back to the top_rim so
        # the canopy-hinge hardware welds into the frame island (routed rear/outboard,
        # clear of the canopy ribs which sit further rear at y~-0.54).
        _tube(frame, f"canopy_hinge_tie_{label}", [(side * (r.half_w + 0.03), -0.485, 0.705), (side * (r.half_w - 0.01), -0.42, 0.685)], 0.010, mats["frame_tube"])


def _canopy_hinge_collars(canopy, r, mats):
    for label, side in SIDES:
        canopy.visual(Cylinder(radius=0.026, length=0.030), origin=Origin(xyz=(side * (r.half_w - 0.01), -0.02, 0.00), rpy=(0.0, pi / 2.0, 0.0)), material=mats["plastic"], name=f"canopy_hinge_collar_{label}", material_class_id="plastic.opaque_glossy_molded")
    _tube(canopy, "canopy_hinge_sleeve", [(-r.half_w, -0.04, 0.00), (r.half_w, -0.04, 0.00)], 0.012, mats["frame_tube"])


def _make_canopy_part(model):
    canopy = model.part("canopy")
    canopy.inertial = Inertial.from_geometry(Box((0.74, 0.62, 0.38)), mass=1.2, origin=Origin(xyz=(0.0, 0.22, 0.23)))
    return canopy


def _emit_canopy_joint(model, frame, canopy, *, upper):
    model.articulation(
        "canopy_hinge", ArticulationType.REVOLUTE, parent=frame, child=canopy,
        origin=Origin(xyz=CANOPY_HINGE), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=1.2, lower=-0.20, upper=upper),
    )


def _build_top_fold_back_canopy(model, frame, r, mats):
    _frame_canopy_hardware(frame, r, mats)
    canopy = _make_canopy_part(model)
    width = 2 * (r.half_w - 0.01)
    profile = [(-0.04, 0.00), (-0.06, 0.16), (0.15, 0.35), (0.50, 0.15)]
    canopy.visual(_mesh(_canopy_shell_from_side_path(profile, width=width, thickness=0.012), "canopy_fabric"), material=mats["fabric"], name="canopy_fabric", material_class_id="fabric.canvas")
    for label, side in SIDES:
        _tube(canopy, f"canopy_rib_{label}", [(side * (r.half_w - 0.01), y, z) for y, z in profile], 0.014, mats["frame_tube"])
    _canopy_hinge_collars(canopy, r, mats)
    _tube(canopy, "canopy_front_bow", [(-r.half_w + 0.01, 0.50, 0.15), (0.0, 0.54, 0.16), (r.half_w - 0.01, 0.50, 0.15)], 0.012, mats["frame_tube"])
    _emit_canopy_joint(model, frame, canopy, upper=0.90)


def _build_top_enclosed_dome(model, frame, r, mats):
    """Full mesh dome (roof + side walls + front wall) that lifts open on the
    canopy hinge (enclosed_dome fork, adapted to A's axes). Fully encloses the
    cabin down to the rim; ③ Volumetric-Envelope reading."""
    _frame_canopy_hardware(frame, r, mats)
    canopy = _make_canopy_part(model)
    hw = r.half_w - 0.01
    width = 2 * hw
    # Arch profile in canopy-local (y, z): rear (hinge) -> forward, reaching the
    # cabin front. Cabin rim is world z=CABIN_TOP_Z -> local z = CABIN_TOP_Z-0.735.
    # Dome lower hem hovers just above the tubular mouth rim (top_rim tops out near
    # world z=0.693) instead of interpenetrating it: world ~0.72 -> local -0.015.
    rim_local_z = CABIN_TOP_Z - 0.695  # ~ -0.015
    profile = [(-0.05, 0.00), (-0.02, 0.20), (0.30, 0.36), (0.70, 0.30), (0.94, 0.10)]
    canopy.visual(_mesh(_canopy_shell_from_side_path(profile, width=width, thickness=0.012), "dome_roof"), material=mats["fabric"], name="dome_roof", material_class_id="fabric.canvas")
    # Side mesh walls dropping from the arch to the cabin rim.
    for label, side in SIDES:
        wall = _dome_side_wall(profile, side * hw, rim_local_z, thickness=0.004)
        canopy.visual(_mesh(wall, f"dome_side_wall_{label}"), material=mats["mesh_window"], name=f"dome_side_wall_{label}", material_class_id="fabric.open_mesh")
    # Front mesh wall from the arch front edge down to the cabin front rim.
    front_y, front_z = profile[-1]
    canopy.visual(_mesh(_dome_front_wall(front_y, front_z, rim_local_z, hw, thickness=0.004), "dome_front_wall"), material=mats["mesh_window"], name="dome_front_wall", material_class_id="fabric.open_mesh")
    for label, side in SIDES:
        _tube(canopy, f"canopy_rib_{label}", [(side * hw, y, z) for y, z in profile], 0.010, mats["frame_tube"])
    _canopy_hinge_collars(canopy, r, mats)
    canopy.visual(Cylinder(radius=0.010, length=width), origin=Origin(xyz=(0.0, front_y, rim_local_z), rpy=(0.0, pi / 2.0, 0.0)), material=mats["plastic"], name="canopy_front_lip", material_class_id="plastic.opaque_glossy_molded")
    # Open range capped at 0.85 rad: enough to lift the whole dome clear of the cabin
    # for access, but not so far that the tall roof swings back into the rear push
    # handle / telescoping mast (which live at world y=-0.74).
    _emit_canopy_joint(model, frame, canopy, upper=0.85)


def _build_top_front_door_canopy(model, frame, r, mats):
    """Arched fold-back canopy + a separate drop-down front door flap
    (front_door fork). Two REVOLUTE joints."""
    _build_top_fold_back_canopy(model, frame, r, mats)
    hw = r.half_w
    # Front hinge bar at the lower cabin front edge.
    _tube(frame, "front_hinge_bar", [(-0.28 * r.cabin_width_scale, FRONT_Y, 0.440), (0.28 * r.cabin_width_scale, FRONT_Y, 0.440)], 0.012, mats["plastic"])
    door = model.part("front_door")
    door.inertial = Inertial.from_geometry(Box((0.56, 0.020, 0.230)), mass=0.30, origin=Origin(xyz=(0.0, 0.0, 0.115)))
    door.visual(Box((2 * hw - 0.10, 0.016, 0.190)), origin=Origin(xyz=(0.0, 0.0, 0.115)), material=mats["fabric"], name="door_panel", material_class_id="fabric.canvas")
    door_mesh = _mesh(PerforatedPanelGeometry((0.40, 0.12), 0.004, hole_diameter=0.009, pitch=(0.028, 0.028), frame=0.010, stagger=True), "door_mesh_window")
    door.visual(door_mesh, origin=Origin(xyz=(0.0, 0.010, 0.118), rpy=(pi / 2.0, 0.0, 0.0)), material=mats["mesh_window"], name="door_mesh", material_class_id="fabric.open_mesh")
    door.visual(Box((2 * hw - 0.12, 0.028, 0.022)), origin=Origin(xyz=(0.0, 0.008, 0.011)), material=mats["plastic"], name="door_hinge_strip", material_class_id="plastic.opaque_glossy_molded")
    door.visual(Box((2 * hw - 0.12, 0.024, 0.016)), origin=Origin(xyz=(0.0, 0.0, 0.202)), material=mats["plastic"], name="door_top_rim", material_class_id="plastic.opaque_glossy_molded")
    door.visual(Box((0.038, 0.014, 0.020)), origin=Origin(xyz=(0.0, 0.013, 0.195)), material=mats["silver"], name="door_buckle_clip", material_class_id="metal.stainless_matte")
    model.articulation(
        "front_door_hinge", ArticulationType.REVOLUTE, parent=frame, child=door,
        origin=Origin(xyz=(0.0, FRONT_Y, 0.440)), axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=1.30),
    )


def _build_top_access(model, frame, r, mats):
    {
        "fold_back_canopy": _build_top_fold_back_canopy,
        "enclosed_mesh_dome": _build_top_enclosed_dome,
        "front_door_canopy": _build_top_front_door_canopy,
    }[r.top_access](model, frame, r, mats)


# ===========================================================================
# Slot D: push_handle
# ===========================================================================
def _frame_handle_hinge_hardware(frame, r, mats):
    for label, side in SIDES:
        # Routed LOW (z<=0.64 through the y=-0.52 region) so it clears the canopy
        # hinge collar that sits at z~0.735 there. Starts inside the fold hinge so it
        # welds into the frame island.
        _tube(frame, f"handle_support_{label}", [(side * 0.28 * r.cabin_width_scale, -0.40, 0.62), (side * 0.43, -0.62, 0.64), (side * 0.385, -0.82, 0.720)], 0.014, mats["frame_tube"])
        frame.visual(Box((0.030, 0.052, 0.055)), origin=Origin(xyz=(side * 0.385, -0.82, 0.720)), material=mats["plastic"], name=f"handle_hinge_bracket_{label}", material_class_id="plastic.opaque_glossy_molded")
        frame.visual(Cylinder(radius=0.006, length=0.100), origin=Origin(xyz=(side * 0.33, -0.82, 0.720), rpy=(0.0, pi / 2.0, 0.0)), material=mats["silver"], name=f"handle_hinge_pin_{label}", material_class_id="metal.stainless_matte")


def _handle_part(model):
    handle = model.part("handle")
    handle.inertial = Inertial.from_geometry(Box((0.78, 0.62, 0.56)), mass=1.6, origin=Origin(xyz=(0.0, -0.30, 0.34)))
    return handle


def _build_handle_u_fold(model, frame, r, mats):
    _frame_handle_hinge_hardware(frame, r, mats)
    handle = _handle_part(model)
    pts = [
        (-0.33, 0.00, 0.00), (-0.34, -0.22, 0.28), (-0.31, -0.50, 0.54), (-0.16, -0.60, 0.60),
        (0.00, -0.63, 0.61), (0.16, -0.60, 0.60), (0.31, -0.50, 0.54), (0.34, -0.22, 0.28), (0.33, 0.00, 0.00),
    ]
    handle.visual(_mesh(tube_from_spline_points(pts, radius=0.016, samples_per_segment=10, radial_segments=14), "handle_tube"), material=mats["frame_tube"], name="handle_tube", material_class_id="metal.paint_coated")
    handle.visual(Cylinder(radius=0.024, length=0.36), origin=Origin(xyz=(0.0, -0.625, 0.61), rpy=(0.0, pi / 2.0, 0.0)), material=mats["grip"], name="handle_grip", material_class_id="rubber.sponge_foam")
    for label, side in SIDES:
        handle.visual(Cylinder(radius=0.029, length=0.026), origin=Origin(xyz=(side * 0.33, 0.00, 0.00), rpy=(0.0, pi / 2.0, 0.0)), material=mats["plastic"], name=f"handle_pivot_{label}", material_class_id="plastic.opaque_glossy_molded")
        handle.visual(Box((0.055, 0.040, 0.040)), origin=Origin(xyz=(side * 0.31, -0.24, 0.30)), material=mats["plastic"], name=f"handle_clamp_{label}", material_class_id="plastic.opaque_glossy_molded")
    model.articulation(
        "handle_hinge", ArticulationType.REVOLUTE, parent=frame, child=handle,
        origin=Origin(xyz=HANDLE_HINGE), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.0, lower=0.0, upper=0.95),
    )


def _build_handle_swing_bar(model, frame, r, mats):
    """Two straight side arms + a transverse foam grip (origin B, adapted to A):
    a single-fold swing handle, structurally distinct from the U-tube."""
    _frame_handle_hinge_hardware(frame, r, mats)
    handle = _handle_part(model)
    for label, side in SIDES:
        _tube(handle, f"handle_arm_{label}", [(side * 0.33, 0.00, 0.00), (side * 0.32, -0.10, 0.16), (side * 0.30, -0.14, 0.30)], 0.014, mats["frame_tube"])
        handle.visual(Cylinder(radius=0.029, length=0.026), origin=Origin(xyz=(side * 0.33, 0.00, 0.00), rpy=(0.0, pi / 2.0, 0.0)), material=mats["plastic"], name=f"handle_pivot_{label}", material_class_id="plastic.opaque_glossy_molded")
    _tube(handle, "foam_grip", [(-0.30, -0.14, 0.30), (0.0, -0.16, 0.315), (0.30, -0.14, 0.30)], 0.024, mats["grip"])
    handle.visual(Box((0.050, 0.050, 0.070)), origin=Origin(xyz=(-0.29, -0.10, 0.09)), material=mats["plastic"], name="fold_latch", material_class_id="plastic.opaque_glossy_molded")
    model.articulation(
        "handle_hinge", ArticulationType.REVOLUTE, parent=frame, child=handle,
        origin=Origin(xyz=HANDLE_HINGE), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.5, lower=-0.65, upper=0.35),
    )


def _build_handle_telescoping(model, frame, r, mats):
    """Telescoping height-adjust handle: fixed outer sleeves on the frame; the
    inner U-tube slides out (PRISMATIC). Telescoping fork, adapted to A."""
    # Rear telescoping mast: short support arms tie two fixed vertical outer sleeves
    # to the rear-upright tops, positioned BEHIND the canopy's full open-swing rear
    # extent (the fold-back canopy's rear rib sweeps back to world y=-0.66 at the
    # open limit, so the mast sits at y=-0.74). The inner U-tube slides straight UP
    # (axis +Z, no forward lean), so it never enters the fold-back canopy / dome
    # sweep over the cabin, at rest, folded open, or fully extended.
    my = -0.74
    sx = 0.30
    for label, side in SIDES:
        _tube(
            frame, f"telescope_support_{label}",
            [(side * 0.28 * r.cabin_width_scale, -0.38, 0.62), (side * sx, -0.58, 0.58), (side * sx, my, 0.52)],
            0.015, mats["frame_tube"],
        )
        _tube(frame, f"telescope_sleeve_{label}", [(side * sx, my, 0.44), (side * sx, my, 0.66)], 0.022, mats["plastic"])
    handle = model.part("handle")
    handle.inertial = Inertial.from_geometry(Box((0.62, 0.14, 0.60)), mass=1.4, origin=Origin(xyz=(0.0, 0.0, 0.22)))
    # Local frame origin = prismatic joint origin at q=0 (world 0, my, 0.50).
    # Straight vertical U-tube (constant local y=0).
    pts = [
        (-sx, 0.00, -0.06), (-sx, 0.00, 0.06), (-sx, 0.00, 0.18), (-sx + 0.02, 0.00, 0.30),
        (-sx + 0.10, 0.00, 0.40), (-0.10, 0.00, 0.46), (0.00, 0.00, 0.47), (0.10, 0.00, 0.46),
        (sx - 0.10, 0.00, 0.40), (sx - 0.02, 0.00, 0.30), (sx, 0.00, 0.18), (sx, 0.00, 0.06), (sx, 0.00, -0.06),
    ]
    handle.visual(_mesh(tube_from_spline_points(pts, radius=0.016, samples_per_segment=10, radial_segments=14), "handle_tube"), material=mats["frame_tube"], name="handle_tube", material_class_id="metal.paint_coated")
    handle.visual(Cylinder(radius=0.024, length=0.30), origin=Origin(xyz=(0.0, 0.00, 0.47), rpy=(0.0, pi / 2.0, 0.0)), material=mats["grip"], name="handle_grip", material_class_id="rubber.sponge_foam")
    for label, side in SIDES:
        handle.visual(Cylinder(radius=0.024, length=0.022), origin=Origin(xyz=(side * sx, 0.00, 0.10), rpy=(0.0, pi / 2.0, 0.0)), material=mats["plastic"], name=f"handle_pivot_{label}", material_class_id="plastic.opaque_glossy_molded")
    model.articulation(
        "handle_slide", ArticulationType.PRISMATIC, parent=frame, child=handle,
        origin=Origin(xyz=(0.0, my, 0.50)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.5, lower=0.0, upper=0.18),
    )


def _build_handle_reversible(model, frame, r, mats):
    """Reversible swing-over handle: long arms on a high transverse pivot that sweep
    from rear over the canopy to the front (wide REVOLUTE about the width axis).
    Reversible fork, adapted to A."""
    pivot = (0.0, -0.10, 0.78)
    # Arms ride OUTBOARD of the canopy fabric (which spans only x=±(hw-0.01)) so the
    # swinging side arms sweep alongside — never through — the canopy sheet; only the
    # transverse grip crosses the top, and it clears the canopy peak on its wide arc.
    arm_x = r.half_w + 0.03
    # Frame-side pivot bar + collars + brackets + detent bosses (high on the rails).
    frame.visual(Cylinder(radius=0.018, length=2 * arm_x + 0.05), origin=Origin(xyz=(0.0, pivot[1], pivot[2]), rpy=(0.0, pi / 2.0, 0.0)), material=mats["plastic"], name="handle_pivot_bar", material_class_id="plastic.opaque_glossy_molded")
    for label, side in SIDES:
        frame.visual(Cylinder(radius=0.028, length=0.036), origin=Origin(xyz=(side * arm_x, pivot[1], pivot[2]), rpy=(0.0, pi / 2.0, 0.0)), material=mats["plastic"], name=f"handle_hinge_collar_{label}", material_class_id="plastic.opaque_glossy_molded")
        _tube(frame, f"handle_pivot_bracket_{label}", [(side * (r.half_w - 0.02), -0.20, 0.695), (side * arm_x, pivot[1], pivot[2])], 0.013, mats["frame_tube"])
        frame.visual(Box((0.035, 0.018, 0.025)), origin=Origin(xyz=(side * arm_x, pivot[1], pivot[2])), material=mats["silver"], name=f"handle_detent_boss_{label}", material_class_id="metal.stainless_matte")
    handle = model.part("handle")
    handle.inertial = Inertial.from_geometry(Box((0.80, 0.30, 0.58)), mass=1.6, origin=Origin(xyz=(0.0, 0.0, 0.28)))
    # Local frame at the pivot; +Z arms up at q=0.
    for label, side in SIDES:
        _tube(handle, f"handle_arm_{label}", [(side * arm_x, 0.0, 0.0), (side * arm_x, 0.0, 0.30), (side * (arm_x - 0.01), -0.02, 0.54)], 0.014, mats["frame_tube"])
        handle.visual(Cylinder(radius=0.024, length=0.024), origin=Origin(xyz=(side * arm_x, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)), material=mats["plastic"], name=f"handle_pivot_{label}", material_class_id="plastic.opaque_glossy_molded")
    _tube(handle, "foam_grip", [(-(arm_x - 0.01), -0.02, 0.54), (0.0, -0.02, 0.57), (arm_x - 0.01, -0.02, 0.54)], 0.022, mats["grip"])
    handle.visual(Box((0.024, 0.032, 0.020)), origin=Origin(xyz=(-arm_x, 0.0, 0.04)), material=mats["silver"], name="lock_pin", material_class_id="metal.stainless_matte")
    model.articulation(
        # axis -X so +q sweeps the arms FORWARD (+y) over the cabin (matches the
        # rear->front sweep assertion); -q reclines them toward the pusher. The rear
        # travel is capped at -0.45 (a normal handle recline) so the transverse grip
        # never reaches the folded-OPEN canopy's rear-swung sheet; the full forward
        # +1.35 is the reversible swing-over-the-top motion.
        "handle_hinge", ArticulationType.REVOLUTE, parent=frame, child=handle,
        origin=Origin(xyz=pivot), axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.5, lower=-0.45, upper=1.35),
    )


def _build_push_handle(model, frame, r, mats):
    {
        "u_fold_handle": _build_handle_u_fold,
        "swing_bar_handle": _build_handle_swing_bar,
        "telescoping_handle": _build_handle_telescoping,
        "reversible_handle": _build_handle_reversible,
    }[r.push_handle](model, frame, r, mats)


# ===========================================================================
# Assembly
# ===========================================================================
def build_pet_stroller(config: PetStrollerConfig | None = None, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {k: model.material(f"ps_{k}_{r.palette_style}", rgba=v) for k, v in PALETTES[r.palette_style].items()}

    frame = _build_frame(model, r, mats)
    _build_chassis(model, frame, r, mats)
    _build_cabin_form(model, frame, r, mats)
    _build_top_access(model, frame, r, mats)
    _build_push_handle(model, frame, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pet_stroller(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_pet_stroller(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _allow_captured_pins(ctx, model, r: ResolvedPetStrollerConfig) -> None:
    # Rear wheel axle stubs captured in hubs.
    for label, _s in SIDES:
        wname = f"rear_wheel_{label}"
        ctx.allow_overlap("frame", wname, elem_a=f"rear_axle_stub_{label}", elem_b="hub_cap", reason="Rear axle stub captured inside the spinning wheel hub.")
        ctx.expect_overlap("frame", wname, axes="xyz", elem_a=f"rear_axle_stub_{label}", elem_b="hub_cap", min_overlap=0.003, name=f"rear_wheel_{label}_captured")

    if r.chassis in ("four_wheel_fixed", "three_wheel_jogger"):
        fronts = ("0", "1") if r.chassis == "four_wheel_fixed" else ("0",)
        for label in fronts:
            wname = f"front_wheel_{label}"
            stub = f"front_axle_stub_{label}"
            ctx.allow_overlap("frame", wname, elem_a=stub, elem_b="hub_cap", reason="Front axle stub captured inside the spinning wheel hub.")
            ctx.allow_overlap("frame", wname, elem_a=stub, elem_b="rim", reason="Front axle stub passes through the wheel bore/rim (captured axle).")
            forks = (f"front_fork_{label}",) if r.chassis == "four_wheel_fixed" else ("front_fork_0", "front_fork_1")
            for fk in forks:
                ctx.allow_overlap("frame", wname, elem_a=fk, elem_b="tire", reason="Front fork straddles the front wheel at the axle.")

    if r.chassis == "four_wheel_swivel":
        for label, _s in SIDES:
            yoke = f"caster_yoke_{label}"
            wname = f"front_wheel_{label}"
            ctx.allow_overlap(yoke, wname, elem_a="axle", elem_b="hub_cap", reason="Caster yoke axle captured inside the front wheel hub.")
            ctx.allow_overlap(yoke, wname, elem_a="axle", elem_b="rim", reason="Caster yoke axle passes through the wheel bore/rim (captured axle; axle is fatter than the compact caster wheel's bore).")
            ctx.allow_overlap(yoke, wname, elem_a="fork_crown", elem_b="tire", reason="Caster fork crown spans just above the front wheel tire at the axle.")
            ctx.expect_overlap(yoke, wname, axes="xyz", elem_a="axle", elem_b="hub_cap", min_overlap=0.003, name=f"{yoke}_axle_captured")
            for elem in ("kingpin", "bearing_housing", "fork_crown", "fork_leg_0", "fork_leg_1"):
                ctx.allow_overlap("frame", yoke, elem_a=f"caster_socket_{label}", elem_b=elem, reason="Caster bearing/kingpin seats inside the frame socket at the swivel pivot.")
                ctx.allow_overlap("frame", yoke, elem_a=f"caster_mount_{label}", elem_b=elem, reason="Caster assembly interfaces with the frame mount tube at the swivel pivot.")
            ctx.expect_overlap("frame", yoke, axes="z", elem_a=f"caster_socket_{label}", elem_b="kingpin", min_overlap=0.003, name=f"{yoke}_kingpin_nested")

    # Canopy hinge pins captured by the canopy collars (canopy always present).
    for label, _s in SIDES:
        ctx.allow_overlap("frame", "canopy", elem_a=f"canopy_hinge_pin_{label}", elem_b=f"canopy_hinge_collar_{label}", reason="Canopy hinge pin captured inside the folding canopy collar.")
        ctx.expect_overlap("frame", "canopy", axes="xyz", elem_a=f"canopy_hinge_pin_{label}", elem_b=f"canopy_hinge_collar_{label}", min_overlap=0.003, name=f"canopy_hinge_pin_{label}_captured")
        ctx.allow_overlap("frame", "canopy", elem_a=f"canopy_hinge_pin_{label}", elem_b="canopy_hinge_sleeve", reason="Canopy hinge sleeve wraps the hinge pins.")

    # Enclosed mesh dome: its lower hem / roof seam SEATS on the tubular mouth rim
    # (top_rim + side_rails + soft-cabin front_lip) — the real closed-enclosure
    # contact (dome lifts clear of the rim when the hinge opens).
    if r.top_access == "enclosed_mesh_dome":
        dome_shell = ("dome_roof", "dome_side_wall_0", "dome_side_wall_1", "dome_front_wall", "canopy_rib_0", "canopy_rib_1", "canopy_front_lip")
        rim_seat = ("top_rim", "side_rail_0", "side_rail_1", "front_lip", "rear_panel", "side_wall_0", "side_wall_1", "canopy_hinge_bracket_0", "canopy_hinge_bracket_1", "canopy_hinge_tie_0", "canopy_hinge_tie_1")
        for de in dome_shell:
            for fe in rim_seat:
                ctx.allow_overlap("frame", "canopy", elem_a=fe, elem_b=de, reason="Enclosed dome lower seam seats/mounts on the cabin mouth rim (closed-enclosure contact).")

    # Front door: hinge strip wraps the frame front hinge bar; the closed door leaf
    # seats over the cabin front opening (front_lip / basket_floor / front mesh).
    if r.top_access == "front_door_canopy":
        ctx.allow_overlap("frame", "front_door", elem_a="front_hinge_bar", elem_b="door_hinge_strip", reason="Door hinge strip wraps around the frame front hinge bar (captured fabric hinge).")
        door_leaf = ("door_hinge_strip", "door_panel", "door_mesh", "door_top_rim")
        front_seat = ("front_lip", "basket_floor", "front_mesh_window", "front_hinge_bar")
        for dl in door_leaf:
            for fs in front_seat:
                ctx.allow_overlap("frame", "front_door", elem_a=fs, elem_b=dl, reason="Closed front door leaf seats over the cabin front opening (front lip / floor / mesh).")
        ctx.expect_overlap("frame", "front_door", axes="xyz", elem_a="front_hinge_bar", elem_b="door_hinge_strip", min_overlap=0.003, name="front_hinge_bar_captured")

    # Handle captures.
    if r.push_handle in ("u_fold_handle", "swing_bar_handle"):
        for label, _s in SIDES:
            ctx.allow_overlap("frame", "handle", elem_a=f"handle_hinge_pin_{label}", elem_b=f"handle_pivot_{label}", reason="Handle hinge pin captured inside the folding handle pivot collar.")
            pin_target = "handle_tube" if r.push_handle == "u_fold_handle" else f"handle_arm_{label}"
            ctx.allow_overlap("frame", "handle", elem_a=f"handle_hinge_pin_{label}", elem_b=pin_target, reason="Handle hinge pin passes through the handle at the pivot.")
            ctx.expect_overlap("frame", "handle", axes="xyz", elem_a=f"handle_hinge_pin_{label}", elem_b=f"handle_pivot_{label}", min_overlap=0.003, name=f"handle_hinge_pin_{label}_captured")
    elif r.push_handle == "telescoping_handle":
        # The telescoping tube + slide collars nest inside the rear frame cluster
        # (sleeves, uprights, folding diagonals, fold hinges) — a real captured
        # telescoping mechanism running through the rear frame.
        rear_frame_elems = (
            "telescope_sleeve_0", "telescope_sleeve_1",
            "telescope_support_0", "telescope_support_1",
            "rear_upright_0", "rear_upright_1", "rear_panel",
        )
        for fe in rear_frame_elems:
            for he in ("handle_tube", "handle_pivot_0", "handle_pivot_1"):
                ctx.allow_overlap("frame", "handle", elem_a=fe, elem_b=he, reason="Telescoping handle tube/collars nest inside the rear mast sleeves/support (captured slide mechanism).")
        for label, _s in SIDES:
            ctx.expect_overlap("frame", "handle", axes="xyz", elem_a=f"telescope_sleeve_{label}", elem_b="handle_tube", min_overlap=0.005, name=f"telescope_sleeve_{label}_retains_tube")
    elif r.push_handle == "reversible_handle":
        for label, _s in SIDES:
            for arm_elem in (f"handle_arm_{label}", f"handle_pivot_{label}"):
                ctx.allow_overlap("frame", "handle", elem_a="handle_pivot_bar", elem_b=arm_elem, reason="Handle arm/pivot rotates around the pivot bar (swing-over mechanism).")
                ctx.allow_overlap("frame", "handle", elem_a=f"handle_hinge_collar_{label}", elem_b=arm_elem, reason="Handle arm/pivot rotates within the pivot collar.")
                ctx.allow_overlap("frame", "handle", elem_a=f"handle_pivot_bracket_{label}", elem_b=arm_elem, reason="Pivot bracket carries the arm shaft through the swing-over pivot.")
                ctx.allow_overlap("frame", "handle", elem_a=f"handle_detent_boss_{label}", elem_b=arm_elem, reason="Detent boss sits at the arm base pivot (engages the swing-over lock).")
            ctx.allow_overlap("frame", "handle", elem_a=f"handle_detent_boss_{label}", elem_b="lock_pin", reason="Spring lock pin engages the detent boss at the swing-over end position.")
            # elem_a is on part_a ('frame'=collar), elem_b on part_b ('handle'=pivot).
            ctx.expect_overlap("frame", "handle", axes="yz", elem_a=f"handle_hinge_collar_{label}", elem_b=f"handle_pivot_{label}", min_overlap=0.003, name=f"handle_arm_{label}_captured")

    # Rigid pod: the pod's floor-level elements seat onto the frame mount cluster.
    if r.cabin_form == "rigid_carrier_pod":
        frame_mount = ("pod_mount_pad", "pod_cradle_bar", "pod_saddle_0", "pod_saddle_1", "pod_clip_tab_0", "pod_clip_tab_1", "pod_cradle_leg_0", "pod_cradle_leg_1")
        pod_floor_elems = ("pod_floor", "pod_wall", "pod_clip_receiver_0", "pod_clip_receiver_1")
        for fe in frame_mount:
            for pe in pod_floor_elems:
                ctx.allow_overlap("frame", "pod", elem_a=fe, elem_b=pe, reason="Pod floor/clip receivers seat onto the frame saddle-cradle mount cluster.")
        ctx.expect_contact("frame", "pod", elem_a="pod_mount_pad", elem_b="pod_floor", contact_tol=0.02, name="pod_seated_on_mount_pad")


def run_pet_stroller_tests(object_model: ArticulatedObject, config: PetStrollerConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    _allow_captured_pins(ctx, object_model, r)

    # ---- Identity: canopy + handle + >=3 spinning wheels. ----
    wheel_names = [f"rear_wheel_{i}" for i in ("0", "1")] + (
        [f"front_wheel_{i}" for i in ("0", "1")] if r.wheel_count == 4 else ["front_wheel_0"]
    )
    ctx.check(
        "pet_stroller_core_parts",
        object_model.get_part("frame") is not None
        and object_model.get_part("canopy") is not None
        and object_model.get_part("handle") is not None
        and all(object_model.get_part(n) is not None for n in wheel_names),
        details=f"wheels={wheel_names}",
    )
    spin_joints = ["rear_wheel_spin_0", "rear_wheel_spin_1"] + (
        ["front_wheel_spin_0", "front_wheel_spin_1"] if r.wheel_count == 4 else ["front_wheel_spin_0"]
    )
    ctx.check(
        "wheels_spin_and_top_hinges",
        all(object_model.get_articulation(n) is not None for n in spin_joints)
        and object_model.get_articulation("canopy_hinge") is not None,
        details=f"spins={spin_joints}",
    )

    # ---- Wheels touch the ground with round proportions. ----
    for wname in wheel_names:
        wheel = object_model.get_part(wname)
        aabb = ctx.part_world_aabb(wheel)
        if aabb is not None:
            mins, maxs = aabb
            ctx.check(f"{wname}_contacts_ground", abs(float(mins[2])) <= 0.010, details=f"aabb={aabb!r}")
            # Front wheels span joggers/fixed casters (>=0.19 dia) down to compact
            # swivel casters (~0.15 dia); rear wheels are always the large drive wheels.
            need = 0.13 if "front" in wname else 0.26
            ctx.check(f"{wname}_round_proportions", float(maxs[2] - mins[2]) > need, details=f"aabb={aabb!r}")

    # ---- Targeted mechanism poses. ----
    canopy = object_model.get_part("canopy")
    canopy_hinge = object_model.get_articulation("canopy_hinge")
    if canopy is not None and canopy_hinge is not None:
        rest = ctx.part_world_aabb(canopy)
        with ctx.pose({canopy_hinge: 0.70}):
            lifted = ctx.part_world_aabb(canopy)
        ctx.check("canopy_lifts_front_edge", rest is not None and lifted is not None and float(lifted[1][2]) > float(rest[1][2]) + 0.03, details=f"rest={rest}, lifted={lifted}")

    if r.top_access == "front_door_canopy":
        door = object_model.get_part("front_door")
        door_hinge = object_model.get_articulation("front_door_hinge")
        closed = ctx.part_world_aabb(door)
        with ctx.pose({door_hinge: 1.0}):
            opened = ctx.part_world_aabb(door)
        ctx.check("front_door_drops_when_opened", closed is not None and opened is not None and float(opened[1][2]) < float(closed[1][2]) - 0.05, details=f"closed={closed}, opened={opened}")

    handle = object_model.get_part("handle")
    if handle is not None:
        if r.push_handle == "telescoping_handle":
            j = object_model.get_articulation("handle_slide")
            rest = ctx.part_world_position(handle)
            with ctx.pose({j: 0.18}):
                ext = ctx.part_world_position(handle)
            if rest is not None and ext is not None:
                ctx.check("telescoping_handle_extends_up", float(ext[2]) > float(rest[2]) + 0.08, details=f"rest={rest}, ext={ext}")
        elif r.push_handle == "reversible_handle":
            j = object_model.get_articulation("handle_hinge")
            with ctx.pose({j: -1.30}):
                rear = ctx.part_world_aabb(handle)
            with ctx.pose({j: 1.30}):
                front = ctx.part_world_aabb(handle)
            ctx.check("reversible_handle_sweeps_rear_to_front", rear is not None and front is not None and float(front[1][1]) > float(rear[1][1]) + 0.15, details=f"rear={rear}, front={front}")
        else:
            j = object_model.get_articulation("handle_hinge")
            rest = ctx.part_world_aabb(handle)
            with ctx.pose({j: 0.30}):
                folded = ctx.part_world_aabb(handle)
            ctx.check("handle_folds", rest is not None and folded is not None and abs(float(folded[1][2]) - float(rest[1][2])) > 0.03, details=f"rest={rest}, folded={folded}")

    if r.chassis == "four_wheel_swivel":
        for label, _s in SIDES:
            sw = object_model.get_articulation(f"front_caster_swivel_{label}")
            wheel = object_model.get_part(f"front_wheel_{label}")
            if sw is not None and wheel is not None:
                rest = ctx.part_world_position(wheel)
                with ctx.pose({sw: pi / 2.0}):
                    turned = ctx.part_world_position(wheel)
                if rest is not None and turned is not None:
                    shift = ((turned[0] - rest[0]) ** 2 + (turned[1] - rest[1]) ** 2) ** 0.5
                    ctx.check(f"caster_swivel_{label}_displaces_wheel", shift > 0.015, details=f"rest={rest}, turned={turned}, shift={shift:.4f}")

    # ---- Rule 5: full-travel non-穿模 across sampled joint poses. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    # ---- Compiler-owned baseline. ----
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    return ctx.report()


__all__ = [
    "Chassis",
    "CabinForm",
    "TopAccess",
    "PushHandle",
    "PaletteStyle",
    "PetStrollerConfig",
    "ResolvedPetStrollerConfig",
    "build_pet_stroller",
    "build_seeded_pet_stroller",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_pet_stroller_tests",
]
