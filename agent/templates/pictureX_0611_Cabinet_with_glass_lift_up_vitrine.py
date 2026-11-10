# SPDX-License-Identifier: Apache-2.0

"""pictureX/0611/Cabinet_with_glass_lift-up_vitrine modular template.

A glazed display vitrine whose DEFINING feature is a LIFT-UP glass opening.
Derived from 12 five-star sources (2 origins + 10 forks):

- opening_mechanism (②, defining slot): front_dual_panes (001, REVOLUTE -X),
  front_single_flap (002, REVOLUTE), top_single_lid (var_top_lid_single,
  REVOLUTE rear-hinge), top_gullwing (var_gullwing, dual REVOLUTE about the
  ridge Y-axis), front_slider (var_sliding_glass, PRISMATIC +X).
- body_form (③): low_case / tower / tabletop / wall_mount.
- frame_construction (①): wood / metal / frameless.
- base_style (①): legs / plinth / wall_cleat (gated by body_form).
- shelf_count (N multiplicity): 1..4 interior glass shelves.

All static frame/glass/shelf geometry are visuals of a single ``carcass`` part
(parallel-children pattern). The moving glazed lid/panel/slider is the only
non-FIXED joint; each declares a MatingContract to a visible carcass hinge
barrel / guide rail. Decorative seals/beads/pulls are host visuals (Rule 1).
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
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

# ---------------------------------------------------------------------------
# Self-contained geometry helpers (inlined: a template must not import another
# template or a shared template helper module).
# ---------------------------------------------------------------------------
RGBA = tuple[float, float, float, float]


PALETTES: dict[str, dict[str, RGBA]] = {
    "oak": {
        "wood": (0.58, 0.39, 0.20, 1.0),
        "dark": (0.23, 0.14, 0.08, 1.0),
        "panel": (0.72, 0.58, 0.38, 1.0),
        "metal": (0.62, 0.64, 0.66, 1.0),
        "glass": (0.58, 0.72, 0.82, 0.38),
        "accent": (0.18, 0.30, 0.58, 1.0),
    },
    "painted": {
        "wood": (0.86, 0.84, 0.78, 1.0),
        "dark": (0.22, 0.23, 0.24, 1.0),
        "panel": (0.92, 0.90, 0.84, 1.0),
        "metal": (0.55, 0.56, 0.58, 1.0),
        "glass": (0.62, 0.78, 0.88, 0.35),
        "accent": (0.72, 0.18, 0.14, 1.0),
    },
    "industrial": {
        "wood": (0.38, 0.40, 0.42, 1.0),
        "dark": (0.12, 0.13, 0.14, 1.0),
        "panel": (0.50, 0.52, 0.54, 1.0),
        "metal": (0.72, 0.74, 0.76, 1.0),
        "glass": (0.50, 0.62, 0.70, 0.34),
        "accent": (0.88, 0.58, 0.12, 1.0),
    },
    "walnut": {
        "wood": (0.32, 0.19, 0.10, 1.0),
        "dark": (0.12, 0.07, 0.04, 1.0),
        "panel": (0.43, 0.27, 0.15, 1.0),
        "metal": (0.68, 0.58, 0.36, 1.0),
        "glass": (0.54, 0.66, 0.72, 0.35),
        "accent": (0.78, 0.72, 0.54, 1.0),
    },
    "slate": {
        "wood": (0.165, 0.205, 0.225, 1.0),
        "dark": (0.10, 0.12, 0.13, 1.0),
        "panel": (0.24, 0.29, 0.31, 1.0),
        "metal": (0.68, 0.52, 0.20, 1.0),
        "glass": (0.52, 0.62, 0.66, 0.36),
        "accent": (0.70, 0.55, 0.24, 1.0),
    },
    "jeweler": {
        "wood": (0.34, 0.16, 0.085, 1.0),
        "dark": (0.055, 0.085, 0.082, 1.0),
        "panel": (0.20, 0.075, 0.035, 1.0),
        "metal": (0.47, 0.45, 0.39, 1.0),
        "glass": (0.12, 0.35, 0.23, 0.58),
        "accent": (0.18, 0.42, 0.28, 0.95),
    },
}


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def add_box(part, size, xyz, material, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.oak")


def add_cylinder(
    part,
    *,
    radius: float,
    length: float,
    xyz,
    material,
    name: str,
    rpy=(0.0, 0.0, 0.0),
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.blackened_gunmetal",
    )


def joint_meta(joint_type: ArticulationType, axis, origin, limits: MotionLimits) -> dict[str, object]:
    return {
        "type": joint_type.value,
        "axis": tuple(axis),
        "origin": tuple(origin),
        "range": (limits.lower, limits.upper),
    }


def material_set(model: ArticulatedObject, palette_name: str) -> dict[str, object]:
    palette = PALETTES[palette_name]
    return {key: model.material(f"{palette_name}_{key}", rgba=value) for key, value in palette.items()}


def finish_body_inertial(part, size, mass: float) -> None:
    part.inertial = Inertial.from_geometry(
        Box(size),
        mass=mass,
        origin=Origin(xyz=(0.0, 0.0, size[2] / 2.0)),
    )

__modular__ = True

BodyForm = Literal["low_case", "tower", "tabletop", "wall_mount"]
OpeningMechanism = Literal[
    "front_dual_panes",
    "front_single_flap",
    "top_single_lid",
    "top_gullwing",
    "front_slider",
]
FrameConstruction = Literal["wood", "metal", "frameless"]
BaseStyle = Literal["legs", "plinth", "wall_cleat"]
PaletteStyle = Literal["oak", "painted", "industrial", "walnut"]

_BODY_FORMS = ("low_case", "tower", "tabletop", "wall_mount")
_OPENINGS = (
    "front_dual_panes",
    "front_single_flap",
    "top_single_lid",
    "top_gullwing",
    "front_slider",
)
_FRAMES = ("wood", "metal", "frameless")
_PALETTES = ("oak", "painted", "industrial", "walnut")

_FRONT_OPENERS = frozenset({"front_dual_panes", "front_single_flap", "front_slider"})

BARREL_R = 0.007
GLASS_T = 0.006
BOTTOM_THICKNESS = 0.06


# ── nominal geometry per body form (width, depth, base_h, case_height) ─────
def _body_nominal(body_form: str) -> tuple[float, float, float, float]:
    return {
        "low_case": (1.10, 0.42, 0.24, 0.74),
        "tower": (0.55, 0.40, 0.12, 1.40),
        "tabletop": (0.35, 0.24, 0.05, 0.28),
        "wall_mount": (1.60, 0.32, 0.06, 0.58),
    }[body_form]


def _wall_for_frame(frame: str) -> float:
    return {"wood": 0.045, "metal": 0.030, "frameless": 0.010}[frame]


def _open_face(mechanism: str) -> str:
    return "front" if mechanism in _FRONT_OPENERS else "top"


@dataclass(frozen=True)
class PictureX0611VitrineConfig:
    body_form: BodyForm = "low_case"
    opening_mechanism: OpeningMechanism = "front_dual_panes"
    frame_construction: FrameConstruction = "wood"
    base_style: BaseStyle = "legs"
    palette_style: PaletteStyle = "oak"
    shelf_count: int = 1
    width: float = 1.10
    depth: float = 0.42
    case_height: float = 0.74
    name: str = "picturex_0611_vitrine"


@dataclass(frozen=True)
class ResolvedPictureX0611VitrineConfig:
    body_form: str
    opening_mechanism: str
    frame_construction: str
    base_style: str
    palette_style: str
    shelf_count: int
    width: float
    depth: float
    case_height: float
    base_h: float
    wall: float
    open_face: str
    name: str

    # derived geometry ---------------------------------------------------
    @property
    def opening_bottom(self) -> float:
        return self.base_h + BOTTOM_THICKNESS

    @property
    def case_top(self) -> float:
        return self.opening_bottom + self.case_height

    @property
    def front_y(self) -> float:
        return -self.depth / 2.0

    @property
    def front_opening_width(self) -> float:
        return self.width - 2.0 * self.wall

    @property
    def glazing_height(self) -> float:
        return self.case_height + 0.004

    @property
    def glazing_z(self) -> float:
        return self.opening_bottom + self.case_height / 2.0


def _gate_base(body_form: str, base_style: str) -> str:
    if body_form == "wall_mount":
        return "wall_cleat"
    if body_form == "tabletop":
        return "plinth"
    # legs / plinth only for floor-standing forms
    return base_style if base_style in ("legs", "plinth") else "legs"


def config_from_seed(seed: int) -> PictureX0611VitrineConfig:
    rng = random.Random(seed)
    body_form = rng.choice(_BODY_FORMS)
    opening = rng.choice(_OPENINGS)
    frame = rng.choice(_FRAMES)
    base = _gate_base(body_form, rng.choice(("legs", "plinth")))
    palette = rng.choice(_PALETTES)
    shelf_count = rng.choices((1, 2, 3, 4), weights=(4, 3, 2, 1))[0]

    w0, d0, base_h0, ch0 = _body_nominal(body_form)
    width = round(w0 * rng.uniform(0.90, 1.12), 3)
    depth = round(d0 * rng.uniform(0.92, 1.08), 3)
    case_height = round(ch0 * rng.uniform(0.90, 1.12), 3)

    return PictureX0611VitrineConfig(
        body_form=body_form,
        opening_mechanism=opening,
        frame_construction=frame,
        base_style=base,
        palette_style=palette,
        shelf_count=shelf_count,
        width=width,
        depth=depth,
        case_height=case_height,
        name=f"picturex_0611_vitrine_seed_{seed}",
    )


def resolve_config(config: PictureX0611VitrineConfig) -> ResolvedPictureX0611VitrineConfig:
    body_form = config.body_form if config.body_form in _BODY_FORMS else "low_case"
    opening = config.opening_mechanism if config.opening_mechanism in _OPENINGS else "front_dual_panes"
    frame = config.frame_construction if config.frame_construction in _FRAMES else "wood"
    base = _gate_base(body_form, config.base_style)
    palette = config.palette_style if config.palette_style in _PALETTES else "oak"
    wall = _wall_for_frame(frame)

    w0, d0, base_h0, ch0 = _body_nominal(body_form)
    # Width must stay wide enough to host the opening plus two frame walls.
    width = clamp(config.width, 4.0 * wall + 0.16, 2.2)
    depth = clamp(config.depth, 4.0 * wall + 0.10, 0.55)
    case_height = clamp(config.case_height, 0.22, 1.75)

    return ResolvedPictureX0611VitrineConfig(
        body_form=body_form,
        opening_mechanism=opening,
        frame_construction=frame,
        base_style=base,
        palette_style=palette,
        shelf_count=max(1, min(4, int(config.shelf_count))),
        width=width,
        depth=depth,
        case_height=case_height,
        base_h=base_h0,
        wall=wall,
        open_face=_open_face(opening),
        name=config.name,
    )


def slot_choices_for_config(config: PictureX0611VitrineConfig):
    r = resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("opening_mechanism", r.opening_mechanism),
        ("frame_construction", r.frame_construction),
        ("base_style", r.base_style),
        ("shelf_count", str(r.shelf_count)),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int):
    return slot_choices_for_config(config_from_seed(seed))


# ── materials mapping ─────────────────────────────────────────────────────
def _mats(model: ArticulatedObject, r: ResolvedPictureX0611VitrineConfig) -> dict:
    m = material_set(model, r.palette_style)
    if r.frame_construction == "frameless":
        frame_mat = m["metal"]  # brushed stainless read
    elif r.frame_construction == "metal":
        frame_mat = m["metal"]
    else:
        frame_mat = m["wood"]
    return {
        "frame": frame_mat,
        "glass": m["glass"],
        "edge": m["dark"] if r.frame_construction == "frameless" else m["panel"],
        "hardware": m["dark"],
        "clip": m["accent"],
        "panel": m["panel"],
    }


# ── base / support ────────────────────────────────────────────────────────
def _build_base(carcass, r, mats) -> None:
    w, d = r.width, r.depth
    ob = r.opening_bottom
    # Bottom deck: every base style carries the enclosure on this deck.
    add_box(carcass, (w, d, BOTTOM_THICKNESS), (0.0, 0.0, ob - BOTTOM_THICKNESS / 2.0),
            mats["frame"], "bottom_panel")

    if r.base_style == "legs":
        leg_x = w / 2.0 - max(0.06, r.wall + 0.03)
        leg_y = d / 2.0 - max(0.05, r.wall + 0.02)
        s = min(0.055, w * 0.06)
        for ix, xp in enumerate((-leg_x, leg_x)):
            for iy, yp in enumerate((-leg_y, leg_y)):
                add_box(carcass, (s, s, r.base_h), (xp, yp, r.base_h / 2.0),
                        mats["frame"], f"leg_{ix}_{iy}")
    elif r.base_style == "plinth":
        add_box(carcass, (w * 0.94, d * 0.94, r.base_h), (0.0, 0.0, r.base_h / 2.0),
                mats["frame"], "plinth_box")
        # slim recessed toe-kick reveal (host visual), embedded into the plinth front.
        add_box(carcass, (w * 0.90, 0.016, 0.018), (0.0, -d * 0.44, r.base_h - 0.011),
                mats["edge"], "toe_kick")
    else:  # wall_cleat
        add_box(carcass, (w * 0.94, d * 0.90, r.base_h), (0.0, 0.0, r.base_h / 2.0),
                mats["frame"], "base_plinth")
        # cleat sits behind and against the rear glazing so it stays connected.
        cleat_front = d / 2.0 - r.wall
        cleat_back = d / 2.0 + 0.05
        add_box(carcass, (w * 0.88, cleat_back - cleat_front, 0.06),
                (0.0, (cleat_front + cleat_back) / 2.0, r.case_top - 0.08),
                mats["frame"], "wall_cleat")


# ── frame + glazing enclosure ─────────────────────────────────────────────
def _build_enclosure(carcass, r, mats) -> None:
    w, d = r.width, r.depth
    ob, ct = r.opening_bottom, r.case_top
    wall = r.wall
    gh, gz = r.glazing_height, r.glazing_z
    framed = r.frame_construction != "frameless"
    inner_hw = w / 2.0 - wall
    inner_hd = d / 2.0 - wall

    # Corner posts (framed constructions only).
    if framed:
        post_x = w / 2.0 - wall / 2.0
        post_y = d / 2.0 - wall / 2.0
        ph = ct - ob
        for ix, xp in enumerate((-post_x, post_x)):
            for iy, yp in enumerate((-post_y, post_y)):
                add_box(carcass, (wall, wall, ph), (xp, yp, ob + ph / 2.0),
                        mats["frame"], f"corner_post_{ix}_{iy}")

    # Side glass (left / right); y-extent overruns the corners so the walls
    # meet the front/rear glass (edge-bonded read, and guarantees connectivity).
    for side, xp in enumerate((-inner_hw, inner_hw)):
        add_box(carcass, (0.006, 2.0 * inner_hd + 0.012, gh), (xp, 0.0, gz), mats["glass"],
                f"side_glass_{side}")
        if framed:
            for edge, yp in enumerate((-(inner_hd - 0.01), inner_hd - 0.01)):
                add_box(carcass, (0.012, 0.018, gh), (xp, yp, gz), mats["edge"],
                        f"side_bead_{side}_{edge}")

    # Rear glass (x-extent reaches the side glass at both corners).
    add_box(carcass, (2.0 * inner_hw + 0.006, 0.006, gh), (0.0, inner_hd, gz),
            mats["glass"], "rear_glass")

    # Fixed face opposite the moving opening.
    if r.open_face == "top":
        # front stays fixed glass; top is opened by the lid.
        add_box(carcass, (2.0 * inner_hw + 0.006, 0.006, gh), (0.0, -inner_hd, gz),
                mats["glass"], "front_glass")
    else:
        # top stays a fixed glazed cap; front is opened by pane/slider.
        top_z = ct - 0.006
        add_box(carcass, (2.0 * inner_hw + 0.006, 2.0 * inner_hd + 0.006, 0.006),
                (0.0, 0.0, top_z), mats["glass"], "top_glass")
        if framed:
            # Front top rail is replaced by the opener's own hinge ledge; keep the rear rail.
            add_box(carcass, (w, wall, 0.02), (0.0, d / 2.0 - wall / 2.0, ct - 0.01),
                    mats["frame"], "top_rear_rail")


# ── interior glass shelves (multiplicity N) ───────────────────────────────
def _build_shelves(carcass, r, mats) -> None:
    n = r.shelf_count
    w, d = r.width, r.depth
    wall = r.wall
    sw = w - 2.0 * wall + 0.004
    sd = d - 2.0 * wall + 0.004
    lo = r.opening_bottom + 0.10
    hi = r.case_top - 0.10
    if hi <= lo:
        hi = lo + 0.02
    for s in range(n):
        z = lo + (hi - lo) * (s + 1) / (n + 1)
        add_box(carcass, (sw, sd, 0.008), (0.0, 0.0, z), mats["glass"], f"glass_shelf_{s}")
        cx = sw / 2.0 - 0.02
        cy = sd / 2.0 - 0.02
        for ix, xp in enumerate((-cx, cx)):
            for iy, yp in enumerate((-cy, cy)):
                add_box(carcass, (0.024, 0.03, 0.012), (xp, yp, z - 0.010),
                        mats["clip"], f"shelf_clip_{s}_{ix}_{iy}")


# ── opening mechanisms ────────────────────────────────────────────────────
# Each emitter returns (joint_names, capture_allowances) where a capture
# allowance is (child_part, carcass_elem, child_elem): the ONLY overlaps left
# are captured-hinge / captured-rail interfaces, declared element-scoped in
# run_tests. Every moving glass body clears the fixed glazing at all poses.
def _emit_front_panes(model, carcass, r, mats, *, count: int, framed_flap: bool):
    """One or two top-front-hinged glass panes lifting up and outward (axis -X)."""
    w, d = r.width, r.depth
    wall = r.wall
    ow = r.front_opening_width
    fy = r.front_y  # hinge sits on the front plane
    hinge_z = r.case_top - 0.010
    glass_top_local = -0.014  # glass hangs below the hinge; tab bridges up to it
    pane_h = hinge_z - r.opening_bottom - 0.022
    upper = 1.05 if framed_flap else 1.15

    # Front-top hinge ledge spans the opening and hosts the barrels; its ends
    # overlap the side glass so the whole assembly stays connected.
    add_box(carcass, (w - 2.0 * wall, wall + 0.008, 0.014),
            (0.0, -(d / 2.0 - wall / 2.0 - 0.004), r.case_top - 0.012),
            mats["frame"], "front_hinge_ledge")

    if count == 2:
        seam = 0.010
        pane_w = (ow - seam) / 2.0 - 0.01
        centers = (-(ow / 2.0) + pane_w / 2.0 + 0.006, (ow / 2.0) - pane_w / 2.0 - 0.006)
    else:
        pane_w = ow - 0.03
        centers = (0.0,)

    joints, captures = [], []
    for i, cx in enumerate(centers):
        add_cylinder(carcass, radius=BARREL_R, length=pane_w - 0.03,
                     xyz=(cx, fy, hinge_z + BARREL_R), material=mats["hardware"],
                     name=f"hinge_barrel_{i}", rpy=(0.0, math.pi / 2.0, 0.0))

        pane = model.part(f"glass_panel_{i}")
        # Hinge tab bridges the glass top up to the barrel (+Z face at joint line).
        add_box(pane, (pane_w - 0.03, GLASS_T + 0.006, 0.020), (0.0, 0.0, -0.010),
                mats["hardware"], "hinge_tab")
        gcz = glass_top_local - pane_h / 2.0
        if framed_flap:
            fw = 0.02
            add_box(pane, (pane_w - 2 * fw, GLASS_T, pane_h - 2 * fw), (0.0, 0.0, gcz),
                    mats["glass"], "glass_panel")
            for nm, xx in (("stile_left", -pane_w / 2.0 + fw / 2.0),
                           ("stile_right", pane_w / 2.0 - fw / 2.0)):
                add_box(pane, (fw, GLASS_T + 0.004, pane_h), (xx, 0.0, gcz), mats["frame"], nm)
            add_box(pane, (pane_w, GLASS_T + 0.004, fw),
                    (0.0, 0.0, glass_top_local - pane_h + fw / 2.0), mats["frame"], "bottom_rail")
        else:
            add_box(pane, (pane_w, GLASS_T, pane_h), (0.0, 0.0, gcz), mats["glass"], "glass_panel")
            for nm, xx in (("edge_seal_l", -pane_w / 2.0 + 0.003),
                           ("edge_seal_r", pane_w / 2.0 - 0.003)):
                add_box(pane, (0.005, GLASS_T + 0.004, pane_h), (xx, 0.0, gcz), mats["edge"], nm)
        add_box(pane, (0.05, 0.012, 0.03), (0.0, -0.007, glass_top_local - pane_h + 0.06),
                mats["hardware"], "finger_pull")

        origin = (cx, fy, hinge_z)
        limits = MotionLimits(effort=18.0, velocity=1.1, lower=0.0, upper=upper)
        model.articulation(
            f"panel_lift_{i}", ArticulationType.REVOLUTE, parent=carcass, child=pane,
            origin=Origin(xyz=origin), axis=(-1.0, 0.0, 0.0), motion_limits=limits,
            meta=joint_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), origin, limits),
            mating=MatingContract(
                parent_face_geometry=f"hinge_barrel_{i}", parent_face_side="negative_z",
                child_face_geometry="hinge_tab", child_face_side="positive_z", contact_tol=0.006,
            ),
        )
        joints.append(f"panel_lift_{i}")
        captures.append((f"glass_panel_{i}", f"hinge_barrel_{i}", "hinge_tab"))
        captures.append((f"glass_panel_{i}", "front_hinge_ledge", "hinge_tab"))
    return joints, captures


def _emit_top_single_lid(model, carcass, r, mats):
    """Full-width rear-hinged lift-up top lid (axis -X). Lid body sits forward of
    the hinge support; only the hinge tab bridges back to the barrel/rail."""
    w, d = r.width, r.depth
    wall = r.wall
    inner_hd = d / 2.0 - wall
    rear_y = inner_hd
    hinge_z = r.case_top + 0.006
    lid_w = w - 2.0 * wall - 0.05
    lid_d = d - 2.0 * wall - 0.09
    rear_gap = 0.05  # lid body starts this far forward of the hinge line

    add_box(carcass, (lid_w, wall, 0.016), (0.0, rear_y, r.case_top),
            mats["frame"], "hinge_rail")
    add_cylinder(carcass, radius=BARREL_R, length=lid_w - 0.04,
                 xyz=(0.0, rear_y, hinge_z + BARREL_R), material=mats["hardware"],
                 name="hinge_barrel", rpy=(0.0, math.pi / 2.0, 0.0))

    lid = model.part("lid")
    # Tab spans from the barrel (world y=rear_y) forward into the lid rear frame
    # so it connects both the carcass hinge and the lid's own body.
    add_box(lid, (lid_w - 0.04, 0.062, 0.010), (0.0, -0.023, -0.005), mats["hardware"], "hinge_tab")
    gy = -rear_gap - lid_d / 2.0
    add_box(lid, (lid_w, lid_d, GLASS_T), (0.0, gy, -0.014), mats["glass"], "lid_glass")
    fw = 0.018
    add_box(lid, (lid_w, fw, 0.012), (0.0, gy - lid_d / 2.0 + fw / 2.0, -0.014),
            mats["frame"], "lid_frame_front")
    add_box(lid, (lid_w, fw, 0.012), (0.0, gy + lid_d / 2.0 - fw / 2.0, -0.014),
            mats["frame"], "lid_frame_rear")
    for nm, xx in (("lid_frame_left", -lid_w / 2.0 + fw / 2.0), ("lid_frame_right", lid_w / 2.0 - fw / 2.0)):
        add_box(lid, (fw, lid_d, 0.012), (xx, gy, -0.014), mats["frame"], nm)
    add_box(lid, (0.05, 0.03, 0.012), (0.0, gy - lid_d / 2.0 + 0.02, -0.004),
            mats["hardware"], "finger_pull")

    origin = (0.0, rear_y, hinge_z)
    limits = MotionLimits(effort=18.0, velocity=1.1, lower=0.0, upper=1.30)
    model.articulation(
        "lid_lift", ArticulationType.REVOLUTE, parent=carcass, child=lid,
        origin=Origin(xyz=origin), axis=(-1.0, 0.0, 0.0), motion_limits=limits,
        meta=joint_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), origin, limits),
        mating=MatingContract(
            parent_face_geometry="hinge_barrel", parent_face_side="negative_z",
            child_face_geometry="hinge_tab", child_face_side="positive_z", contact_tol=0.006,
        ),
    )
    return ["lid_lift"], [("lid", "hinge_barrel", "hinge_tab"), ("lid", "hinge_rail", "hinge_tab"),
                          ("lid", "rear_glass", "hinge_tab")]


def _emit_top_gullwing(model, carcass, r, mats):
    """Two ridge-hinged top lids opening outward about the central Y-axis."""
    w, d = r.width, r.depth
    wall = r.wall
    inner_hw = w / 2.0 - wall
    inner_hd = d / 2.0 - wall
    hinge_z = r.case_top + 0.014
    lid_d = 2.0 * inner_hd - 0.05
    half_w = max(0.05, inner_hw - 0.08)

    # Thin central spine rests on the front + rear glazing tops and hosts both
    # ridge barrels (spans full depth so it is supported at both ends).
    add_box(carcass, (0.02, 2.0 * inner_hd + 0.006, 0.03), (0.0, 0.0, r.case_top + 0.010),
            mats["frame"], "central_ridge")

    joints, captures = [], []
    for idx, side in enumerate((-1.0, 1.0)):
        name = "left_lid" if side < 0 else "right_lid"
        axis = (0.0, 1.0 if side < 0 else -1.0, 0.0)
        add_cylinder(carcass, radius=BARREL_R, length=lid_d - 0.03,
                     xyz=(0.0, 0.0, hinge_z + BARREL_R), material=mats["hardware"],
                     name=f"hinge_barrel_{idx}", rpy=(math.pi / 2.0, 0.0, 0.0))

        lid = model.part(name)
        # Tab reaches from the ridge barrel (x~0, z=hinge line) out and down to the
        # lid glass so it ties the hinge to the lid's own body.
        add_box(lid, (0.05, lid_d - 0.04, 0.024), (side * 0.028, 0.0, -0.012),
                mats["hardware"], "hinge_tab")
        gx = side * (0.04 + half_w / 2.0)
        add_box(lid, (half_w, lid_d, GLASS_T), (gx, 0.0, -0.024), mats["glass"], "lid_glass")
        fw = 0.016
        add_box(lid, (fw, lid_d, 0.012), (side * (0.04 + half_w) - side * fw / 2.0, 0.0, -0.024),
                mats["frame"], "outer_rail")

        origin = (0.0, 0.0, hinge_z)
        limits = MotionLimits(effort=16.0, velocity=1.0, lower=0.0, upper=1.20)
        jn = f"gullwing_lift_{idx}"
        model.articulation(
            jn, ArticulationType.REVOLUTE, parent=carcass, child=lid,
            origin=Origin(xyz=origin), axis=axis, motion_limits=limits,
            meta=joint_meta(ArticulationType.REVOLUTE, axis, origin, limits),
            mating=MatingContract(
                parent_face_geometry=f"hinge_barrel_{idx}", parent_face_side="negative_z",
                child_face_geometry="hinge_tab", child_face_side="positive_z", contact_tol=0.006,
            ),
        )
        joints.append(jn)
        # Both ridge barrels are concentric at x=0, so each lid's tab grazes both.
        captures.append((name, "hinge_barrel_0", "hinge_tab"))
        captures.append((name, "hinge_barrel_1", "hinge_tab"))
        captures.append((name, "central_ridge", "hinge_tab"))
    return joints, captures


def _emit_front_slider(model, carcass, r, mats):
    """Framed clear-glass panel sliding sideways along top/bottom rails (PRISMATIC +X)."""
    ow = r.front_opening_width
    fy = r.front_y - 0.006
    gz = r.glazing_z
    panel_w = ow * 0.52
    panel_h = r.glazing_height - 0.014
    travel = ow - panel_w
    rest_x = -ow / 2.0 + panel_w / 2.0

    panel_top = gz + panel_h / 2.0
    panel_bot = gz - panel_h / 2.0
    # Two front jambs run deck->top at the opening sides, hosting the rails and
    # keeping the whole slide frame connected to the carcass.
    for ji, jx in enumerate((-(ow / 2.0 + 0.012), ow / 2.0 + 0.012)):
        add_box(carcass, (0.014, 0.03, r.case_top - r.opening_bottom),
                (jx, fy, (r.opening_bottom + r.case_top) / 2.0), mats["frame"], f"slide_jamb_{ji}")
    add_box(carcass, (ow + 0.02, 0.018, 0.012), (0.0, fy, panel_top + 0.006),
            mats["frame"], "top_guide_rail")
    add_box(carcass, (ow + 0.02, 0.018, 0.012), (0.0, fy, panel_bot - 0.006),
            mats["frame"], "bottom_track")

    slider = model.part("slider")
    fw = 0.018
    fd = 0.014
    add_box(slider, (panel_w - 2 * fw, GLASS_T, panel_h - 2 * fw), (0.0, 0.0, 0.0),
            mats["glass"], "glass_pane")
    add_box(slider, (panel_w, fd, fw), (0.0, 0.0, panel_h / 2.0 - fw / 2.0), mats["frame"], "frame_top")
    add_box(slider, (panel_w, fd, fw), (0.0, 0.0, -panel_h / 2.0 + fw / 2.0), mats["frame"], "frame_bottom")
    for nm, xx in (("frame_left", -panel_w / 2.0 + fw / 2.0), ("frame_right", panel_w / 2.0 - fw / 2.0)):
        add_box(slider, (fw, fd, panel_h - 2 * fw), (xx, 0.0, 0.0), mats["frame"], nm)
    add_box(slider, (0.03, 0.016, 0.06), (panel_w / 2.0 - fw - 0.01, -fd / 2.0 - 0.006, 0.0),
            mats["hardware"], "finger_pull")

    origin = (rest_x, fy, gz)
    limits = MotionLimits(effort=12.0, velocity=0.4, lower=0.0, upper=travel)
    model.articulation(
        "slide", ArticulationType.PRISMATIC, parent=carcass, child=slider,
        origin=Origin(xyz=origin), axis=(1.0, 0.0, 0.0), motion_limits=limits,
        meta=joint_meta(ArticulationType.PRISMATIC, (1.0, 0.0, 0.0), origin, limits),
        mating=MatingContract(
            parent_face_geometry="top_guide_rail", parent_face_side="negative_z",
            child_face_geometry="frame_top", child_face_side="positive_z", contact_tol=0.006,
        ),
    )
    return ["slide"], [("slider", "top_guide_rail", "frame_top"),
                       ("slider", "bottom_track", "frame_bottom")]


def _build_opening(model, carcass, r, mats):
    mech = r.opening_mechanism
    if mech == "front_dual_panes":
        return _emit_front_panes(model, carcass, r, mats, count=2, framed_flap=False)
    if mech == "front_single_flap":
        return _emit_front_panes(model, carcass, r, mats, count=1, framed_flap=True)
    if mech == "top_single_lid":
        return _emit_top_single_lid(model, carcass, r, mats)
    if mech == "top_gullwing":
        return _emit_top_gullwing(model, carcass, r, mats)
    return _emit_front_slider(model, carcass, r, mats)


# ── top-level build ───────────────────────────────────────────────────────
def build_picturex_0611_vitrine(
    config: PictureX0611VitrineConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or PictureX0611VitrineConfig())
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _mats(model, r)

    carcass = model.part("carcass", meta={"image_role": "glazed vitrine carcass"})
    _build_base(carcass, r, mats)
    _build_enclosure(carcass, r, mats)
    _build_shelves(carcass, r, mats)
    finish_body_inertial(carcass, (r.width, r.depth, r.case_top), 22.0)

    _, captures = _build_opening(model, carcass, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(config or PictureX0611VitrineConfig())
    model.meta["open_face"] = r.open_face
    model.meta["hinge_captures"] = tuple(captures)
    return model


def build_seeded_picturex_0611_vitrine(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_vitrine(config_from_seed(seed), assets=assets)


# convenience aliases matching the slug spelling
build_pictureX_0611_Cabinet_with_glass_lift_up_vitrine = build_picturex_0611_vitrine
build_seeded_pictureX_0611_Cabinet_with_glass_lift_up_vitrine = build_seeded_picturex_0611_vitrine


# ── tests ─────────────────────────────────────────────────────────────────
def _elem_center(aabb):
    if aabb is None:
        return None
    mn, mx = aabb
    return tuple((float(mn[i]) + float(mx[i])) / 2.0 for i in range(3))


def _moving_parts(r) -> tuple[str, ...]:
    mech = r.opening_mechanism
    if mech == "front_dual_panes":
        return ("glass_panel_0", "glass_panel_1")
    if mech == "front_single_flap":
        return ("glass_panel_0",)
    if mech == "top_single_lid":
        return ("lid",)
    if mech == "top_gullwing":
        return ("left_lid", "right_lid")
    return ("slider",)


def run_picturex_0611_vitrine_tests(
    object_model: ArticulatedObject, config: PictureX0611VitrineConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()

    carcass = object_model.get_part("carcass")
    carcass_visuals = {v.name for v in carcass.visuals}

    # Identity: glazed enclosure + interior shelves.
    ctx.check("glazed side walls present",
              {"side_glass_0", "side_glass_1", "rear_glass"}.issubset(carcass_visuals),
              details=str(sorted(carcass_visuals)))
    ctx.check("interior glass shelf present",
              any(n.startswith("glass_shelf_") for n in carcass_visuals),
              details=str(sorted(n for n in carcass_visuals if n.startswith("glass_shelf_"))))
    ctx.check("slot_choices recorded",
              set(dict(object_model.meta.get("slot_choices", ())))
              >= {"body_form", "opening_mechanism", "frame_construction", "base_style",
                  "shelf_count", "palette_style"},
              details=str(object_model.meta.get("slot_choices")))

    # Moving parts + non-fixed joints exist.
    for pn in _moving_parts(r):
        ctx.check(f"moving part {pn} present", object_model.get_part(pn) is not None)
    non_fixed = [j for j in object_model.articulations
                 if j.articulation_type != ArticulationType.FIXED]
    ctx.check("at least one lift-up joint", len(non_fixed) >= 1,
              details=str([j.name for j in non_fixed]))
    for j in non_fixed:
        ctx.check(f"{j.name} has metadata",
                  {"type", "axis", "origin", "range"}.issubset(j.meta), details=str(j.meta))

    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    # Captured hinge / rail contacts are intentional local overlaps, scoped to
    # the exact (carcass hardware elem, child interface elem) pair so any real
    # glass-vs-case collision stays visible.
    for child_part, carcass_elem, child_elem in object_model.meta.get("hinge_captures", ()):
        ctx.allow_overlap(carcass, object_model.get_part(child_part),
                          elem_a=carcass_elem, elem_b=child_elem,
                          reason="glazed lid/panel/slider is captured on the carcass hinge "
                                 "barrel / rail via this interface (declared MatingContract)")

    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=96, overlap_tol=0.004, ignore_fixed=True, ignore_adjacent=True,
    )

    # Targeted motion semantics per mechanism.
    mech = r.opening_mechanism
    if mech in ("front_dual_panes", "front_single_flap"):
        pane = object_model.get_part("glass_panel_0")
        joint = object_model.get_articulation("panel_lift_0")
        # The pane pivots about its top-front hinge, so its glass centroid swings
        # forward (-Y) and up (+Z) while the top edge stays at the hinge line.
        rest = _elem_center(ctx.part_element_world_aabb(pane, elem="glass_panel"))
        with ctx.pose({joint: joint.motion_limits.upper}):
            openp = _elem_center(ctx.part_element_world_aabb(pane, elem="glass_panel"))
        ctx.check("front pane lifts up and outward",
                  rest is not None and openp is not None
                  and openp[1] < rest[1] - 0.03 and openp[2] > rest[2] + 0.02,
                  details=f"rest={rest}, open={openp}")
    elif mech == "top_single_lid":
        lid = object_model.get_part("lid")
        joint = object_model.get_articulation("lid_lift")
        rest = ctx.part_element_world_aabb(lid, elem="lid_glass")
        with ctx.pose({joint: 1.0}):
            openb = ctx.part_element_world_aabb(lid, elem="lid_glass")
        ctx.check("top lid raises its front edge",
                  rest is not None and openb is not None and openb[1][2] > rest[1][2] + 0.10,
                  details=f"rest={rest}, open={openb}")
    elif mech == "top_gullwing":
        for pn, jn in (("left_lid", "gullwing_lift_0"), ("right_lid", "gullwing_lift_1")):
            lid = object_model.get_part(pn)
            joint = object_model.get_articulation(jn)
            rest = ctx.part_element_world_aabb(lid, elem="lid_glass")
            with ctx.pose({joint: joint.motion_limits.upper}):
                openb = ctx.part_element_world_aabb(lid, elem="lid_glass")
            ctx.check(f"{pn} lifts outward-up",
                      rest is not None and openb is not None and openb[1][2] > rest[1][2] + 0.08,
                      details=f"rest={rest}, open={openb}")
    else:  # front_slider
        slider = object_model.get_part("slider")
        joint = object_model.get_articulation("slide")
        rest = ctx.part_world_position(slider)
        with ctx.pose({joint: joint.motion_limits.upper}):
            openp = ctx.part_world_position(slider)
        min_shift = max(0.04, 0.5 * joint.motion_limits.upper)
        ctx.check("slider translates sideways at constant height",
                  rest is not None and openp is not None
                  and openp[0] > rest[0] + min_shift and abs(openp[2] - rest[2]) < 0.006,
                  details=f"rest={rest}, open={openp}, min_shift={min_shift}")

    return ctx.report()


run_pictureX_0611_Cabinet_with_glass_lift_up_vitrine_tests = run_picturex_0611_vitrine_tests
