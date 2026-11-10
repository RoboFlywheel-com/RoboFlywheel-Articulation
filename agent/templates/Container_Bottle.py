# SPDX-License-Identifier: Apache-2.0

"""Container / Bottle modular template (`container_bottle`).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Container_Bottle.md`` and the
Container/Bottle fork-variant pool in articraft_data
(``rec_qwen_bottle_001_v*`` / ``rec_qwen_bottle_002_v*`` + the two clear
plastic bottle parents).

Structure (pattern = ``parallel_children``): a single hollow revolved (lathe)
``bottle_body`` root — base, barrel, shoulder taper, narrow neck with a visible
hollow mouth bore — that carries one of several articulated **closure** subtrees
plus an optional fixed **seal** detail at the neck rim. Three named module axes:

  * ``body_form`` (6): tall_cylindrical / square_shouldered / sports_grip /
    squeeze_conical / ribbed_water / canteen_oval — the lathe-body footprint,
    taper and wall treatment.
  * ``closure`` (5): screw_cap (PRISMATIC lift + CONTINUOUS spin) / flip_cap
    (REVOLUTE hinge) / swingtop_stopper (stopper geometry with PRISMATIC lift +
    CONTINUOUS spin) / pump_press (PRISMATIC press + REVOLUTE twist) /
    straw_spout (flip lid REVOLUTE over a fixed straw).
  * ``seal`` (3): none / gasket_ring (FIXED washer) / mouth_lip (rolled lip ring,
    body visual).

Every variant has at least one non-fixed joint (the closure mechanism). The
seated cap skirt / plug / gasket overlaps are intentional and declared with
element-scoped ``allow_overlap`` in ``run_container_bottle_tests``.

Source map (records under ``data/records/<rec>/revisions/rev_000001/model.py``):
  S1  = rec_qwen_bottle_001_v01  (tall body + screw cap + gasket + mouth rim)
  S13 = rec_qwen_bottle_001_v13  (sports body + flip cap / straw)
  S17 = rec_qwen_bottle_001_v17  (ribbed water body + swing-top stopper + lip)
  S25 = rec_qwen_bottle_001_v25  (squeeze body + pump/nozzle press+twist)
  P2  = rec_qwen_bottle_002_v01 / parent "tapered shoulder + screw cap"
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
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    max_joint_value,
    mesh_from_cadquery,
)

__modular__ = True

BodyForm = Literal[
    "tall_cylindrical",
    "square_shouldered",
    "sports_grip",
    "squeeze_conical",
    "ribbed_water",
    "canteen_oval",
]
Closure = Literal[
    "screw_cap",
    "flip_cap",
    "swingtop_stopper",
    "pump_press",
    "straw_spout",
]
Seal = Literal["none", "gasket_ring", "mouth_lip"]
MaterialStyle = Literal["clear_pet", "amber", "sports_smoke", "juice_green"]

BODY_FORMS: tuple[BodyForm, ...] = (
    "tall_cylindrical",
    "square_shouldered",
    "sports_grip",
    "squeeze_conical",
    "ribbed_water",
    "canteen_oval",
)
CLOSURES: tuple[Closure, ...] = (
    "screw_cap",
    "flip_cap",
    "swingtop_stopper",
    "pump_press",
    "straw_spout",
)
SEALS: tuple[Seal, ...] = ("none", "gasket_ring", "mouth_lip")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "clear_pet",
    "amber",
    "sports_smoke",
    "juice_green",
)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "clear_pet": {
        "body": (0.80, 0.86, 0.84, 0.25),
        "cap": (0.06, 0.06, 0.07, 1.0),
        "seal": (0.18, 0.18, 0.20, 1.0),
        "accent": (0.92, 0.92, 0.94, 0.9),
    },
    "amber": {
        "body": (0.78, 0.45, 0.14, 0.45),
        "cap": (0.16, 0.13, 0.10, 1.0),
        "seal": (0.90, 0.84, 0.72, 1.0),
        "accent": (0.95, 0.78, 0.40, 1.0),
    },
    "sports_smoke": {
        "body": (0.36, 0.40, 0.44, 0.38),
        "cap": (0.85, 0.20, 0.12, 1.0),
        "seal": (0.30, 0.30, 0.32, 1.0),
        "accent": (0.05, 0.05, 0.06, 1.0),
    },
    "juice_green": {
        "body": (0.62, 0.82, 0.55, 0.32),
        "cap": (0.07, 0.07, 0.08, 1.0),
        "seal": (0.20, 0.22, 0.18, 1.0),
        "accent": (0.95, 0.95, 0.96, 0.95),
    },
}

# ---- nominal base dimensions (meters), from S1 ----
_BODY_R = 0.032
_WALL = 0.0018
_BARREL_TOP_Z = 0.150  # where shoulder taper begins (nominal)
_SHOULDER_SPAN = 0.026  # shoulder taper height
_NECK_SPAN = 0.030  # neck height
_NECK_FACTOR = 0.40  # neck_r = body_r * factor


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _compatible_closure(body_form: BodyForm, closure: Closure) -> Closure:
    return closure


@dataclass(frozen=True)
class ContainerBottleConfig:
    body_form: BodyForm | None = None
    closure: Closure | None = None
    seal: Seal | None = None
    material_style: MaterialStyle = "clear_pet"
    body_radius: float = _BODY_R
    body_height_scale: float = 1.0
    oval_scale: float = 1.0
    groove_count: int = 8
    joint_limit_scale: float = 1.0
    name: str = "container_bottle"


@dataclass(frozen=True)
class ResolvedContainerBottleConfig:
    body_form: BodyForm
    closure: Closure
    seal: Seal
    material_style: MaterialStyle
    # Concrete geometry (meters).
    body_r: float
    oval_y: float  # Y-axis scale of the body footprint (1.0 except canteen_oval)
    wall: float
    barrel_top_z: float
    shoulder_top_z: float
    neck_r: float
    neck_top_z: float
    mouth_r: float
    groove_count: int
    joint_limit_scale: float
    name: str


def config_from_seed(seed: int) -> ContainerBottleConfig:
    rng = random.Random(seed)
    body_form = rng.choice(BODY_FORMS)
    return ContainerBottleConfig(
        body_form=body_form,
        closure=rng.choice(CLOSURES),
        seal=rng.choice(SEALS),
        material_style=rng.choice(MATERIAL_STYLES),
        body_radius=round(rng.uniform(0.026, 0.040), 4),
        body_height_scale=round(rng.uniform(0.85, 1.20), 4),
        oval_scale=round(rng.uniform(0.72, 1.0), 4),
        groove_count=rng.choice((6, 8, 10)),
        joint_limit_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_bottle_{seed}",
    )


def resolve_config(
    config: ContainerBottleConfig | None = None,
) -> ResolvedContainerBottleConfig:
    cfg = config or ContainerBottleConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    closure = _pick(cfg.closure, CLOSURES)
    closure = _compatible_closure(body_form, closure)
    seal = _pick(cfg.seal, SEALS)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)

    body_r = _clamp(cfg.body_radius, 0.026, 0.040)
    height_scale = _clamp(cfg.body_height_scale, 0.85, 1.20)

    # Per body_form barrel-height / shoulder factors.
    barrel_factor = 1.0
    shoulder_factor = 1.0
    if body_form == "square_shouldered":
        barrel_factor = 0.72
        shoulder_factor = 0.62  # sharper, shorter shoulder step
    elif body_form == "sports_grip":
        barrel_factor = 0.95
        body_r = _clamp(body_r * 1.08, 0.026, 0.044)
    elif body_form == "squeeze_conical":
        barrel_factor = 0.78
        shoulder_factor = 1.30  # longer taper to a slim neck
    elif body_form == "ribbed_water":
        barrel_factor = 0.80
    elif body_form == "canteen_oval":
        barrel_factor = 0.66
        body_r = _clamp(body_r * 1.10, 0.026, 0.046)

    barrel_top_z = _BARREL_TOP_Z * barrel_factor * height_scale
    shoulder_top_z = barrel_top_z + _SHOULDER_SPAN * shoulder_factor
    neck_top_z = shoulder_top_z + _NECK_SPAN

    # neck_r = f(body_r); squeeze/canteen get a slimmer neck.
    neck_factor = _NECK_FACTOR
    if body_form in ("squeeze_conical", "canteen_oval"):
        neck_factor = 0.34
    neck_r = body_r * neck_factor
    # Compatibility: neck must be clearly narrower than the barrel.
    neck_r = min(neck_r, body_r * 0.65)
    mouth_r = neck_r - _WALL - 0.0006

    oval_y = 1.0
    if body_form == "canteen_oval":
        oval_y = _clamp(cfg.oval_scale, 0.72, 1.0)

    groove_count = cfg.groove_count if cfg.groove_count in (6, 8, 10) else 8

    return ResolvedContainerBottleConfig(
        body_form=body_form,
        closure=closure,
        seal=seal,
        material_style=material_style,
        body_r=body_r,
        oval_y=oval_y,
        wall=_WALL,
        barrel_top_z=barrel_top_z,
        shoulder_top_z=shoulder_top_z,
        neck_r=neck_r,
        neck_top_z=neck_top_z,
        mouth_r=mouth_r,
        groove_count=groove_count,
        joint_limit_scale=_clamp(cfg.joint_limit_scale, 0.85, 1.10),
        name=cfg.name or "container_bottle",
    )


def slot_choices_for_config(
    config: ContainerBottleConfig | ResolvedContainerBottleConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedContainerBottleConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("closure", r.closure),
        ("seal", r.seal),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Body (Slot A): hollow revolved lathe shell. Adapted from S1 _bottle_shell
# (L71-L108), S13 grip waist (L58-L85), S17 grooves (L94-L108), S25 squeeze
# waist (L64-L97).
# ---------------------------------------------------------------------------
def _body_mesh(r: ResolvedContainerBottleConfig, *, assets: AssetContext | None):
    R = r.body_r
    nr = r.neck_r
    wp = cq.Workplane("XZ").moveTo(0.0, 0.0).lineTo(R - 0.006, 0.0)
    wp = wp.threePointArc((R, 0.006), (R, 0.012))

    if r.body_form == "sports_grip":
        # ergonomic grip waist (S13 L68-L72)
        wp = wp.lineTo(R, 0.030)
        wp = wp.lineTo(R - 0.003, 0.050)
        wp = wp.lineTo(R - 0.003, r.barrel_top_z - 0.040)
        wp = wp.lineTo(R, r.barrel_top_z - 0.020)
        wp = wp.lineTo(R, r.barrel_top_z)
    elif r.body_form == "squeeze_conical":
        # waisted soft-squeeze body (S25 L74-L83)
        wp = wp.lineTo(R, 0.030)
        wp = wp.threePointArc(
            (R - 0.004, r.barrel_top_z * 0.45), (R - 0.002, r.barrel_top_z * 0.60)
        )
        wp = wp.threePointArc((R, r.barrel_top_z * 0.82), (R, r.barrel_top_z))
    else:
        # straight barrel (tall / square / ribbed / canteen / default)
        wp = wp.lineTo(R, r.barrel_top_z)

    if r.body_form == "square_shouldered":
        # sharper square-ish shoulder step (P2)
        wp = wp.lineTo(R * 0.86, r.barrel_top_z + (r.shoulder_top_z - r.barrel_top_z) * 0.35)
        wp = wp.lineTo(nr, r.shoulder_top_z)
    else:
        wp = wp.threePointArc(
            ((R + nr) / 2.0, (r.barrel_top_z + r.shoulder_top_z) / 2.0 + 0.004),
            (nr, r.shoulder_top_z),
        )

    # neck
    wp = wp.lineTo(nr, r.neck_top_z)

    if r.seal == "mouth_lip":
        # rolled thicker lip ring step-out (S17 L80-L86)
        lip_or = nr + 0.003
        wp = wp.lineTo(lip_or, r.neck_top_z)
        wp = wp.lineTo(lip_or, r.neck_top_z + 0.005)
        wp = wp.lineTo(0.0, r.neck_top_z + 0.005).close()
    else:
        wp = wp.lineTo(0.0, r.neck_top_z).close()

    outer = wp.revolve(360.0, (0, 0, 0), (0, 1, 0))
    body = outer.faces(">Z").shell(-r.wall)

    # ribbed water: cut vertical grip grooves (S17 L94-L108)
    if r.body_form == "ribbed_water":
        n = r.groove_count
        depth = 0.005
        width = 0.008
        g_bot = 0.015
        g_top = r.barrel_top_z - 0.005
        gh = g_top - g_bot
        for i in range(n):
            ang = 2.0 * math.pi * i / n
            cx = (R - depth / 2.0) * math.cos(ang)
            cy = (R - depth / 2.0) * math.sin(ang)
            cutter = (
                cq.Workplane("XY")
                .transformed(offset=(cx, cy, g_bot + gh / 2.0), rotate=(0, 0, math.degrees(ang)))
                .box(depth, width, gh)
            )
            body = body.cut(cutter)

    # canteen_oval: flatten the footprint along Y (per-axis body scale) via an
    # OCC affine transform in _maybe_oval (CadQuery has no non-uniform scale).
    return mesh_from_cadquery(_maybe_oval(body, r), "container_bottle_body", assets=assets)


def _maybe_oval(solid, r: ResolvedContainerBottleConfig):
    """Apply a non-uniform Y scale for canteen_oval via an OCC affine transform."""
    if r.body_form != "canteen_oval" or r.oval_y >= 0.999:
        return solid
    try:
        from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform
        from OCP.gp import gp_GTrsf, gp_Mat, gp_XYZ

        shp = solid.val().wrapped if hasattr(solid, "val") else solid.wrapped
        gtr = gp_GTrsf()
        gtr.SetVectorialPart(gp_Mat(1.0, 0.0, 0.0, 0.0, r.oval_y, 0.0, 0.0, 0.0, 1.0))
        gtr.SetTranslationPart(gp_XYZ(0.0, 0.0, 0.0))
        scaled = BRepBuilderAPI_GTransform(shp, gtr, True).Shape()
        return cq.Workplane(obj=cq.Solid(scaled))
    except Exception:
        return solid


def _body_inertial(r: ResolvedContainerBottleConfig) -> Inertial:
    return Inertial.from_geometry(
        Cylinder(r.body_r, r.neck_top_z),
        mass=0.045,
        origin=Origin(xyz=(0.0, 0.0, r.neck_top_z / 2.0)),
    )


# ---------------------------------------------------------------------------
# Seal (Slot C): gasket washer ring (FIXED). mouth_lip is baked into the body.
# Adapted from S1 _gasket_ring (L111-L121).
# ---------------------------------------------------------------------------
def _gasket_mesh(r: ResolvedContainerBottleConfig, *, assets: AssetContext | None):
    g_or = r.neck_r + 0.003
    g_ir = r.mouth_r
    g_h = 0.003
    ring = cq.Workplane("XY").circle(g_or).circle(g_ir).extrude(g_h)
    return mesh_from_cadquery(ring, "container_bottle_gasket", assets=assets), g_h


# ---------------------------------------------------------------------------
# Closure (Slot B) meshes.
# ---------------------------------------------------------------------------
def _screw_cap_mesh(r: ResolvedContainerBottleConfig, *, assets: AssetContext | None):
    """Ribbed screw cap. Local origin at the cap joint; disc up, skirt down.
    Adapted from S1 _cap_solid (L124-L156)."""
    cap_r = r.neck_r + 0.005
    cap_h = 0.022
    skirt_drop = 0.012
    outer = cq.Workplane("XY").transformed(offset=(0, 0, -skirt_drop)).circle(cap_r).extrude(cap_h)
    outer = outer.edges(">Z").fillet(0.0025)
    # Cavity inner wall sits just inside the neck outer radius so the seated
    # skirt grips (slight interference fit, declared via allow_overlap in tests).
    # This keeps the cap in contact with the grounded neck shell.
    cavity = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, -skirt_drop - 0.001))
        .circle(r.neck_r - 0.0004)
        .extrude(cap_h - 0.004)
    )
    cap = outer.cut(cavity)
    n = 24
    rib_h = cap_h - 0.004
    zc = -skirt_drop + rib_h / 2.0
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        x = (cap_r - 0.0006) * math.cos(ang)
        y = (cap_r - 0.0006) * math.sin(ang)
        rib = (
            cq.Workplane("XY")
            .transformed(offset=(x, y, zc), rotate=(0, 0, math.degrees(ang)))
            .box(0.0018, 0.0014, rib_h)
        )
        cap = cap.union(rib)
    return (
        mesh_from_cadquery(cap, "container_bottle_screw_cap", assets=assets),
        cap_r,
        cap_h,
        skirt_drop,
    )


# Flip-cap hinge standoff: the rear rim of the lid disc sits this far FORWARD of
# the hinge pivot axis. Keeping the whole disc forward of the pivot (and the
# pivot itself just behind the neck rim) means opening the lid only ever LIFTS
# it — the disc can no longer swing its rim back down onto the neck shoulder,
# which was the seed-3 `bottle_body` vs `flip_lid` 穿模.
_FLIP_HINGE_STANDOFF = 0.0015

# The lid disc is nearly as wide as the neck rim, so past ~vertical its rear/edge
# thickness swings back down toward the mouth-lip rim. The standoff above stops
# the disc dipping for the low-angle swing; for the full range the realized open
# limit is solved with the SDK clearance solver so the swept lid keeps at least
# this margin from the (grounded) bottle_body — the seated lid<->cap_base and
# lid<->straw contacts are element-scoped allowances, not 穿模.
_FLIP_CLEARANCE_MARGIN = 0.0009


def _flip_hinge_geom(
    r: ResolvedContainerBottleConfig,
) -> tuple[float, float, float, float]:
    """Single-source flip-cap ring/lid/pivot geometry (Contract 3c).

    Returns ``(base_r, lid_r, lid_offset_y, pivot_y)``. ``pivot_y`` is placed at
    ``-(lid_r + standoff)`` — just behind the neck rim — and ``lid_offset_y`` at
    ``+(lid_r + standoff)`` so the lid disc is centred over the mouth when closed
    yet lies entirely forward of the pivot axis.
    """
    base_r = r.neck_r + 0.004
    lid_r = base_r - 0.001
    lid_offset_y = lid_r + _FLIP_HINGE_STANDOFF
    pivot_y = -lid_offset_y
    return base_r, lid_r, lid_offset_y, pivot_y


def _cap_base_mesh(r: ResolvedContainerBottleConfig, *, assets: AssetContext | None):
    """Fixed cap base ring with rear hinge ears. Local origin at ring bottom.
    Adapted from S13 _cap_base_solid (L88-L124)."""
    base_r, _, _, pivot_y_geom = _flip_hinge_geom(r)
    base_h = 0.018
    floor_h = 0.0025  # solid deck (with pour hole) at the ring bottom
    # Pour hole capped at 12 mm radius so the deck always has solid geometry
    # within the 15 mm joint-origin tolerance, even for wide necks.
    pour_r = max(0.003, min(r.mouth_r, 0.012))
    outer = cq.Workplane("XY").circle(base_r).extrude(base_h)
    # Hollow only above the floor so a solid deck with a central pour hole exists
    # at z~0 (keeps the FIXED-joint origin near real geometry; the pour hole
    # still clears the mouth bore / straw).
    cavity = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, floor_h))
        .circle(r.neck_r + 0.001)
        .extrude(base_h + 0.002)
    )
    cap_base = outer.cut(cavity)
    pour_hole = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, -0.001))
        .circle(pour_r)
        .extrude(floor_h + 0.002)
    )
    cap_base = cap_base.cut(pour_hole)
    # Ears sit at the pivot (just behind the neck rim). They straddle slightly
    # inward (+Y) so the box still overlaps the ring wall and stays fused to it.
    ear_y = pivot_y_geom
    ear_z_start = base_h - 0.004
    ear_height = 0.010
    ear_z_center = ear_z_start + ear_height / 2.0
    for dx in (-0.006, 0.006):
        ear = (
            cq.Workplane("XY")
            .transformed(offset=(dx, ear_y + 0.003, ear_z_center))
            .box(0.004, 0.008, ear_height + 0.004)
        )
        cap_base = cap_base.union(ear)
    pivot_y = pivot_y_geom
    pivot_z = base_h + 0.004
    return (
        mesh_from_cadquery(cap_base, "container_bottle_cap_base", assets=assets),
        base_r,
        base_h,
        pivot_y,
        pivot_z,
    )


def _flip_lid_mesh(r: ResolvedContainerBottleConfig, base_r: float, *, assets: AssetContext | None):
    """Flip lid disc + hinge barrel. Local origin at hinge pivot.
    Adapted from S13 _flip_cap_lid (L145-L170)."""
    _, lid_r, lid_offset_y, _ = _flip_hinge_geom(r)
    lid_h = 0.012
    lid = cq.Workplane("XY").transformed(offset=(0, lid_offset_y, 0)).circle(lid_r).extrude(lid_h)
    barrel = cq.Workplane("XZ").circle(0.0025).extrude(0.010, both=True)
    lid = lid.union(barrel)
    return (
        mesh_from_cadquery(lid, "container_bottle_flip_lid", assets=assets),
        lid_r,
        lid_h,
        lid_offset_y,
    )


def _straw_radius(r: ResolvedContainerBottleConfig) -> float:
    """Straw outer radius, capped so it clears the flip-cap-base pour hole."""
    pour_r = max(0.003, min(r.mouth_r, 0.012))
    return min(max(0.0035, r.mouth_r * 0.5), pour_r - 0.0012)


def _straw_mesh(r: ResolvedContainerBottleConfig, *, assets: AssetContext | None):
    """Straw tube + base flange that seats in the bore. Local origin at base.
    Adapted from S13 _straw (L173-L200)."""
    straw_r = _straw_radius(r)
    straw_h = 0.035
    straw = cq.Workplane("XY").circle(straw_r).extrude(straw_h)
    hollow = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, 0.005))
        .circle(straw_r - 0.0015)
        .extrude(straw_h - 0.004)
    )
    straw = straw.cut(hollow)
    flange = cq.Workplane("XY").circle(r.mouth_r + 0.0002).extrude(0.005)
    straw = straw.union(flange)
    return mesh_from_cadquery(straw, "container_bottle_straw", assets=assets), straw_h


def _hinge_collar_mesh(r: ResolvedContainerBottleConfig, *, assets: AssetContext | None):
    """Fixed swing-top hinge collar with side pins. Local origin at collar center.
    Adapted from S17 _hinge_collar (L177-L211)."""
    collar_h = 0.006
    collar_r = r.neck_r + 0.004
    arm_offset = r.neck_r + 0.005
    collar = cq.Workplane("XY").circle(collar_r).extrude(collar_h)
    # Bore is slightly under the neck outer radius so the collar clamps onto the
    # neck shell (seated/interference fit -> stays fused, declared overlap).
    bore = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, -0.001))
        .circle(r.neck_r - 0.0006)
        .extrude(collar_h + 0.002)
    )
    collar = collar.cut(bore)
    pin_r = 0.002
    pin_h = 0.004
    for sign in (+1, -1):
        pin = (
            cq.Workplane("XY")
            .transformed(offset=(sign * arm_offset, 0, collar_h / 2.0 - pin_h / 2.0))
            .circle(pin_r)
            .extrude(pin_h)
        )
        collar = collar.union(pin)
    return (
        mesh_from_cadquery(collar, "container_bottle_hinge_collar", assets=assets),
        arm_offset,
        collar_h,
    )


def _stopper_mesh(
    r: ResolvedContainerBottleConfig,
    arm_offset: float,
    hinge_z: float,
    *,
    assets: AssetContext | None,
):
    """Swing-top stopper: plug + disc + bail arms. Local origin at hinge pivot.
    Adapted from S17 _stopper_solid (L111-L174)."""
    # Plug seats into the mouth bore with a light interference fit against the
    # neck inner wall (radius = neck_r - wall) so the closed stopper contacts the
    # grounded neck shell (declared overlap in tests).
    plug_r = max(0.004, r.neck_r - r.wall + 0.0004)
    plug_h = 0.012
    cap_r = r.neck_r + 0.003
    cap_h = 0.004
    plug_drop = hinge_z - r.neck_top_z
    plug = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, -plug_drop - plug_h))
        .circle(plug_r)
        .extrude(plug_h)
    )
    disc_z = -plug_drop + 0.002
    disc = cq.Workplane("XY").transformed(offset=(0, 0, disc_z)).circle(cap_r).extrude(cap_h)
    stem = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, -plug_drop))
        .circle(plug_r * 0.5)
        .extrude(0.002)
    )
    stopper = plug.union(stem).union(disc)
    arm_t = 0.0025
    arm_w = 0.003
    arm_top_z = 0.008
    arm_bottom_z = disc_z + cap_h
    arm_length = max(0.002, arm_top_z - arm_bottom_z)
    arm_cz = (arm_top_z + arm_bottom_z) / 2.0
    for sign in (+1, -1):
        arm = (
            cq.Workplane("XY")
            .transformed(offset=(sign * arm_offset, 0, arm_cz))
            .box(arm_w, arm_t, arm_length)
        )
        stopper = stopper.union(arm)
    crossbar = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, arm_top_z - arm_w))
        .box(arm_offset * 2.0, arm_t, arm_w * 2)
    )
    stopper = stopper.union(crossbar)
    return mesh_from_cadquery(stopper, "container_bottle_stopper", assets=assets), plug_h, cap_r


def _pump_head_mesh(r: ResolvedContainerBottleConfig, *, assets: AssetContext | None):
    """Conical nozzle/pump head: skirt + conical nozzle + grip ridges.
    Local origin at cap joint (neck top). Adapted from S25 _nozzle_cap_solid
    (L113-L180)."""
    base_r = r.neck_r + 0.003
    tip_r = 0.004
    nozzle_h = 0.030
    skirt_h = 0.010
    skirt_r = r.neck_r + 0.0014
    skirt_outer = (
        cq.Workplane("XY").transformed(offset=(0, 0, -skirt_h)).circle(base_r).extrude(skirt_h)
    )
    skirt_inner = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, -skirt_h - 0.001))
        .circle(skirt_r)
        .extrude(skirt_h - 0.002)
    )
    skirt = skirt_outer.cut(skirt_inner)
    nozzle_profile = (
        cq.Workplane("XZ")
        .moveTo(base_r, 0.0)
        .lineTo(base_r, 0.003)
        .lineTo(tip_r + 0.002, nozzle_h - 0.004)
        .lineTo(tip_r, nozzle_h - 0.002)
        .lineTo(tip_r, nozzle_h)
        .lineTo(0.0, nozzle_h)
        .close()
    )
    nozzle = nozzle_profile.revolve(360.0, (0, 0, 0), (0, 1, 0))
    channel = (
        cq.Workplane("XZ")
        .moveTo(base_r - r.wall * 2, 0.0)
        .lineTo(base_r - r.wall * 2, 0.004)
        .lineTo(tip_r + 0.001, nozzle_h - 0.006)
        .lineTo(tip_r - 0.001, nozzle_h - 0.003)
        .lineTo(0.002, nozzle_h - 0.003)
        .lineTo(0.002, 0.0)
        .close()
        .revolve(360.0, (0, 0, 0), (0, 1, 0))
    )
    cap = skirt.union(nozzle.cut(channel))
    n = 16
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        x = (base_r - 0.0005) * math.cos(ang)
        y = (base_r - 0.0005) * math.sin(ang)
        ridge = (
            cq.Workplane("XY")
            .transformed(offset=(x, y, -skirt_h / 2.0), rotate=(0, 0, math.degrees(ang)))
            .box(0.0015, 0.0012, skirt_h * 0.8)
        )
        cap = cap.union(ridge)
    return (
        mesh_from_cadquery(cap, "container_bottle_pump_head", assets=assets),
        base_r,
        nozzle_h,
        skirt_h,
    )


# ---------------------------------------------------------------------------
# Closure emitters: each attaches a closure subtree to the body root and emits
# at least one non-fixed joint.
# ---------------------------------------------------------------------------
def _emit_screw_cap(model, r, body, mats, *, assets):
    mesh, cap_r, cap_h, skirt_drop = _screw_cap_mesh(r, assets=assets)
    carrier = model.part("cap_carrier")
    carrier.inertial = Inertial.from_geometry(Box((0.008, 0.008, 0.008)), mass=1e-4)
    cap = model.part("closure_cap")
    cap.visual(mesh, material=mats["cap"], name="cap_shell", material_class_id="plastic.opaque_glossy_molded")
    cap.visual(
        Box((0.004, 0.006, 0.012)),
        origin=Origin(xyz=(cap_r + 0.0015, 0.0, -skirt_drop + 0.006)),
        material=mats["cap"],
        name="cap_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(cap_r, cap_h), mass=0.006, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )
    joint_z = r.neck_top_z + 0.001
    model.articulation(
        "cap_lift",
        ArticulationType.PRISMATIC,
        parent=body,
        child=carrier,
        origin=Origin(xyz=(0.0, 0.0, joint_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=cap_h, effort=1.0, velocity=1.0),
        meta={"source_id": "S1", "semantic": "cap lifts off neck along +Z before unscrewing"},
    )
    model.articulation(
        "cap_spin",
        ArticulationType.CONTINUOUS,
        parent=carrier,
        child=cap,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=6.0),
        meta={"source_id": "S1", "semantic": "screw cap spins coaxially on neck"},
    )


def _emit_flip_cap(model, r, body, mats, *, assets, with_straw: bool):
    base_mesh, base_r, base_h, pivot_y, pivot_z = _cap_base_mesh(r, assets=assets)
    cap_base = model.part("cap_base")
    cap_base.visual(base_mesh, material=mats["cap"], name="cap_base_ring", material_class_id="plastic.opaque_glossy_molded")
    cap_base.inertial = Inertial.from_geometry(
        Cylinder(base_r, base_h), mass=0.005, origin=Origin(xyz=(0.0, 0.0, base_h / 2.0))
    )
    base_z = r.neck_top_z - 0.012
    model.articulation(
        "body_to_cap_base",
        ArticulationType.FIXED,
        parent=body,
        child=cap_base,
        origin=Origin(xyz=(0.0, 0.0, base_z)),
        meta={"source_id": "S13"},
    )
    lid_mesh, lid_r, lid_h, lid_offset_y = _flip_lid_mesh(r, base_r, assets=assets)
    flip = model.part("flip_lid")
    flip.visual(lid_mesh, material=mats["cap"], name="flip_lid_disc", material_class_id="plastic.opaque_glossy_molded")
    flip.inertial = Inertial.from_geometry(
        Cylinder(lid_r, lid_h),
        mass=0.006,
        origin=Origin(xyz=(0.0, lid_offset_y, lid_h / 2.0)),
    )
    upper = _clamp(2.2 * r.joint_limit_scale, 1.4, 2.4)
    model.articulation(
        "cap_flip",
        ArticulationType.REVOLUTE,
        parent=cap_base,
        child=flip,
        origin=Origin(xyz=(0.0, pivot_y, pivot_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=upper),
        meta={"source_id": "S13", "semantic": "flip lid opens on rear hinge"},
    )
    if with_straw:
        straw_mesh, straw_h = _straw_mesh(r, assets=assets)
        straw = model.part("straw")
        straw.visual(straw_mesh, material=mats["accent"], name="straw_tube", material_class_id="plastic.opaque_glossy_molded")
        straw.inertial = Inertial.from_geometry(
            Cylinder(_straw_radius(r), straw_h),
            mass=0.002,
            origin=Origin(xyz=(0.0, 0.0, straw_h / 2.0)),
        )
        model.articulation(
            "body_to_straw",
            ArticulationType.FIXED,
            parent=body,
            child=straw,
            origin=Origin(xyz=(0.0, 0.0, r.neck_top_z - 0.012)),
            meta={"source_id": "S13"},
        )

    # Solve the realized flip-open limit so the swept lid never 穿模 the body.
    # Moving set = flip_lid subtree; keepout = the grounded bottle_body; the
    # seated lid<->cap_base and lid<->straw contacts are allowed (they are the
    # captured hinge / pass-through, declared in run_container_bottle_tests too).
    allowed = [("flip_lid", "cap_base")]
    if with_straw:
        allowed.append(("flip_lid", "straw"))
    solved_upper = max_joint_value(
        model,
        joint="cap_flip",
        limit=upper,
        start=0.0,
        margin=_FLIP_CLEARANCE_MARGIN,
        allowed_pairs=allowed,
    )
    flip_joint = next(a for a in model.articulations if a.name == "cap_flip")
    flip_joint.motion_limits = MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=solved_upper)


def _emit_swingtop(model, r, body, mats, *, assets):
    collar_mesh, arm_offset, collar_h = _hinge_collar_mesh(r, assets=assets)
    hinge_z = r.neck_top_z + 0.004
    # Collar is a fixed body visual that wraps the neck just below the rim so it
    # stays fused to the neck shell (S17 mounts it on the body). Its bore hugs
    # the neck; centring it at neck_top_z - collar_h spans the upper neck.
    collar_z = r.neck_top_z - collar_h
    body.visual(
        collar_mesh,
        origin=Origin(xyz=(0.0, 0.0, collar_z)),
        material=mats["accent"],
        name="hinge_collar", material_class_id="plastic.opaque_glossy_molded",
    )
    stopper_mesh, plug_h, cap_r = _stopper_mesh(r, arm_offset, hinge_z, assets=assets)
    carrier = model.part("stopper_carrier")
    carrier.inertial = Inertial.from_geometry(Box((0.008, 0.008, 0.008)), mass=1e-4)
    stopper = model.part("stopper")
    stopper.visual(stopper_mesh, material=mats["cap"], name="stopper_body", material_class_id="plastic.opaque_glossy_molded")
    stopper.inertial = Inertial.from_geometry(
        Cylinder(cap_r, plug_h + 0.01),
        mass=0.010,
        origin=Origin(xyz=(0.0, 0.0, -(hinge_z - r.neck_top_z) / 2.0)),
    )
    travel = _clamp(0.020 * r.joint_limit_scale, 0.014, 0.026)
    model.articulation(
        "stopper_lift",
        ArticulationType.PRISMATIC,
        parent=body,
        child=carrier,
        origin=Origin(xyz=(0.0, 0.0, hinge_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=1.0, lower=0.0, upper=travel),
        meta={"source_id": "S17", "semantic": "stopper lifts vertically out of the mouth"},
    )
    model.articulation(
        "stopper_spin",
        ArticulationType.CONTINUOUS,
        parent=carrier,
        child=stopper,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=6.0),
        meta={"source_id": "S17", "semantic": "stopper rotates about the vertical neck axis"},
    )


def _emit_pump_press(model, r, body, mats, *, assets):
    mesh, base_r, nozzle_h, skirt_h = _pump_head_mesh(r, assets=assets)
    carrier = model.part("cap_carrier")
    carrier.inertial = Inertial.from_geometry(Box((0.006, 0.006, 0.006)), mass=1e-4)
    nozzle = model.part("pump_head")
    nozzle.visual(mesh, material=mats["cap"], name="nozzle_shell", material_class_id="plastic.opaque_glossy_molded")
    nozzle.visual(
        Box((0.004, 0.005, 0.008)),
        origin=Origin(xyz=(base_r + 0.001, 0.0, -skirt_h / 2.0)),
        material=mats["cap"],
        name="rotation_tab", material_class_id="plastic.opaque_glossy_molded",
    )
    nozzle.inertial = Inertial.from_geometry(
        Cylinder(base_r, nozzle_h + skirt_h),
        mass=0.008,
        origin=Origin(xyz=(0.0, 0.0, (nozzle_h - skirt_h) / 2.0)),
    )
    travel = 0.008
    rot_lim = 0.4
    model.articulation(
        "cap_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=carrier,
        origin=Origin(xyz=(0.0, 0.0, r.neck_top_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(lower=0.0, upper=travel, effort=2.0, velocity=0.5),
        meta={"source_id": "S25", "semantic": "pump head presses down"},
    )
    model.articulation(
        "cap_rotate",
        ArticulationType.REVOLUTE,
        parent=carrier,
        child=nozzle,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=-rot_lim, upper=rot_lim, effort=1.0, velocity=2.0),
        meta={"source_id": "S25", "semantic": "pump head twists slightly"},
    )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_container_bottle(
    config: ContainerBottleConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"bottle_{key}_{r.material_style}", rgba=rgba)
        for key, rgba in PALETTES[r.material_style].items()
    }

    body = model.part("bottle_body")
    body.visual(_body_mesh(r, assets=assets), material=mats["body"], name="body_shell", material_class_id="plastic.clear_rigid")
    body.inertial = _body_inertial(r)

    # Slot C: seal (gasket_ring is a FIXED part; mouth_lip is baked into body).
    if r.seal == "gasket_ring":
        gasket_mesh, g_h = _gasket_mesh(r, assets=assets)
        gasket = model.part("gasket")
        gasket.visual(gasket_mesh, material=mats["seal"], name="gasket_ring", material_class_id="rubber.smooth_plain")
        gasket.inertial = Inertial.from_geometry(
            Cylinder(r.neck_r + 0.003, g_h),
            mass=0.002,
            origin=Origin(xyz=(0.0, 0.0, g_h / 2.0)),
        )
        model.articulation(
            "gasket_fixed",
            ArticulationType.FIXED,
            parent=body,
            child=gasket,
            origin=Origin(xyz=(0.0, 0.0, r.neck_top_z)),
            meta={"source_id": "S1"},
        )

    # Slot B: closure (exactly one).
    if r.closure == "screw_cap":
        _emit_screw_cap(model, r, body, mats, assets=assets)
    elif r.closure == "flip_cap":
        _emit_flip_cap(model, r, body, mats, assets=assets, with_straw=False)
    elif r.closure == "straw_spout":
        _emit_flip_cap(model, r, body, mats, assets=assets, with_straw=True)
    elif r.closure == "swingtop_stopper":
        _emit_swingtop(model, r, body, mats, assets=assets)
    elif r.closure == "pump_press":
        _emit_pump_press(model, r, body, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_bottle(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_container_bottle(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
_NON_FIXED = {
    ArticulationType.REVOLUTE,
    ArticulationType.PRISMATIC,
    ArticulationType.CONTINUOUS,
}


def run_container_bottle_tests(
    object_model: ArticulatedObject,
    config: ContainerBottleConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()

    body = object_model.get_part("bottle_body")
    ctx.check("body_exists", body is not None, "bottle_body part required")

    # --- identity: neck narrower than barrel ---
    ctx.check(
        "neck_narrower_than_body",
        r.neck_r < r.body_r * 0.7,
        details=f"neck_r={r.neck_r:.4f}, body_r={r.body_r:.4f}",
    )

    # --- body is tinted-transparent ---
    body_shell = body.get_visual("body_shell")
    ctx.check(
        "body_translucent",
        body_shell.material.rgba is not None and body_shell.material.rgba[3] < 1.0,
        details=f"body rgba={body_shell.material.rgba}",
    )

    # --- seal placement ---
    if r.seal == "gasket_ring":
        gasket = object_model.get_part("gasket")
        ctx.check("gasket_exists", gasket is not None)
        gj = object_model.get_articulation("gasket_fixed")
        ctx.check("gasket_fixed_type", gj.articulation_type == ArticulationType.FIXED)
        ctx.allow_overlap(
            gasket,
            body,
            elem_a="gasket_ring",
            elem_b="body_shell",
            reason="gasket ring is seated on the neck rim as a seal.",
        )

    # --- closure: at least one non-fixed joint, correct types/axes ---
    arts = list(object_model.articulations)
    non_fixed = [a for a in arts if a.articulation_type in _NON_FIXED]
    ctx.check(
        "has_non_fixed_joint",
        len(non_fixed) >= 1,
        details=f"non-fixed joints: {[a.name for a in non_fixed]}",
    )

    if r.closure == "screw_cap":
        spin = object_model.get_articulation("cap_spin")
        lift = object_model.get_articulation("cap_lift")
        ctx.check("cap_spin_continuous", spin.articulation_type == ArticulationType.CONTINUOUS)
        ctx.check("cap_lift_prismatic", lift.articulation_type == ArticulationType.PRISMATIC)
        ctx.check("cap_spin_axis_z", tuple(spin.axis) == (0.0, 0.0, 1.0), details=str(spin.axis))
        cap = object_model.get_part("closure_cap")
        # cap skirt seats over neck (intentional overlap)
        ctx.allow_overlap(
            cap,
            body,
            elem_a="cap_shell",
            elem_b="body_shell",
            reason="screw cap skirt is seated over the threaded neck.",
        )
        # lifting raises the cap
        rest_z = ctx.part_world_position(cap)[2]
        with ctx.pose({lift: lift.motion_limits.upper}):
            lifted_z = ctx.part_world_position(cap)[2]
        ctx.check(
            "cap_lift_raises",
            lifted_z > rest_z + lift.motion_limits.upper * 0.7,
            details=f"rest={rest_z:.4f}, lifted={lifted_z:.4f}",
        )

    elif r.closure in ("flip_cap", "straw_spout"):
        flip = object_model.get_articulation("cap_flip")
        ctx.check("cap_flip_revolute", flip.articulation_type == ArticulationType.REVOLUTE)
        ctx.check("cap_flip_axis_x", tuple(flip.axis) == (1.0, 0.0, 0.0), details=str(flip.axis))
        cap_base = object_model.get_part("cap_base")
        flip_lid = object_model.get_part("flip_lid")
        ctx.allow_overlap(
            cap_base,
            body,
            elem_a="cap_base_ring",
            elem_b="body_shell",
            reason="cap base ring is seated over the bottle neck.",
        )
        ctx.allow_overlap(
            flip_lid,
            cap_base,
            elem_a="flip_lid_disc",
            elem_b="cap_base_ring",
            reason="flip lid hinge barrel connects to the cap base ears.",
        )
        # opening swings the lid upward (pose at the solver-clamped open limit)
        open_angle = flip.motion_limits.upper
        with ctx.pose({flip: 0.0}):
            closed = ctx.part_world_aabb(flip_lid)
        with ctx.pose({flip: open_angle}):
            opened = ctx.part_world_aabb(flip_lid)
        ctx.check(
            "flip_lid_opens_up",
            opened[1][2] > closed[1][2] + 0.004,
            details=f"closed_zmax={closed[1][2]:.4f}, open_zmax={opened[1][2]:.4f}",
        )
        # the solved open limit is a real, useful opening (not clamped to ~0)
        ctx.check(
            "flip_lid_open_limit_usable",
            open_angle >= 0.35,
            details=f"open_angle={open_angle:.4f}",
        )
        if r.closure == "straw_spout":
            straw = object_model.get_part("straw")
            ctx.check("straw_exists", straw is not None)
            ctx.allow_overlap(
                straw,
                body,
                elem_a="straw_tube",
                elem_b="body_shell",
                reason="straw base flange is press-fit inside the bottle neck.",
            )
            ctx.allow_overlap(
                straw,
                cap_base,
                elem_a="straw_tube",
                elem_b="cap_base_ring",
                reason="straw passes through the cap base opening.",
            )
            ctx.allow_overlap(
                straw,
                flip_lid,
                elem_a="straw_tube",
                elem_b="flip_lid_disc",
                reason="straw passes through the flip lid when closed.",
            )

        # With every seated closure overlap declared above, assert the swept lid
        # at its solved open limit introduces no new 穿模 (notably lid vs body).
        with ctx.pose({flip: flip.motion_limits.upper}):
            ctx.fail_if_parts_overlap_in_current_pose(name="flip_lid_clears_body_when_open")

    elif r.closure == "swingtop_stopper":
        lift = object_model.get_articulation("stopper_lift")
        spin = object_model.get_articulation("stopper_spin")
        ctx.check("stopper_lift_prismatic", lift.articulation_type == ArticulationType.PRISMATIC)
        ctx.check("stopper_spin_continuous", spin.articulation_type == ArticulationType.CONTINUOUS)
        ctx.check(
            "stopper_lift_axis_z", tuple(lift.axis) == (0.0, 0.0, 1.0), details=str(lift.axis)
        )
        ctx.check(
            "stopper_spin_axis_z", tuple(spin.axis) == (0.0, 0.0, 1.0), details=str(spin.axis)
        )
        stopper = object_model.get_part("stopper")
        ctx.allow_overlap(
            stopper,
            body,
            elem_a="stopper_body",
            elem_b="body_shell",
            reason="stopper plug is seated in the mouth bore when closed.",
        )
        ctx.allow_overlap(
            stopper,
            body,
            elem_a="stopper_body",
            elem_b="hinge_collar",
            reason="bail arms are retained inside the neck collar while the stopper lifts and spins.",
        )
        closed_pos = ctx.part_world_position(stopper)
        with ctx.pose({lift: lift.motion_limits.upper}):
            lifted_pos = ctx.part_world_position(stopper)
        ctx.check(
            "stopper_lifts_straight_up",
            lifted_pos[2] > closed_pos[2] + lift.motion_limits.upper * 0.7
            and abs(lifted_pos[0] - closed_pos[0]) < 1e-6
            and abs(lifted_pos[1] - closed_pos[1]) < 1e-6,
            details=f"closed={closed_pos}, lifted={lifted_pos}",
        )

    elif r.closure == "pump_press":
        slide = object_model.get_articulation("cap_slide")
        rotate = object_model.get_articulation("cap_rotate")
        ctx.check("pump_slide_prismatic", slide.articulation_type == ArticulationType.PRISMATIC)
        ctx.check("pump_rotate_revolute", rotate.articulation_type == ArticulationType.REVOLUTE)
        head = object_model.get_part("pump_head")
        ctx.allow_overlap(
            head,
            body,
            elem_a="nozzle_shell",
            elem_b="body_shell",
            reason="pump head skirt is seated over the neck.",
        )
        rest_z = ctx.part_world_position(head)[2]
        with ctx.pose({slide: slide.motion_limits.upper}):
            pressed_z = ctx.part_world_position(head)[2]
        ctx.check(
            "pump_presses_down",
            pressed_z < rest_z - slide.motion_limits.upper * 0.7,
            details=f"rest={rest_z:.4f}, pressed={pressed_z:.4f}",
        )

    return ctx.report()
