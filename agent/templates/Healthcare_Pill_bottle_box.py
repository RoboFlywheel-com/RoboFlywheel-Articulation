# SPDX-License-Identifier: Apache-2.0

"""Procedural modular template for `Healthcare_Pill_bottle_box` (stem: pill_box).

Two mutually-exclusive ③ Primary-Form families:

- **bottle** — hollow revolved/box CadQuery pill-bottle shell (round or square
  section) + one closure (PRISMATIC lift cap, or REVOLUTE flip-top). Amber
  softgel fill + wraparound label are host-conformal *visuals* of the body
  (they do not move → not parts, §A Rule 1).
- **organizer** — shallow tray (rectangular or round) + one lid mechanism:
  N REVOLUTE flip lids (multiplicity), one PRISMATIC sliding cover, or one
  REVOLUTE-z rotating dial. Uniform grid → all N lids share ONE mesh.

`config_from_seed` first picks the family, then samples only that family's
slots (cross-family cells are gated). Every non-FIXED joint declares a
`MatingContract` to real faces. Derived from 7 five-star sources (see spec
`articraft_template_authoring/specs_modular_v1/Healthcare_Pill_bottle_box.md`).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal, Optional

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MatingContract,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    scale_geometry_to_size,
)

__modular__ = True

FormFamily = Literal["bottle", "organizer"]
BodyForm = Literal["round_cylinder", "square_prism"]
Closure = Literal["screw_lift_cap", "fliptop_hinged"]
LidMechanism = Literal["individual_flip_lids", "single_sliding_cover", "rotating_dial_lid"]

FAMILIES: tuple[FormFamily, ...] = ("bottle", "organizer")
BODY_FORMS: tuple[BodyForm, ...] = ("round_cylinder", "square_prism")
CLOSURES: tuple[Closure, ...] = ("screw_lift_cap", "fliptop_hinged")
MECHANISMS: tuple[LidMechanism, ...] = (
    "individual_flip_lids",
    "single_sliding_cover",
    "rotating_dial_lid",
)

# ── palettes (⑥): every .visual(material=) is driven by palette_style ──────
BOTTLE_PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "amber_bottle": {
        "body": (0.78, 0.45, 0.14, 0.45),
        "cap": (0.05, 0.05, 0.06, 1.0),
        "label": (1.0, 1.0, 0.96, 1.0),
        "accent": (0.17, 0.78, 0.75, 1.0),
        "fill": (1.0, 0.70, 0.08, 0.58),
        "mark": (0.04, 0.08, 0.22, 1.0),
    },
    "clear_bottle": {
        "body": (0.80, 0.86, 0.84, 0.28),
        "cap": (0.90, 0.90, 0.92, 1.0),
        "label": (1.0, 1.0, 0.96, 1.0),
        "accent": (0.10, 0.55, 0.72, 1.0),
        "fill": (0.95, 0.82, 0.45, 0.55),
        "mark": (0.06, 0.10, 0.28, 1.0),
    },
    "white_bottle": {
        "body": (0.96, 0.96, 0.93, 1.0),
        "cap": (0.05, 0.05, 0.06, 1.0),
        "label": (1.0, 1.0, 0.96, 1.0),
        "accent": (0.85, 0.20, 0.15, 1.0),
        "fill": (1.0, 0.70, 0.08, 0.58),
        "mark": (0.06, 0.10, 0.28, 1.0),
    },
}
ORGANIZER_PALETTES: dict[str, dict[str, object]] = {
    "pastel_organizer": {
        "frame": (0.94, 0.88, 0.68, 1.0),
        "well": (0.58, 0.74, 0.88, 1.0),
        "cover": (0.82, 0.87, 0.91, 0.42),
        "mark": (1.0, 1.0, 0.96, 1.0),
        "post": (0.94, 0.88, 0.68, 1.0),
        "lids": [
            (1.00, 0.47, 0.42, 0.58),
            (0.42, 0.63, 0.86, 0.55),
            (0.88, 0.66, 0.48, 0.55),
            (0.78, 0.72, 0.90, 0.55),
            (0.55, 0.80, 0.62, 0.55),
            (0.42, 0.72, 0.86, 0.55),
            (0.97, 0.90, 0.52, 0.55),
        ],
    },
    "cream_organizer": {
        "frame": (0.90, 0.85, 0.72, 1.0),
        "well": (0.72, 0.78, 0.82, 0.60),
        "cover": (0.86, 0.84, 0.78, 0.42),
        "mark": (1.0, 1.0, 0.96, 1.0),
        "post": (0.90, 0.85, 0.72, 1.0),
        "lids": [
            (0.97, 0.90, 0.52, 0.55),
            (0.88, 0.66, 0.48, 0.55),
            (0.95, 0.80, 0.55, 0.55),
            (0.82, 0.70, 0.50, 0.55),
        ],
    },
    "mint_organizer": {
        "frame": (0.88, 0.93, 0.86, 1.0),
        "well": (0.72, 0.88, 0.72, 1.0),
        "cover": (0.80, 0.90, 0.85, 0.40),
        "mark": (1.0, 1.0, 0.96, 1.0),
        "post": (0.88, 0.93, 0.86, 1.0),
        "lids": [
            (0.55, 0.80, 0.62, 0.55),
            (0.42, 0.72, 0.86, 0.55),
            (0.60, 0.85, 0.70, 0.55),
            (0.45, 0.78, 0.80, 0.55),
        ],
    },
}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


@dataclass(frozen=True)
class PillBoxConfig:
    form_family: Optional[FormFamily] = None
    palette_style: Optional[str] = None
    # bottle slots
    bottle_body_form: Optional[BodyForm] = None
    bottle_closure: Optional[Closure] = None
    body_radius: float = 0.030
    body_height_scale: float = 1.0
    # organizer slots
    lid_mechanism: Optional[LidMechanism] = None
    compartment_count: Optional[int] = None
    base_w: float = 0.130
    tray_radius: float = 0.065
    name: str = "pill_box"


@dataclass(frozen=True)
class ResolvedPillBoxConfig:
    form_family: FormFamily
    palette_style: str
    # bottle
    body_form: BodyForm
    closure: Closure
    body_r: float
    body_h: float          # mouth top z (BODY_TOP_Z)
    neck_outer: float
    cap_r: float
    cap_h: float
    cap_lift: float
    collar_top: float
    hinge_x: float
    flip_upper: float
    # organizer
    lid_mechanism: LidMechanism
    base_form: str          # rect_tray | round_tray
    n: int
    cols: int
    rows: int
    base_w: float
    base_d: float
    tray_radius: float
    lid_open_angle: float
    slide_travel: float
    name: str


def _weighted_rect_n(rng: random.Random) -> int:
    pool = [4, 5, 6, 7, 7, 7, 8, 10, 12, 14, 14, 16, 21, 28]
    return rng.choice(pool)


def config_from_seed(seed: int) -> PillBoxConfig:
    rng = random.Random(seed)
    family: FormFamily = rng.choice(FAMILIES)
    if family == "bottle":
        return PillBoxConfig(
            form_family="bottle",
            palette_style=rng.choice(tuple(BOTTLE_PALETTES.keys())),
            bottle_body_form=rng.choice(BODY_FORMS),
            bottle_closure=rng.choice(CLOSURES),
            body_radius=round(rng.uniform(0.026, 0.036), 4),
            body_height_scale=round(rng.uniform(0.80, 1.25), 4),
            name=f"seeded_pill_box_{seed}",
        )
    mechanism: LidMechanism = rng.choice(MECHANISMS)
    if mechanism == "rotating_dial_lid":
        n = rng.choice((4, 5, 6, 7, 7, 8))
    else:
        n = _weighted_rect_n(rng)
    return PillBoxConfig(
        form_family="organizer",
        palette_style=rng.choice(tuple(ORGANIZER_PALETTES.keys())),
        lid_mechanism=mechanism,
        compartment_count=n,
        base_w=round(rng.uniform(0.10, 0.17), 4),
        tray_radius=round(rng.uniform(0.050, 0.075), 4),
        name=f"seeded_pill_box_{seed}",
    )


def resolve_config(config: Optional[PillBoxConfig] = None) -> ResolvedPillBoxConfig:
    # Idempotent: pipelines may hand back an already-resolved config (raw-slot
    # overrides only apply to PillBoxConfig, so a ResolvedPillBoxConfig is
    # already final) — never re-read raw-only fields off it.
    if isinstance(config, ResolvedPillBoxConfig):
        return config
    cfg = config or PillBoxConfig()
    family: FormFamily = _pick(cfg.form_family, FAMILIES)

    # bottle geometry
    body_form: BodyForm = _pick(cfg.bottle_body_form, BODY_FORMS)
    closure: Closure = _pick(cfg.bottle_closure, CLOSURES)
    body_r = _clamp(cfg.body_radius, 0.026, 0.036)
    hs = _clamp(cfg.body_height_scale, 0.80, 1.25)
    body_h = 0.104 * hs
    neck_outer = 0.020 * (body_r / 0.030)
    cap_r = 0.85 * body_r
    cap_h = max(0.016, 0.020 * hs)
    cap_lift = _clamp(cap_h * 2.5, 0.030, 0.060)
    collar_top = body_h + 0.002
    hinge_x = cap_r
    flip_upper = 1.7

    # organizer geometry
    mechanism: LidMechanism = _pick(cfg.lid_mechanism, MECHANISMS)
    base_form = "round_tray" if mechanism == "rotating_dial_lid" else "rect_tray"
    n_raw = int(cfg.compartment_count) if cfg.compartment_count else 7
    if base_form == "round_tray":
        n = int(_clamp(n_raw, 4, 8))
    else:
        n = int(_clamp(n_raw, 4, 28))
    cols = min(7, n)
    rows = int(math.ceil(n / cols))
    base_w = _clamp(cfg.base_w, 0.10, 0.17)
    base_d = base_w * 0.77
    tray_radius = _clamp(cfg.tray_radius, 0.050, 0.075)
    lid_open_angle = 1.5
    slide_travel = _clamp(base_w * 0.55, 0.040, 0.100)

    if family == "bottle":
        palette = cfg.palette_style if cfg.palette_style in BOTTLE_PALETTES else "amber_bottle"
    else:
        palette = cfg.palette_style if cfg.palette_style in ORGANIZER_PALETTES else "pastel_organizer"

    return ResolvedPillBoxConfig(
        form_family=family,
        palette_style=palette,
        body_form=body_form,
        closure=closure,
        body_r=body_r,
        body_h=body_h,
        neck_outer=neck_outer,
        cap_r=cap_r,
        cap_h=cap_h,
        cap_lift=cap_lift,
        collar_top=collar_top,
        hinge_x=hinge_x,
        flip_upper=flip_upper,
        lid_mechanism=mechanism,
        base_form=base_form,
        n=n,
        cols=cols,
        rows=rows,
        base_w=base_w,
        base_d=base_d,
        tray_radius=tray_radius,
        lid_open_angle=lid_open_angle,
        slide_travel=slide_travel,
        name=cfg.name or "pill_box",
    )


def _n_band(n: int) -> str:
    if n <= 8:
        return "4-8"
    if n <= 16:
        return "9-16"
    return "17-28"


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedPillBoxConfig) else resolve_config(config)
    if r.form_family == "bottle":
        return (
            ("form_family", "bottle"),
            ("bottle_body_form", r.body_form),
            ("bottle_closure", r.closure),
        )
    return (
        ("form_family", "organizer"),
        ("organizer_base_form", r.base_form),
        ("lid_mechanism", r.lid_mechanism),
        ("compartment_count", _n_band(r.n)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ═══════════════════════════════════════════════════════════════════════════
# Family A — bottle
# ═══════════════════════════════════════════════════════════════════════════
# Revolved-profile CadQuery hollow shell (S_A1 L33-L63); scaled by (R, H).
_ROUND_PROFILE = [
    (0.000, 0.003), (0.030, 0.003), (0.030, 0.074), (0.029, 0.080),
    (0.026, 0.088), (0.020, 0.096), (0.020, 0.104), (0.016, 0.104),
    (0.016, 0.098), (0.020, 0.091), (0.023, 0.083), (0.026, 0.074),
    (0.026, 0.008), (0.000, 0.008),
]


def _round_shell_mesh(R: float, H: float):
    xs, zs = R / 0.030, H / 0.104
    pts = [(x * xs, z * zs) for (x, z) in _ROUND_PROFILE]
    wp = (
        cq.Workplane("XZ")
        .polyline(pts)
        .close()
        .revolve(360.0, axisStart=(0.0, 0.0, 0.0), axisEnd=(0.0, 1.0, 0.0))
    )
    return mesh_from_cadquery(wp, "body_shell", tolerance=0.0008)


def _square_shell_mesh(R: float, H: float):
    # Rounded-square box + round neck + shell(-wall) (S_A2 L68-L93), scaled.
    zs = H / 0.104
    hw = hd = R
    fillet = R * 0.34
    wall = 0.002
    body_total_h = 0.092 * zs
    neck_ro = 0.020 * (R / 0.030)
    nk_h = 0.012 * zs
    outer = (
        cq.Workplane("XY")
        .rect(2 * hw, 2 * hd)
        .extrude(body_total_h)
        .edges("|Z").fillet(fillet)
        .faces(">Z").workplane()
        .circle(neck_ro)
        .extrude(nk_h)
    )
    return mesh_from_cadquery(outer.faces(">Z").shell(-wall), "body_shell", tolerance=0.0008)


def _round_sleeve_mesh(inner_r, outer_r, z0, z1, name):
    pts = [(inner_r, z0), (outer_r, z0), (outer_r, z1), (inner_r, z1)]
    wp = (
        cq.Workplane("XZ")
        .polyline(pts)
        .close()
        .revolve(360.0, axisStart=(0.0, 0.0, 0.0), axisEnd=(0.0, 1.0, 0.0))
    )
    return mesh_from_cadquery(wp, name, tolerance=0.0008)


def _square_sleeve_mesh(hw, hd, fillet, z0, z1, name, thickness=0.0009):
    outer = cq.Workplane("XY").workplane(offset=z0).rect(2 * hw, 2 * hd).extrude(z1 - z0)
    if fillet > 0.0005:
        outer = outer.edges("|Z").fillet(fillet)
    ihw, ihd = hw - thickness, hd - thickness
    ifil = max(fillet - thickness, 0.0001)
    inner = (
        cq.Workplane("XY").workplane(offset=z0 - 0.0001).rect(2 * ihw, 2 * ihd).extrude(z1 - z0 + 0.0002)
    )
    if ifil > 0.0005:
        inner = inner.edges("|Z").fillet(ifil)
    return mesh_from_cadquery(outer.cut(inner), name, tolerance=0.0008)


def _emit_label(body, r: ResolvedPillBoxConfig, mats):
    """Host-conformal wraparound label + accent stripe (§A Rule 4)."""
    hs = r.body_h / 0.104
    z0, z1 = 0.030 * hs, 0.062 * hs      # label band
    a0, a1 = 0.023 * hs, 0.028 * hs      # accent stripe
    R = r.body_r
    if r.body_form == "round_cylinder":
        body.visual(
            _round_sleeve_mesh(R - 0.00015, R + 0.0010, z0, z1, "label_band"),
            material=mats["label"], name="label_band", material_class_id="paper.plain_sheet",
        )
        body.visual(
            _round_sleeve_mesh(R - 0.00015, R + 0.0013, a0, a1, "label_accent"),
            material=mats["accent"], name="label_accent", material_class_id="paper.plain_sheet",
        )
    else:
        # thickness > (hw - R) so each sleeve's inner face embeds into the shell
        # wall (dist 0) rather than floating a few 0.1mm proud → no island.
        fillet = R * 0.34 + 0.0001
        body.visual(
            _square_sleeve_mesh(R + 0.0009, R + 0.0009, fillet, z0, z1, "label_band", thickness=0.0012),
            material=mats["label"], name="label_band", material_class_id="paper.plain_sheet",
        )
        body.visual(
            _square_sleeve_mesh(R + 0.0013, R + 0.0013, fillet, a0, a1, "label_accent", thickness=0.0017),
            material=mats["accent"], name="label_accent", material_class_id="paper.plain_sheet",
        )


def _emit_fill(body, r: ResolvedPillBoxConfig, mats):
    """Amber softgel fill folded into the bottle body as connected visuals
    (does not move → not a part, §A Rule 1). Sized to kiss the inner wall so it
    is never a disconnected island within the part."""
    hs = r.body_h / 0.104
    fill_r = r.body_r - 0.001            # embeds into inner wall → contact
    z_lo, z_barrel = 0.010 * hs, 0.074 * hs
    body.visual(
        Cylinder(radius=fill_r, length=(z_barrel - z_lo)),
        origin=Origin(xyz=(0.0, 0.0, (z_lo + z_barrel) / 2.0)),
        material=mats["fill"], name="fill_core", material_class_id="organic.wax",
    )
    body.visual(
        Cylinder(radius=r.body_r * 0.80, length=0.014 * hs),
        origin=Origin(xyz=(0.0, 0.0, (0.074 + 0.007) * hs)),
        material=mats["fill"], name="fill_shoulder", material_class_id="organic.wax",
    )
    pellet = scale_geometry_to_size(Sphere(0.005), (0.014, 0.007, 0.006), filename="softgel_ovoid")
    for i in range(12):
        ang = i * (2.0 * math.pi / 6.0) + (i // 6) * 0.5
        rad = fill_r * (0.32 + 0.30 * (i % 3))
        z = (0.050 + 0.012 * (i // 6)) * hs
        body.visual(
            pellet,
            origin=Origin(xyz=(rad * math.cos(ang), rad * math.sin(ang), z),
                          rpy=(0.1 * (i % 3), 0.2 * (i % 2), ang)),
            material=mats["fill"], name=f"fill_pellet_{i}", material_class_id="organic.wax",
        )


def _emit_bottle_body(model, r: ResolvedPillBoxConfig, mats):
    body = model.part("bottle_body")
    if r.body_form == "round_cylinder":
        shell = _round_shell_mesh(r.body_r, r.body_h)
    else:
        shell = _square_shell_mesh(r.body_r, r.body_h)
    body.visual(shell, origin=Origin(), material=mats["body"], name="body_shell", material_class_id="plastic.clear_rigid")
    _emit_fill(body, r, mats)
    _emit_label(body, r, mats)
    return body


def _emit_screw_cap(model, r: ResolvedPillBoxConfig, body, mats):
    cap = model.part("closure_cap")
    cap.visual(
        Cylinder(radius=r.cap_r, length=r.cap_h),
        origin=Origin(xyz=(0.0, 0.0, r.cap_h / 2.0)), material=mats["cap"], name="cap_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    cap.visual(
        Cylinder(radius=r.cap_r * 0.92, length=0.0016),
        origin=Origin(xyz=(0.0, 0.0, r.cap_h + 0.0008)), material=mats["cap"], name="cap_top", material_class_id="plastic.opaque_glossy_molded",
    )
    ribs = 36
    for i in range(ribs):
        th = 2.0 * math.pi * i / ribs
        cap.visual(
            Box((0.0030, 0.0010, r.cap_h * 0.75)),
            origin=Origin(
                xyz=((r.cap_r + 0.0002) * math.cos(th), (r.cap_r + 0.0002) * math.sin(th), r.cap_h * 0.47),
                rpy=(0.0, 0.0, th),
            ),
            material=mats["cap"], name=f"cap_rib_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    model.articulation(
        "bottle_to_cap", ArticulationType.PRISMATIC, parent=body, child=cap,
        origin=Origin(xyz=(0.0, 0.0, r.body_h)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.25, lower=0.0, upper=r.cap_lift),
        mating=MatingContract(
            parent_face_geometry="body_shell", parent_face_side="positive_z",
            child_face_geometry="cap_shell", child_face_side="negative_z", contact_tol=0.0028,
        ),
        meta={"source_id": "S_A1", "semantic": "cap lifts off the mouth along +z"},
    )


def _emit_fliptop(model, r: ResolvedPillBoxConfig, body, mats):
    # neck_collar is a fixed decorative ring folded into the body (Rule 1);
    # the flip lid hinges on its top rim.
    body.visual(
        Cylinder(radius=r.cap_r, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, r.body_h - 0.003)), material=mats["cap"], name="neck_collar", material_class_id="plastic.opaque_glossy_molded",
    )
    lid = model.part("flip_lid")
    lt = 0.003
    lid.visual(
        Cylinder(radius=r.cap_r * 0.95, length=lt),
        origin=Origin(xyz=(-r.hinge_x, 0.0, lt / 2.0)), material=mats["cap"], name="lid_disk", material_class_id="plastic.opaque_glossy_molded",
    )
    lid.visual(
        Box((0.008, 0.012, 0.003)),
        origin=Origin(xyz=(-2.0 * r.hinge_x, 0.0, lt + 0.0005)), material=mats["cap"], name="lid_tab", material_class_id="plastic.opaque_glossy_molded",
    )
    lid.visual(
        Box((0.006, 0.008, lt)),
        origin=Origin(xyz=(-0.002, 0.0, lt)), material=mats["cap"], name="hinge_ear", material_class_id="plastic.opaque_glossy_molded",
    )
    lid.visual(
        Cylinder(radius=0.002, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["cap"], name="hinge_barrel", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "body_to_flip_lid", ArticulationType.REVOLUTE, parent=body, child=lid,
        origin=Origin(xyz=(r.hinge_x, 0.0, r.collar_top)), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=3.0, lower=0.0, upper=r.flip_upper),
        mating=MatingContract(
            parent_face_geometry="neck_collar", parent_face_side="positive_z",
            child_face_geometry="lid_disk", child_face_side="negative_z", contact_tol=0.0028,
        ),
        meta={"source_id": "S_A3", "semantic": "flip lid opens on rear hinge"},
    )


# ═══════════════════════════════════════════════════════════════════════════
# Family B — organizer  (shared rounded-box lids, S_B1/S_B2/S_B3/S_B4)
# ═══════════════════════════════════════════════════════════════════════════
BASE_BOTTOM_H = 0.004
WALL_H = 0.010
WALL_TOP_Z = BASE_BOTTOM_H + WALL_H     # 0.014
RIM_T = 0.005
WALL_T = 0.0022
FLOOR_H = 0.0008
LID_T = 0.003
RAIL_H = 0.002
COVER_T = 0.003
COVER_BOTTOM_Z = WALL_TOP_Z + RAIL_H    # 0.016


def rounded_box_mesh(width, depth, height, radius, name):
    solid = cq.Workplane("XY").box(width, depth, height)
    if radius > 0:
        solid = solid.edges("|Z").fillet(min(radius, width * 0.45, depth * 0.45, height * 0.45))
    return mesh_from_cadquery(solid, name, tolerance=0.00035, angular_tolerance=0.12)


def add_box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)):
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="plastic.opaque_glossy_molded")


def _annular_sector_mesh(inner_r, outer_r, a0, a1, height, name, n_arc=12):
    pts = []
    for i in range(n_arc + 1):
        a = a0 + (a1 - a0) * i / n_arc
        pts.append((outer_r * math.cos(a), outer_r * math.sin(a)))
    for i in range(n_arc + 1):
        a = a1 - (a1 - a0) * i / n_arc
        pts.append((inner_r * math.cos(a), inner_r * math.sin(a)))
    wp = cq.Workplane("XY").moveTo(pts[0][0], pts[0][1])
    for p in pts[1:]:
        wp = wp.lineTo(p[0], p[1])
    return mesh_from_cadquery(wp.close().extrude(height), name, tolerance=0.0003, angular_tolerance=0.15)


def _dial_disc_mesh(radius, win_a0, win_a1, thickness, hole_r, name):
    n_arc = 20
    disc = cq.Workplane("XY").circle(radius).extrude(thickness)
    cut_r = radius + 0.003
    pts = [(0.0, 0.0)]
    for i in range(n_arc + 1):
        a = win_a0 + (win_a1 - win_a0) * i / n_arc
        pts.append((cut_r * math.cos(a), cut_r * math.sin(a)))
    cutter = cq.Workplane("XY").moveTo(pts[0][0], pts[0][1])
    for p in pts[1:]:
        cutter = cutter.lineTo(p[0], p[1])
    cutter = cutter.close().extrude(thickness + 0.006).translate((0, 0, -0.003))
    disc = disc.cut(cutter)
    hole = cq.Workplane("XY").circle(hole_r).extrude(thickness + 0.006).translate((0, 0, -0.003))
    disc = disc.cut(hole)
    return mesh_from_cadquery(disc, name, tolerance=0.0003, angular_tolerance=0.12)


def _rect_cells(r: ResolvedPillBoxConfig):
    inner_w = r.base_w - 2.0 * RIM_T
    inner_d = r.base_d - 2.0 * RIM_T
    cell_w = (inner_w - (r.cols - 1) * WALL_T) / r.cols
    cell_d = (inner_d - (r.rows - 1) * WALL_T) / r.rows
    cells = []
    for n in range(r.n):
        col = n % r.cols
        row = n // r.cols
        x = (-inner_w / 2.0 + cell_w / 2.0) + col * (cell_w + WALL_T)
        y = (inner_d / 2.0 - cell_d / 2.0) - row * (cell_d + WALL_T)
        cells.append({"n": n, "x": x, "y": y, "w": cell_w, "d": cell_d})
    return cells, cell_w, cell_d


def _emit_rect_base(model, r: ResolvedPillBoxConfig, mats):
    base = model.part("base_tray")
    base.visual(
        rounded_box_mesh(r.base_w, r.base_d, BASE_BOTTOM_H, 0.009, "rounded_base_bottom"),
        origin=Origin(xyz=(0.0, 0.0, BASE_BOTTOM_H / 2.0)), material=mats["frame"], name="rounded_base_bottom", material_class_id="plastic.opaque_glossy_molded",
    )
    zc = BASE_BOTTOM_H + WALL_H / 2.0
    add_box(base, (r.base_w, RIM_T, WALL_H), (0.0, r.base_d / 2.0 - RIM_T / 2.0, zc), mats["frame"], "rear_rim")
    add_box(base, (r.base_w, RIM_T, WALL_H), (0.0, -r.base_d / 2.0 + RIM_T / 2.0, zc), mats["frame"], "front_rim")
    add_box(base, (RIM_T, r.base_d - 2.0 * RIM_T, WALL_H), (-r.base_w / 2.0 + RIM_T / 2.0, 0.0, zc), mats["frame"], "side_rim_0")
    add_box(base, (RIM_T, r.base_d - 2.0 * RIM_T, WALL_H), (r.base_w / 2.0 - RIM_T / 2.0, 0.0, zc), mats["frame"], "side_rim_1")
    cells, cw, cd = _rect_cells(r)
    for c in cells:
        n, x, y, w, d = c["n"], c["x"], c["y"], c["w"], c["d"]
        add_box(base, (w - 2.0 * WALL_T, d - 2.0 * WALL_T, FLOOR_H), (x, y, BASE_BOTTOM_H + FLOOR_H / 2.0), mats["well"], f"well_{n}_floor")
        add_box(base, (w, WALL_T, WALL_H), (x, y + d / 2.0 - WALL_T / 2.0, zc), mats["frame"], f"well_{n}_rear_wall")
        add_box(base, (w, WALL_T, WALL_H), (x, y - d / 2.0 + WALL_T / 2.0, zc), mats["frame"], f"well_{n}_front_wall")
        add_box(base, (WALL_T, d, WALL_H), (x - w / 2.0 + WALL_T / 2.0, y, zc), mats["frame"], f"well_{n}_side_wall_0")
        add_box(base, (WALL_T, d, WALL_H), (x + w / 2.0 - WALL_T / 2.0, y, zc), mats["frame"], f"well_{n}_side_wall_1")
    return base, cells, cw, cd


def _emit_flip_lids(model, r: ResolvedPillBoxConfig, base, mats, cells, cw, cd):
    lids = mats["lids"]
    lid_mesh = rounded_box_mesh(cw - 0.0025, cd - 0.0025, LID_T, 0.0055, "compartment_lid_panel")
    for c in cells:
        n, x, y, d = c["n"], c["x"], c["y"], c["d"]
        w = c["w"]
        lid = model.part(f"compartment_lid_{n}")
        mat = model.material(f"lid_{n}_{r.palette_style}", rgba=lids[n % len(lids)])
        # Rear edge on the hinge line: the panel edge stays seated on the well
        # wall top through the whole flip (fit clearance gathers at the front).
        lid.visual(lid_mesh, origin=Origin(xyz=(0.0, 0.00125 - d / 2.0, LID_T / 2.0)), material=mat, name="lid_panel", material_class_id="plastic.frosted_translucent")
        add_box(lid, (w * 0.55, 0.0030, 0.0011), (0.0, -d + 0.0012, LID_T + 0.00055), mat, "front_fingernail")
        add_box(lid, (0.0020, 0.0020, 0.0006), (0.0, -d / 2.0, LID_T), mats["mark"], "day_mark")
        model.articulation(
            f"base_to_lid_{n}", ArticulationType.REVOLUTE, parent=base, child=lid,
            origin=Origin(xyz=(x, y + d / 2.0, WALL_TOP_Z)), axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=0.6, velocity=3.0, lower=0.0, upper=r.lid_open_angle),
            mating=MatingContract(
                parent_face_geometry=f"well_{n}_rear_wall", parent_face_side="positive_z",
                child_face_geometry="lid_panel", child_face_side="negative_z", contact_tol=0.0025,
            ),
            meta={"source_id": "S_B1"},
        )


def _emit_sliding_cover(model, r: ResolvedPillBoxConfig, base, mats):
    rail_w = 0.004
    rail_d = r.base_d - 0.016
    add_box(base, (rail_w, rail_d, RAIL_H), (-r.base_w / 2.0 + 0.008, 0.0, WALL_TOP_Z + RAIL_H / 2.0), mats["frame"], "slide_rail_0")
    add_box(base, (rail_w, rail_d, RAIL_H), (r.base_w / 2.0 - 0.008, 0.0, WALL_TOP_Z + RAIL_H / 2.0), mats["frame"], "slide_rail_1")
    cover = model.part("sliding_cover")
    cover_w = r.base_w - 0.016
    cover_d = r.base_d - 0.014
    cover.visual(rounded_box_mesh(cover_w, cover_d, COVER_T, 0.008, "cover_panel"),
                 origin=Origin(xyz=(0.0, 0.0, COVER_T / 2.0)), material=mats["cover"], name="cover_panel", material_class_id="plastic.frosted_translucent")
    add_box(cover, (rail_w + 0.001, cover_d - 0.004, 0.0012), (-cover_w / 2.0 + 0.001, 0.0, -0.0004), mats["cover"], "cover_groove_0")
    add_box(cover, (rail_w + 0.001, cover_d - 0.004, 0.0012), (cover_w / 2.0 - 0.001, 0.0, -0.0004), mats["cover"], "cover_groove_1")
    add_box(cover, (0.014, 0.030, COVER_T + 0.003), (-cover_w / 2.0 - 0.004, 0.0, COVER_T / 2.0), mats["cover"], "grip_tab")
    for i in range(3):
        add_box(cover, (0.010, 0.001, 0.001), (-cover_w / 2.0 - 0.004, -0.008 + i * 0.008, COVER_T + 0.0016), mats["mark"], f"grip_ridge_{i}")
    model.articulation(
        "base_to_sliding_cover", ArticulationType.PRISMATIC, parent=base, child=cover,
        origin=Origin(xyz=(0.0, 0.0, COVER_BOTTOM_Z)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=0.30, lower=0.0, upper=r.slide_travel),
        mating=MatingContract(
            parent_face_geometry="slide_rail_0", parent_face_side="positive_z",
            child_face_geometry="cover_panel", child_face_side="negative_z", contact_tol=0.0025,
        ),
        meta={"source_id": "S_B3"},
    )


def _emit_round_dial(model, r: ResolvedPillBoxConfig, mats):
    TR = r.tray_radius
    RIM = 0.003
    POST_R = 0.004
    POST_H = WALL_H + LID_T + 0.010
    N = r.n
    SECTOR = 2.0 * math.pi / N
    WELL_IN = POST_R + 0.003
    WELL_OUT = TR - RIM - 0.001
    GAP = 0.015
    lids = mats["lids"]

    base = model.part("base_tray")
    base.visual(
        mesh_from_cadquery(cq.Workplane("XY").circle(TR).extrude(BASE_BOTTOM_H), "base_plate", tolerance=0.0003, angular_tolerance=0.15),
        origin=Origin(), material=mats["frame"], name="base_plate", material_class_id="plastic.opaque_glossy_molded",
    )
    base.visual(
        mesh_from_cadquery(cq.Workplane("XY").circle(TR).circle(TR - RIM).extrude(WALL_H), "outer_rim", tolerance=0.0003, angular_tolerance=0.15),
        origin=Origin(xyz=(0.0, 0.0, BASE_BOTTOM_H)), material=mats["frame"], name="outer_rim", material_class_id="plastic.opaque_glossy_molded",
    )
    base.visual(Cylinder(radius=POST_R, length=POST_H), origin=Origin(xyz=(0.0, 0.0, POST_H / 2.0)), material=mats["post"], name="center_post", material_class_id="plastic.opaque_glossy_molded")
    WALL_LEN = TR - RIM - POST_R
    WALL_MID = POST_R + WALL_LEN / 2.0
    for i in range(N):
        ang = i * SECTOR
        base.visual(
            Box((WALL_LEN, 0.0020, WALL_H)),
            origin=Origin(xyz=(WALL_MID * math.cos(ang), WALL_MID * math.sin(ang), BASE_BOTTOM_H + WALL_H / 2.0), rpy=(0.0, 0.0, ang)),
            material=mats["frame"], name=f"divider_wall_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        a0 = ang + GAP
        a1 = (i + 1) * SECTOR - GAP
        wmat = model.material(f"welltint_{i}_{r.palette_style}", rgba=lids[i % len(lids)])
        base.visual(
            _annular_sector_mesh(WELL_IN, WELL_OUT, a0, a1, 0.001, f"well_floor_{i}"),
            origin=Origin(xyz=(0.0, 0.0, BASE_BOTTOM_H)), material=wmat, name=f"well_floor_{i}", material_class_id="plastic.frosted_translucent",
        )
    dial = model.part("dial_lid")
    LID_R = TR - 0.002
    win_a0, win_a1 = GAP, SECTOR - GAP
    dial.visual(_dial_disc_mesh(LID_R, win_a0, win_a1, LID_T, POST_R + 0.001, "dial_disc"), origin=Origin(), material=mats["cover"], name="dial_disc", material_class_id="plastic.frosted_translucent")
    grip_a = win_a1 + 0.06
    grip_r = LID_R - 0.008
    dial.visual(
        Box((0.012, 0.006, 0.004)),
        origin=Origin(xyz=(grip_r * math.cos(grip_a), grip_r * math.sin(grip_a), LID_T + 0.0015), rpy=(0.0, 0.0, grip_a)),
        material=mats["cover"], name="grip_tab", material_class_id="plastic.frosted_translucent",
    )
    ind_a = win_a0 - 0.03
    ind_r = LID_R - 0.012
    dial.visual(
        Cylinder(radius=0.0015, length=0.0008),
        origin=Origin(xyz=(ind_r * math.cos(ind_a), ind_r * math.sin(ind_a), LID_T + 0.0004)),
        material=mats["mark"], name="window_indicator", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    model.articulation(
        "base_to_dial_lid", ArticulationType.REVOLUTE, parent=base, child=dial,
        origin=Origin(xyz=(0.0, 0.0, WALL_TOP_Z)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=0.0, upper=SECTOR * (N - 1)),
        mating=MatingContract(
            parent_face_geometry="outer_rim", parent_face_side="positive_z",
            child_face_geometry="dial_disc", child_face_side="negative_z", contact_tol=0.0025,
        ),
        meta={"source_id": "S_B4"},
    )
    return base


# ═══════════════════════════════════════════════════════════════════════════
# Build
# ═══════════════════════════════════════════════════════════════════════════
def build_pill_box(config: Optional[PillBoxConfig] = None, *, assets: Optional[AssetContext] = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    if r.form_family == "bottle":
        mats = {k: model.material(f"pillbottle_{k}_{r.palette_style}", rgba=v) for k, v in BOTTLE_PALETTES[r.palette_style].items()}
        body = _emit_bottle_body(model, r, mats)
        if r.closure == "screw_lift_cap":
            _emit_screw_cap(model, r, body, mats)
        else:
            _emit_fliptop(model, r, body, mats)
    else:
        pal = ORGANIZER_PALETTES[r.palette_style]
        mats = {
            k: (model.material(f"pillorg_{k}_{r.palette_style}", rgba=v) if k != "lids" else v)
            for k, v in pal.items()
        }
        if r.base_form == "round_tray":
            _emit_round_dial(model, r, mats)
        else:
            base, cells, cw, cd = _emit_rect_base(model, r, mats)
            if r.lid_mechanism == "individual_flip_lids":
                _emit_flip_lids(model, r, base, mats, cells, cw, cd)
            else:
                _emit_sliding_cover(model, r, base, mats)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pill_box(seed: int, *, assets: Optional[AssetContext] = None) -> ArticulatedObject:
    return build_pill_box(config_from_seed(seed), assets=assets)


# ═══════════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════════
def run_pill_box_tests(object_model: ArticulatedObject, config: PillBoxConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()

    if r.form_family == "bottle":
        body = object_model.get_part("bottle_body")
        ctx.check("bottle_body_present", body is not None, "bottle_body required")
        ctx.check("fill_present", body is not None and body.get_visual("fill_core") is not None,
                  "softgel fill folded into body")
        ctx.check("label_present", body is not None and body.get_visual("label_band") is not None,
                  "host-conformal label band")

        if r.closure == "screw_lift_cap":
            cap = object_model.get_part("closure_cap")
            lift = object_model.get_articulation("bottle_to_cap")
            ctx.allow_isolated_part(
                cap,
                reason="The screw cap lifts clear of the bottle mouth along +z and loses contact with the body at full travel.",
            )
            ctx.check("cap_present", cap is not None)
            ctx.check("cap_lift_prismatic_z",
                      lift.articulation_type == ArticulationType.PRISMATIC and tuple(lift.axis) == (0.0, 0.0, 1.0),
                      details=f"type={lift.articulation_type}, axis={tuple(lift.axis)}")
            rest_z = ctx.part_world_position(cap)[2]
            with ctx.pose({lift: lift.motion_limits.upper}):
                lifted_z = ctx.part_world_position(cap)[2]
            ctx.check("cap_lifts_up", lifted_z > rest_z + lift.motion_limits.upper * 0.7,
                      details=f"rest={rest_z:.4f}, lifted={lifted_z:.4f}")
        else:
            flip = object_model.get_articulation("body_to_flip_lid")
            lid = object_model.get_part("flip_lid")
            ctx.check("flip_present", lid is not None)
            ctx.check("flip_revolute_y",
                      flip.articulation_type == ArticulationType.REVOLUTE and tuple(flip.axis) == (0.0, 1.0, 0.0),
                      details=f"type={flip.articulation_type}, axis={tuple(flip.axis)}")
            ctx.allow_overlap(lid, body, elem_a="hinge_barrel", elem_b="neck_collar",
                              reason="flip-lid hinge barrel is captured on the collar rim.")
            ctx.allow_overlap(lid, body, elem_a="hinge_ear", elem_b="neck_collar",
                              reason="flip-lid hinge ear seats on the collar rim.")
            with ctx.pose({flip: 0.0}):
                closed = ctx.part_element_world_aabb(lid, elem="lid_disk")
            with ctx.pose({flip: flip.motion_limits.upper}):
                opened = ctx.part_element_world_aabb(lid, elem="lid_disk")
            ctx.check("flip_lid_opens_up", opened[1][2] > closed[1][2] + 0.006,
                      details=f"closed_zmax={closed[1][2]:.4f}, open_zmax={opened[1][2]:.4f}")

    else:
        base = object_model.get_part("base_tray")
        ctx.check("base_tray_present", base is not None, "base_tray required")

        if r.lid_mechanism == "individual_flip_lids":
            ctx.check("all_lids_present", all(object_model.get_part(f"compartment_lid_{n}") for n in range(r.n)),
                      details=f"expected {r.n} lids")
            hinge0 = object_model.get_articulation("base_to_lid_0")
            ctx.check("lid_hinge_revolute_x",
                      hinge0.articulation_type == ArticulationType.REVOLUTE and tuple(hinge0.axis) == (-1.0, 0.0, 0.0),
                      details=f"type={hinge0.articulation_type}, axis={tuple(hinge0.axis)}")
            lid0 = object_model.get_part("compartment_lid_0")
            with ctx.pose({hinge0: 0.0}):
                closed = ctx.part_element_world_aabb(lid0, elem="lid_panel")
            with ctx.pose({hinge0: hinge0.motion_limits.upper}):
                opened = ctx.part_element_world_aabb(lid0, elem="lid_panel")
            ctx.check("lid_flips_up", opened[1][2] > closed[1][2] + 0.012,
                      details=f"closed_zmax={closed[1][2]:.4f}, open_zmax={opened[1][2]:.4f}")

        elif r.lid_mechanism == "single_sliding_cover":
            cover = object_model.get_part("sliding_cover")
            slide = object_model.get_articulation("base_to_sliding_cover")
            ctx.check("cover_present", cover is not None)
            ctx.check("cover_prismatic_x",
                      slide.articulation_type == ArticulationType.PRISMATIC and tuple(slide.axis) == (1.0, 0.0, 0.0),
                      details=f"type={slide.articulation_type}, axis={tuple(slide.axis)}")
            rest_x = ctx.part_world_position(cover)[0]
            with ctx.pose({slide: slide.motion_limits.upper}):
                slid_x = ctx.part_world_position(cover)[0]
            ctx.check("cover_slides_plus_x", slid_x > rest_x + slide.motion_limits.upper * 0.7,
                      details=f"rest_x={rest_x:.4f}, slid_x={slid_x:.4f}")

        else:  # rotating_dial_lid
            dial = object_model.get_part("dial_lid")
            dj = object_model.get_articulation("base_to_dial_lid")
            ctx.check("dial_present", dial is not None)
            ctx.check("dial_revolute_z",
                      dj.articulation_type == ArticulationType.REVOLUTE and abs(tuple(dj.axis)[2]) > 0.99,
                      details=f"type={dj.articulation_type}, axis={tuple(dj.axis)}")
            ctx.allow_overlap(dial, base, elem_a="dial_disc", elem_b="center_post",
                              reason="center pivot post passes through the dial center hole.")
            rest = ctx.part_element_world_aabb(dial, elem="grip_tab")
            with ctx.pose({dj: dj.motion_limits.upper}):
                rot = ctx.part_element_world_aabb(dial, elem="grip_tab")
            ctx.check("dial_rotates",
                      abs(rot[0][0] - rest[0][0]) > 0.004 or abs(rot[0][1] - rest[0][1]) > 0.004,
                      details=f"rest={rest}, rot={rot}")

    # Isolation runs after the family branches so justified detachables
    # (lift-off cap) carry their allowance; the check itself is unchanged.
    ctx.fail_if_isolated_parts()
    # Rule 5: no 穿模 across sampled joint poses (kept modest for many-lid grids).
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=24, ignore_fixed=True)
    return ctx.report()
