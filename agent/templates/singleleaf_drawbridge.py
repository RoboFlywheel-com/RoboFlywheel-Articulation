# SPDX-License-Identifier: Apache-2.0

"""Single-leaf drawbridge (bascule) — modular procedural template.

A grounded ``fixed_support`` (Slot A: abutment / twin-tower machinery /
torus-ring road abutment / cadquery bored shore) hosts one REVOLUTE joint
joining a single ``bridge_leaf`` (Slot B) about the rear-corner trunnion
line. Slot C selects the hinge-bearing topology: 2-part trunk
(``trunnion_tube_in_cylinder_housing`` / ``trunnion_shaft_through_torus_ring``
/ ``leaf_sleeve_over_support_pin``) vs 4-part trunk
(``separate_bearing_parts`` — two independent FIXED ``left_bearing``/
``right_bearing`` parts seated on the support). Slot D and Slot E are GATED
baked-visual extensions on the leaf (topside_extras) and support
(shore_context) respectively — no new DOFs.

Identity invariant: every seed has exactly one REVOLUTE leaf_hinge joint.

Motion convention: the hinge axis is +X; ``0 rad`` is the horizontal closed
deck (the rest pose rendered in viewer thumbnails). A positive angle lifts the
leaf UP, a negative angle dips it DOWN below horizontal. Per seed the limits are
sampled as ``upper ∈ [+30°, +60°]`` (lift) and ``lower ∈ [-45°, -15°]`` (dip).

seed=0 anchor: masonry_abutment + box_deck_girder +
trunnion_tube_in_cylinder_housing + curb_guard + bare_abutment.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
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
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True


SupportStyle = Literal[
    "masonry_abutment",
    "twin_tower_machinery",
    "torus_ring_road_abutment",
    "cadquery_bored_shore",
]
LeafStyle = Literal[
    "box_deck_girder",
    "railed_road_leaf",
    "mesh_girder_leaf",
    "bascule_counterweight_leaf",
]
HingeBearing = Literal[
    "trunnion_tube_in_cylinder_housing",
    "trunnion_shaft_through_torus_ring",
    "leaf_sleeve_over_support_pin",
    "separate_bearing_parts",
]
TopsideExtras = Literal["curb_guard", "rail_balustrade", "tread_underside_ribs"]
ShoreContext = Literal["bare_abutment", "approach_receiving_span", "channel_water_context"]
PaletteTheme = Literal["river_gray", "ocean_steel", "rural_iron", "industrial_red"]


SUPPORT_MODULES: tuple[SupportStyle, ...] = (
    "masonry_abutment",
    "twin_tower_machinery",
    "torus_ring_road_abutment",
    "cadquery_bored_shore",
)
LEAF_MODULES: tuple[LeafStyle, ...] = (
    "box_deck_girder",
    "railed_road_leaf",
    "mesh_girder_leaf",
    "bascule_counterweight_leaf",
)
BEARING_MODULES: tuple[HingeBearing, ...] = (
    "trunnion_tube_in_cylinder_housing",
    "trunnion_shaft_through_torus_ring",
    "leaf_sleeve_over_support_pin",
    "separate_bearing_parts",
)
TOPSIDE_MODULES: tuple[TopsideExtras, ...] = (
    "curb_guard",
    "rail_balustrade",
    "tread_underside_ribs",
)
SHORE_MODULES: tuple[ShoreContext, ...] = (
    "bare_abutment",
    "approach_receiving_span",
    "channel_water_context",
)

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "river_gray": {
        "stone": (0.55, 0.55, 0.57, 1.0),
        "stone_dark": (0.40, 0.40, 0.42, 1.0),
        "deck": (0.45, 0.45, 0.47, 1.0),
        "asphalt": (0.18, 0.18, 0.20, 1.0),
        "steel": (0.55, 0.57, 0.60, 1.0),
        "warning": (0.95, 0.78, 0.10, 1.0),
        "water": (0.18, 0.40, 0.55, 1.0),
        "rail": (0.32, 0.32, 0.34, 1.0),
        "dark": (0.10, 0.10, 0.12, 1.0),
    },
    "ocean_steel": {
        "stone": (0.50, 0.52, 0.55, 1.0),
        "stone_dark": (0.32, 0.35, 0.38, 1.0),
        "deck": (0.30, 0.32, 0.35, 1.0),
        "asphalt": (0.12, 0.12, 0.14, 1.0),
        "steel": (0.55, 0.60, 0.65, 1.0),
        "warning": (0.95, 0.78, 0.10, 1.0),
        "water": (0.10, 0.30, 0.40, 1.0),
        "rail": (0.22, 0.22, 0.25, 1.0),
        "dark": (0.06, 0.06, 0.08, 1.0),
    },
    "rural_iron": {
        "stone": (0.62, 0.55, 0.42, 1.0),
        "stone_dark": (0.40, 0.34, 0.24, 1.0),
        "deck": (0.40, 0.34, 0.24, 1.0),
        "asphalt": (0.20, 0.18, 0.16, 1.0),
        "steel": (0.30, 0.30, 0.30, 1.0),
        "warning": (0.95, 0.78, 0.10, 1.0),
        "water": (0.20, 0.35, 0.40, 1.0),
        "rail": (0.22, 0.22, 0.22, 1.0),
        "dark": (0.10, 0.08, 0.06, 1.0),
    },
    "industrial_red": {
        "stone": (0.60, 0.55, 0.55, 1.0),
        "stone_dark": (0.45, 0.40, 0.38, 1.0),
        "deck": (0.50, 0.45, 0.40, 1.0),
        "asphalt": (0.18, 0.18, 0.20, 1.0),
        "steel": (0.85, 0.20, 0.15, 1.0),
        "warning": (0.95, 0.78, 0.10, 1.0),
        "water": (0.18, 0.40, 0.55, 1.0),
        "rail": (0.85, 0.20, 0.15, 1.0),
        "dark": (0.10, 0.10, 0.12, 1.0),
    },
}


@dataclass(frozen=True)
class SingleleafDrawbridgeConfig:
    support_style: SupportStyle | None = None
    leaf_style: LeafStyle | None = None
    hinge_bearing: HingeBearing | None = None
    topside_extras: TopsideExtras | None = None
    shore_context: ShoreContext | None = None
    palette_theme: PaletteTheme = "river_gray"
    span_length: float = 6.0
    deck_width: float = 2.0
    deck_thickness: float = 0.20
    support_height: float = 1.6
    trunnion_radius: float = 0.18
    # Motion limits about the hinge line. 0 rad == horizontal closed deck
    # (the rest pose shown in viewer thumbnails). Positive angle (axis +X)
    # lifts the leaf UP; negative angle dips it DOWN below horizontal.
    leaf_open_upper: float = 1.047  # +60° (max up)
    leaf_open_lower: float = -0.524  # -30° (down)
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["river_gray"])
    )


@dataclass(frozen=True)
class ResolvedSingleleafDrawbridgeConfig:
    support_style: SupportStyle
    leaf_style: LeafStyle
    hinge_bearing: HingeBearing
    topside_extras: TopsideExtras
    shore_context: ShoreContext
    palette_theme: PaletteTheme
    span_length: float
    deck_width: float
    deck_thickness: float
    support_height: float
    trunnion_radius: float
    leaf_open_upper: float
    leaf_open_lower: float
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _add_bolt_z(
    p,
    *,
    x: float,
    y: float,
    z_face: float,
    radius: float,
    head_len: float,
    embed: float,
    material: str,
    name: str,
) -> None:
    """Bolt head standing proud of a +Z face, embedded by ``embed`` (0004 _add_bolt_on_z_face)."""
    p.visual(
        Cylinder(radius=radius, length=head_len),
        origin=Origin(xyz=(x, y, z_face + 0.5 * head_len - embed)),
        material=material,
        name=name, material_class_id="metal.blackened_gunmetal",
    )


def _add_bolt_x(
    p,
    *,
    x_face: float,
    y: float,
    z: float,
    radius: float,
    head_len: float,
    embed: float,
    material: str,
    name: str,
) -> None:
    """Bolt head on a ±X face (axis along x), embedded by ``embed`` (0004 _add_bolt_on_y_face)."""
    sign = 1.0 if x_face >= 0.0 else -1.0
    p.visual(
        Cylinder(radius=radius, length=head_len),
        origin=Origin(
            xyz=(x_face + sign * (0.5 * head_len - embed), y, z),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=material,
        name=name, material_class_id="metal.blackened_gunmetal",
    )


def _cap_and_course(
    p,
    *,
    cx: float,
    cy: float,
    cz: float,
    sx: float,
    sy: float,
    sz: float,
    name: str,
    core_material: str = "stone",
    trim_material: str = "stone_dark",
) -> None:
    """Break up a plain masonry block into core + overhanging coping cap +
    mid string course + base plinth + corner pilasters, so a tall block reads
    as a layered abutment instead of a featureless slab (303cdd7f cutwater /
    coping courses; c5bac345 webs read as vertical strips)."""
    t = _clamp(sz * 0.09, 0.06, 0.30)
    p.visual(
        Box((sx, sy, sz)),
        origin=Origin(xyz=(cx, cy, cz)),
        material=core_material,
        name=f"{name}_core", material_class_id="stone.masonry_wall",
    )
    p.visual(
        Box((sx * 1.06, sy * 1.08, t)),
        origin=Origin(xyz=(cx, cy, cz + sz * 0.5 - t * 0.5)),
        material=trim_material,
        name=f"{name}_coping", material_class_id="stone.cut_sedimentary",
    )
    p.visual(
        Box((sx * 1.03, sy * 1.05, t * 0.75)),
        origin=Origin(xyz=(cx, cy, cz + sz * 0.12)),
        material=trim_material,
        name=f"{name}_string_course", material_class_id="stone.cut_sedimentary",
    )
    p.visual(
        Box((sx * 1.10, sy * 1.10, t * 1.2)),
        origin=Origin(xyz=(cx, cy, cz - sz * 0.5 + t * 0.6)),
        material=trim_material,
        name=f"{name}_plinth", material_class_id="stone.cut_sedimentary",
    )
    for psign, pside in ((+1, "r"), (-1, "l")):
        p.visual(
            Box((t * 1.1, sy * 0.62, sz * 0.86)),
            origin=Origin(xyz=(cx + psign * sx * 0.5, cy, cz)),
            material=trim_material,
            name=f"{name}_pilaster_{pside}", material_class_id="stone.cut_sedimentary",
        )


def config_from_seed(seed: int) -> SingleleafDrawbridgeConfig:
    if seed == 0:
        return SingleleafDrawbridgeConfig(
            support_style="masonry_abutment",
            leaf_style="box_deck_girder",
            hinge_bearing="trunnion_tube_in_cylinder_housing",
            topside_extras="curb_guard",
            shore_context="bare_abutment",
            palette_theme="river_gray",
            span_length=6.0,
            deck_width=2.0,
            deck_thickness=0.20,
            support_height=1.6,
            trunnion_radius=0.18,
            leaf_open_upper=1.047,
            leaf_open_lower=-0.524,
        )
    rng = random.Random(seed)
    span = rng.uniform(2.5, 10.0)
    return SingleleafDrawbridgeConfig(
        support_style=rng.choice(SUPPORT_MODULES),  # type: ignore[arg-type]
        leaf_style=rng.choice(LEAF_MODULES),  # type: ignore[arg-type]
        hinge_bearing=rng.choice(BEARING_MODULES),  # type: ignore[arg-type]
        topside_extras=rng.choice(TOPSIDE_MODULES),  # type: ignore[arg-type]
        shore_context=rng.choice(SHORE_MODULES),  # type: ignore[arg-type]
        palette_theme=rng.choice(tuple(PALETTES.keys())),  # type: ignore[arg-type]
        span_length=round(span, 3),
        deck_width=round(rng.uniform(1.0, 3.5), 3),
        deck_thickness=round(rng.uniform(0.12, 0.30), 3),
        support_height=round(rng.uniform(0.80, 2.8), 3),
        trunnion_radius=round(rng.uniform(0.10, 0.30), 3),
        # Per-seed motion range: lift up to +30°..+60°, dip down to -45°..-15°.
        leaf_open_upper=round(rng.uniform(math.radians(30.0), math.radians(60.0)), 3),
        leaf_open_lower=round(rng.uniform(math.radians(-45.0), math.radians(-15.0)), 3),
    )


def resolve_config(config: SingleleafDrawbridgeConfig) -> ResolvedSingleleafDrawbridgeConfig:
    support = config.support_style or "masonry_abutment"
    leaf = config.leaf_style or "box_deck_girder"
    bearing = config.hinge_bearing or "trunnion_tube_in_cylinder_housing"
    topside = config.topside_extras or "curb_guard"
    shore = config.shore_context or "bare_abutment"
    for value, pool, label in (
        (support, SUPPORT_MODULES, "support_style"),
        (leaf, LEAF_MODULES, "leaf_style"),
        (bearing, BEARING_MODULES, "hinge_bearing"),
        (topside, TOPSIDE_MODULES, "topside_extras"),
        (shore, SHORE_MODULES, "shore_context"),
    ):
        if value not in pool:
            raise ValueError(f"Unsupported {label}: {value!r}")
    if config.palette_theme not in PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme!r}")
    return ResolvedSingleleafDrawbridgeConfig(
        support_style=support,
        leaf_style=leaf,
        hinge_bearing=bearing,
        topside_extras=topside,
        shore_context=shore,
        palette_theme=config.palette_theme,
        span_length=_clamp(config.span_length, 1.5, 14.0),
        deck_width=_clamp(config.deck_width, 0.6, 4.2),
        deck_thickness=_clamp(config.deck_thickness, 0.08, 0.45),
        support_height=_clamp(config.support_height, 0.6, 3.5),
        trunnion_radius=_clamp(config.trunnion_radius, 0.06, 0.40),
        # up capped at +60°, down capped at -45° (0 == horizontal closed deck).
        leaf_open_upper=_clamp(config.leaf_open_upper, math.radians(15.0), math.radians(60.0)),
        leaf_open_lower=_clamp(config.leaf_open_lower, math.radians(-45.0), 0.0),
        palette=dict(PALETTES[config.palette_theme]),
    )


# --------------------------------------------------------------------------- #
# Slot A: fixed_support
# --------------------------------------------------------------------------- #


def _build_support(model: ArticulatedObject, r: ResolvedSingleleafDrawbridgeConfig) -> None:
    """Emit the fixed_support root part. The trunnion line is at
    (x=0, y=0, z=support_height). The hinge_block (a Box) is always
    emitted at the trunnion line so the joint origin lies on real
    geometry regardless of style.
    """
    style = r.support_style
    W = r.deck_width * 1.4  # support is wider than leaf
    H = r.support_height
    abut_depth = max(1.0, r.span_length * 0.20)
    p = model.part("fixed_support")
    # Foundation slab
    p.visual(
        Box((W, abut_depth, max(0.20, H * 0.15))),
        origin=Origin(xyz=(0.0, -abut_depth * 0.5, max(0.20, H * 0.15) * 0.5)),
        material="stone_dark",
        name="foundation", material_class_id="concrete.rough_weathered",
    )
    # Main support body
    body_h = H - max(0.20, H * 0.15)
    body_z = max(0.20, H * 0.15) + body_h * 0.5
    if style == "masonry_abutment":
        # Layered stone abutment (core + coping/string course/plinth/pilasters)
        _cap_and_course(
            p,
            cx=0.0,
            cy=-abut_depth * 0.40,
            cz=body_z,
            sx=W * 0.92,
            sy=abut_depth * 0.85,
            sz=body_h,
            name="abutment",
        )
        # Roadway surface on the abutment top (303cdd7f roadway_surface)
        p.visual(
            Box((W * 0.80, abut_depth * 0.55, max(0.04, body_h * 0.05))),
            origin=Origin(xyz=(0.0, -abut_depth * 0.40, body_z + body_h * 0.5 + 0.02)),
            material="asphalt",
            name="roadway_surface", material_class_id="asphalt.plain_road",
        )
        # Cutwater face on the front
        p.visual(
            Box((W * 0.30, 0.30, body_h * 0.92)),
            origin=Origin(xyz=(0.0, 0.05, body_z)),
            material="stone",
            name="cutwater", material_class_id="stone.masonry_wall",
        )
    elif style == "twin_tower_machinery":
        # Twin built-up steel machinery towers flanking the hinge line
        # (c5bac345 inner/outer web + front/back cheek + saddle + crown + brace).
        tx0 = W * 0.32
        ty0 = -abut_depth * 0.30
        tw_x = W * 0.20
        tw_y = abut_depth * 0.5
        web_t = max(0.06, tw_x * 0.18)
        for sign, side in ((+1, "right"), (-1, "left")):
            tx = sign * tx0
            # masonry plinth the tower stands on
            p.visual(
                Box((tw_x * 1.25, tw_y * 1.1, body_h * 0.22)),
                origin=Origin(xyz=(tx, ty0, body_z - body_h * 0.5 + body_h * 0.11)),
                material="stone",
                name=f"tower_{side}_plinth", material_class_id="stone.masonry_wall",
            )
            # front + back vertical web plates
            for ysign, web in ((+1, "front"), (-1, "back")):
                p.visual(
                    Box((tw_x, web_t, body_h * (0.96 if web == "front" else 0.88))),
                    origin=Origin(xyz=(tx, ty0 + ysign * tw_y * 0.32, body_z)),
                    material="steel",
                    name=f"tower_{side}_{web}_web", material_class_id="metal.paint_coated",
                )
            # inner + outer side plates bridging front/back (keeps frame connected)
            for xsign, sidew in ((+1, "outer"), (-1, "inner")):
                p.visual(
                    Box((web_t, tw_y * 0.74, body_h * 0.92)),
                    origin=Origin(xyz=(tx + sign * xsign * tw_x * 0.42, ty0, body_z)),
                    material="steel",
                    name=f"tower_{side}_{sidew}_web", material_class_id="metal.paint_coated",
                )
            # front cheek toward the hinge + saddle pad + bearing cap
            p.visual(
                Box((tw_x * 0.9, tw_y * 0.22, body_h * 0.5)),
                origin=Origin(xyz=(tx, ty0 + tw_y * 0.40, body_z + body_h * 0.12)),
                material="dark",
                name=f"tower_{side}_cheek", material_class_id="metal.blackened_gunmetal",
            )
            p.visual(
                Box((tw_x * 0.7, abut_depth * 0.30, body_h * 0.14)),
                origin=Origin(xyz=(tx, ty0 + tw_y * 0.48, body_z + body_h * 0.30)),
                material="steel",
                name=f"tower_{side}_saddle", material_class_id="metal.steel_bare",
            )
            # overhanging crown cap
            p.visual(
                Box((tw_x * 1.22, tw_y * 0.92, body_h * 0.10)),
                origin=Origin(xyz=(tx, ty0, body_z + body_h * 0.5)),
                material="steel",
                name=f"tower_{side}_crown", material_class_id="metal.paint_coated",
            )
            # outer diagonal brace
            p.visual(
                Box((web_t, tw_y * 0.7, body_h * 0.55)),
                origin=Origin(
                    xyz=(tx + sign * tw_x * 0.5, ty0, body_z),
                    rpy=(0.0, sign * 0.5, 0.0),
                ),
                material="steel",
                name=f"tower_{side}_brace", material_class_id="metal.paint_coated",
            )
        # drive cabinet between towers
        p.visual(
            Box((W * 0.40, abut_depth * 0.30, body_h * 0.45)),
            origin=Origin(xyz=(0.0, -abut_depth * 0.35, body_z - body_h * 0.20)),
            material="dark",
            name="drive_cabinet", material_class_id="metal.paint_coated",
        )
    elif style == "torus_ring_road_abutment":
        # Roadway abutment with torus bearing ring (layered core)
        _cap_and_course(
            p,
            cx=0.0,
            cy=-abut_depth * 0.40,
            cz=body_z,
            sx=W * 0.95,
            sy=abut_depth * 0.85,
            sz=body_h,
            name="abutment",
        )
        # Approach slab on top
        p.visual(
            Box((W, abut_depth * 0.30, 0.10)),
            origin=Origin(xyz=(0.0, -abut_depth * 0.25, body_z + body_h * 0.5 + 0.05)),
            material="asphalt",
            name="approach_slab", material_class_id="asphalt.plain_road",
        )
        # Torus bearing ring decorative ring at trunnion
        try:
            p.visual(
                mesh_from_geometry(
                    TorusGeometry(radius=r.trunnion_radius * 1.2, tube=0.04, tubular_segments=24),
                    "torus_ring",
                ),
                origin=Origin(xyz=(0.0, 0.0, H), rpy=(0.0, math.pi / 2.0, 0.0)),
                material="steel",
                name="torus_bearing_ring", material_class_id="metal.steel_bare",
            )
        except Exception:
            pass
    else:  # cadquery_bored_shore
        # Bored block shore — layered block with a (fake) bored cylindrical pocket
        _cap_and_course(
            p,
            cx=0.0,
            cy=-abut_depth * 0.40,
            cz=body_z,
            sx=W * 0.95,
            sy=abut_depth * 0.85,
            sz=body_h,
            name="bored_block",
        )
        # Cross tie / bracket
        p.visual(
            Box((W * 0.75, 0.12, 0.30)),
            origin=Origin(xyz=(0.0, -abut_depth * 0.55, body_z + body_h * 0.35)),
            material="stone_dark",
            name="cross_tie", material_class_id="concrete.rough_weathered",
        )

    # Mandatory hinge_block — sits at the trunnion line (y=0, z=H) and
    # hosts the leaf_hinge joint origin. Must always be present.
    bearing_x = r.deck_width * 0.45
    p.visual(
        Box((W * 0.92, 0.30, 0.30)),
        origin=Origin(xyz=(0.0, 0.0, H)),
        material="steel",
        name="hinge_block", material_class_id="metal.steel_bare",
    )
    # Style-specific bearing hardware
    if r.hinge_bearing == "trunnion_tube_in_cylinder_housing":
        # Cylinder housing visuals on the left/right sides
        for sign, side in ((+1, "right"), (-1, "left")):
            p.visual(
                Cylinder(radius=r.trunnion_radius * 1.30, length=0.25),
                origin=Origin(xyz=(sign * bearing_x, 0.0, H), rpy=(0.0, math.pi / 2.0, 0.0)),
                material="steel",
                name=f"bearing_housing_{side}", material_class_id="metal.steel_bare",
            )
    elif r.hinge_bearing == "trunnion_shaft_through_torus_ring":
        # Pedestal saddles holding the ring
        for sign, side in ((+1, "right"), (-1, "left")):
            p.visual(
                Box((0.20, 0.25, 0.25)),
                origin=Origin(xyz=(sign * bearing_x, 0.0, H)),
                material="steel",
                name=f"pedestal_{side}", material_class_id="metal.steel_bare",
            )
    elif r.hinge_bearing == "leaf_sleeve_over_support_pin":
        # Baked hinge pin Cylinder spanning width
        p.visual(
            Cylinder(radius=r.trunnion_radius * 0.85, length=W * 0.95),
            origin=Origin(xyz=(0.0, 0.0, H), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="steel",
            name="hinge_pin", material_class_id="metal.steel_bare",
        )
    # (separate_bearing_parts handled below — bearing is its own part.)

    # Slot E: shore context baked visuals
    if r.shore_context == "approach_receiving_span":
        # Approach (near-side) + receiving (far-side) deck slabs flanking the
        # leaf. Both baked on the support.
        appr_depth = r.span_length * 0.45
        # Approach: behind the support, sitting on top
        p.visual(
            Box((r.deck_width, appr_depth, 0.10)),
            origin=Origin(xyz=(0.0, -abut_depth * 0.5 - appr_depth * 0.5, H + 0.05)),
            material="asphalt",
            name="approach_deck", material_class_id="asphalt.plain_road",
        )
        # Receiving span on the far side (water side)
        p.visual(
            Box((r.deck_width, r.span_length * 0.30, 0.10)),
            origin=Origin(
                xyz=(
                    0.0,
                    abut_depth * 0.0 + r.span_length * 1.10 + r.span_length * 0.15,
                    H + 0.05,
                )
            ),
            material="asphalt",
            name="receiving_deck", material_class_id="asphalt.plain_road",
        )
        # Far-side pier holding the receiving deck up
        p.visual(
            Box((r.deck_width * 0.92, 0.40, H)),
            origin=Origin(xyz=(0.0, abut_depth * 0.0 + r.span_length * 1.10, H * 0.5)),
            material="stone",
            name="far_pier", material_class_id="stone.masonry_wall",
        )
        # Water surface connecting near and far structures
        water_depth = r.span_length * 1.30
        p.visual(
            Box((W * 1.6, water_depth, 0.02)),
            origin=Origin(xyz=(0.0, r.span_length * 0.55, -0.010)),
            material="water",
            name="water_surface", material_class_id="liquid.water_wave_foam",
        )
    elif r.shore_context == "channel_water_context":
        # Water plane + cutwater + approach + receiving + control tower
        water_depth = r.span_length * 1.5
        p.visual(
            Box((W * 1.8, water_depth, 0.02)),
            origin=Origin(xyz=(0.0, r.span_length * 0.5, -0.010)),
            material="water",
            name="water_surface", material_class_id="liquid.water_wave_foam",
        )
        # Far-side abutment (mirrored, layered core)
        _cap_and_course(
            p,
            cx=0.0,
            cy=r.span_length * 1.10 + abut_depth * 0.40,
            cz=H * 0.5,
            sx=W,
            sy=abut_depth * 0.85,
            sz=H,
            name="far_abutment",
        )
        # Operator control house: pedestal column + glazed body + window band +
        # overhanging roof + roof parapet + signal mast (a9f8a88 control tower).
        ctx = W * 0.45
        cty = -abut_depth * 0.20
        cw = max(W * 0.18, 0.30)
        cd = max(0.25, abut_depth * 0.18)
        chh = H * 0.7
        ctz = H + chh * 0.5
        p.visual(
            Box((cw * 0.7, cd * 0.7, H)),
            origin=Origin(xyz=(ctx, cty, H * 0.5)),
            material="stone_dark",
            name="control_tower_pedestal", material_class_id="stone.masonry_wall",
        )
        p.visual(
            Box((cw, cd, chh)),
            origin=Origin(xyz=(ctx, cty, ctz)),
            material="stone",
            name="control_tower", material_class_id="stone.masonry_wall",
        )
        p.visual(
            Box((cw * 1.03, cd * 1.05, chh * 0.20)),
            origin=Origin(xyz=(ctx, cty, ctz + chh * 0.16)),
            material="dark",
            name="control_tower_windows", material_class_id="glass.smoked_tinted",
        )
        p.visual(
            Box((cw * 1.38, cd * 1.48, max(0.04, chh * 0.09))),
            origin=Origin(xyz=(ctx, cty, ctz + chh * 0.5 + chh * 0.045)),
            material="steel",
            name="control_tower_roof", material_class_id="metal.paint_coated",
        )
        p.visual(
            Box((cw * 1.18, cd * 1.28, max(0.03, chh * 0.07))),
            origin=Origin(xyz=(ctx, cty, ctz + chh * 0.5 + chh * 0.12)),
            material="rail",
            name="control_tower_parapet", material_class_id="metal.paint_coated",
        )
        p.visual(
            Cylinder(radius=max(0.02, cw * 0.06), length=chh * 0.55),
            origin=Origin(xyz=(ctx, cty, ctz + chh * 0.5 + chh * 0.40)),
            material="steel",
            name="control_tower_mast", material_class_id="metal.paint_coated",
        )

    p.inertial = Inertial.from_geometry(
        Box((W, abut_depth, H)),
        mass=50.0,
        origin=Origin(xyz=(0.0, -abut_depth * 0.3, H * 0.5)),
    )


def _build_bearing_part(
    model: ArticulatedObject, r: ResolvedSingleleafDrawbridgeConfig, *, side: int, name: str
) -> None:
    """Build a single bearing part (for separate_bearing_parts variant)."""
    p = model.part(name)
    # Mount block
    p.visual(
        Box((0.25, 0.30, 0.20)),
        origin=Origin(xyz=(0.0, 0.0, -0.05)),
        material="steel",
        name="mount_block", material_class_id="metal.steel_bare",
    )
    # Bearing shell — Cylinder along x axis covering origin
    p.visual(
        Cylinder(radius=r.trunnion_radius * 1.35, length=0.22),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material="steel",
        name="bearing_shell", material_class_id="metal.steel_bare",
    )
    p.inertial = Inertial.from_geometry(
        Box((0.25, 0.30, 0.40)), mass=2.0, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )


# --------------------------------------------------------------------------- #
# Slot B: bridge_leaf
# --------------------------------------------------------------------------- #


def _build_leaf(model: ArticulatedObject, r: ResolvedSingleleafDrawbridgeConfig) -> None:
    """Build the bridge leaf. Part frame origin is at the hinge line. The
    deck extends from y=0 (heel) to y=span_length (tip)."""
    style = r.leaf_style
    span = r.span_length
    dw = r.deck_width
    dt = r.deck_thickness
    p = model.part("bridge_leaf")
    # Trunnion tube — full width along x at the hinge line (leaf origin).
    trunnion_radius = r.trunnion_radius
    p.visual(
        Cylinder(radius=trunnion_radius, length=dw * 1.05),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material="steel",
        name="trunnion", material_class_id="metal.steel_bare",
    )
    # Trunnion hub + shaft collar at each end (c5bac345 trunnion hub/collar).
    for sign, side in ((+1, "right"), (-1, "left")):
        p.visual(
            Cylinder(radius=trunnion_radius * 1.55, length=0.10),
            origin=Origin(xyz=(sign * dw * 0.40, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="steel",
            name=f"trunnion_hub_{side}", material_class_id="metal.steel_bare",
        )
        p.visual(
            Cylinder(radius=trunnion_radius * 1.25, length=0.06),
            origin=Origin(xyz=(sign * dw * 0.46, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="steel",
            name=f"shaft_collar_{side}", material_class_id="metal.steel_bare",
        )

    # Shared deck geometry references.
    deck_cy = span * 0.5 + 0.10
    edge_x = dw * 0.42
    web_t = max(0.06, dw * 0.05)
    girder_h = _clamp(max(dt * 2.4, span * 0.07), 0.22, 1.10)
    girder_z = dt * 0.5 - girder_h * 0.5  # I-beam web hangs below the deck plate
    flange_t = max(0.03, dt * 0.4)

    # Heel torque beam — deep box straddling the trunnion (0004 hinge_torque_beam).
    heel_h = _clamp(max(dt * 2.2, girder_h * 0.9), 0.18, 1.00)
    p.visual(
        Box((dw, 0.46, heel_h)),
        origin=Origin(xyz=(0.0, 0.23, 0.0)),
        material="deck",
        name="heel_crossbeam", material_class_id="concrete.smooth_cast",
    )
    # Deck plate (running +y to span_length).
    p.visual(
        Box((dw, span, dt)),
        origin=Origin(xyz=(0.0, deck_cy, dt * 0.5)),
        material="deck",
        name="deck_plate", material_class_id="concrete.smooth_cast",
    )
    # Two non-skid wear strips on the deck surface (0004 wear_strip / 303cdd7f leaf_surface).
    wear_t = max(0.01, dt * 0.12)
    for sign, side in ((+1, "right"), (-1, "left")):
        p.visual(
            Box((dw * 0.34, span * 0.90, wear_t)),
            origin=Origin(xyz=(sign * dw * 0.22, deck_cy, dt + wear_t * 0.5)),
            material="asphalt",
            name=f"wear_strip_{side}", material_class_id=("asphalt.weathered_damaged" if r.palette_theme == "rural_iron" else "asphalt.plain_road"),
        )
    # Deep I-girders (web + top/bottom flange) along y (303cdd7f main_girder / 0004 leaf_girder).
    for sign, side in ((+1, "right"), (-1, "left")):
        p.visual(
            Box((web_t, span * 0.95, girder_h)),
            origin=Origin(xyz=(sign * edge_x, deck_cy, girder_z)),
            material="steel",
            name=f"girder_web_{side}", material_class_id="metal.paint_coated",
        )
        p.visual(
            Box((max(0.12, dw * 0.11), span * 0.95, flange_t)),
            origin=Origin(xyz=(sign * edge_x, deck_cy, dt * 0.5 - flange_t * 0.5)),
            material="steel",
            name=f"girder_topflange_{side}", material_class_id="metal.paint_coated",
        )
        p.visual(
            Box((max(0.14, dw * 0.13), span * 0.95, flange_t)),
            origin=Origin(xyz=(sign * edge_x, deck_cy, girder_z - girder_h * 0.5 + flange_t * 0.5)),
            material="steel",
            name=f"girder_botflange_{side}", material_class_id="metal.paint_coated",
        )
    # Transverse floorbeams under the deck (303cdd7f floorbeam).
    fb_count = int(_clamp(round(span / 1.2), 4, 8))
    fb_h = girder_h * 0.55
    for i in range(fb_count):
        frac = (i + 1) / (fb_count + 1)
        p.visual(
            Box((dw * 0.94, max(0.08, dw * 0.06), fb_h)),
            origin=Origin(xyz=(0.0, span * frac + 0.10, dt * 0.5 - fb_h * 0.5)),
            material="steel",
            name=f"floorbeam_{i}", material_class_id="metal.paint_coated",
        )
    # Hinge cheeks + gussets tying the trunnion to the girders (0004 hinge_cheek/gusset).
    cheek_h = _clamp(max(dt * 2.2, girder_h * 0.8), 0.20, 0.90)
    for sign, side in ((+1, "right"), (-1, "left")):
        p.visual(
            Box((web_t, 0.16, cheek_h)),
            origin=Origin(xyz=(sign * edge_x, 0.22, 0.0)),
            material="steel",
            name=f"hinge_cheek_{side}", material_class_id="metal.paint_coated",
        )
        p.visual(
            Box((max(0.05, dw * 0.04), 0.34, max(0.05, dt * 0.5))),
            origin=Origin(xyz=(sign * edge_x, 0.30, dt * 0.5), rpy=(0.62, 0.0, 0.0)),
            material="steel",
            name=f"hinge_gusset_up_{side}", material_class_id="metal.paint_coated",
        )
        p.visual(
            Box((max(0.05, dw * 0.04), 0.30, max(0.05, dt * 0.45))),
            origin=Origin(xyz=(sign * edge_x, 0.28, girder_z), rpy=(-0.55, 0.0, 0.0)),
            material="steel",
            name=f"hinge_gusset_lo_{side}", material_class_id="metal.paint_coated",
        )
    # Tip: end floorbeam + nose plate (0004 nose_beam + tip nose).
    p.visual(
        Box((dw, max(0.18, dw * 0.12), girder_h * 0.70)),
        origin=Origin(xyz=(0.0, span + 0.05, dt * 0.5 - girder_h * 0.35)),
        material="steel",
        name="nose_beam", material_class_id="metal.paint_coated",
    )
    p.visual(
        Box((dw, 0.22, dt)),
        origin=Origin(xyz=(0.0, span + 0.20, dt * 0.5)),
        material="deck",
        name="tip_nose", material_class_id="concrete.smooth_cast",
    )
    # Bolt detailing — deck-edge rows (top face) + girder outer-face rows (0004 bolt arrays).
    bolt_r = _clamp(dw * 0.012, 0.010, 0.030)
    bolt_head = max(0.02, dt * 0.18)
    bolt_embed = bolt_head * 0.4
    n_deck = int(_clamp(round(span / 0.9), 4, 10))
    for sign, side in ((+1, "right"), (-1, "left")):
        for k in range(n_deck):
            _add_bolt_z(
                p,
                x=sign * dw * 0.40,
                y=span * (k + 0.5) / n_deck + 0.10,
                z_face=dt,
                radius=bolt_r,
                head_len=bolt_head,
                embed=bolt_embed,
                material="dark",
                name=f"deck_bolt_{side}_{k}",
            )
    n_g = int(_clamp(round(span / 1.4), 3, 7))
    for sign, side in ((+1, "right"), (-1, "left")):
        for k in range(n_g):
            _add_bolt_x(
                p,
                x_face=sign * (edge_x + web_t * 0.5),
                y=span * (k + 0.5) / n_g + 0.10,
                z=girder_z,
                radius=bolt_r,
                head_len=bolt_head,
                embed=bolt_embed,
                material="dark",
                name=f"girder_bolt_{side}_{k}",
            )

    # Style-specific extras
    if style == "railed_road_leaf":
        # Asphalt road surface + lane markings + curb caps
        p.visual(
            Box((dw * 0.85, span * 0.95, 0.02)),
            origin=Origin(xyz=(0.0, span * 0.5 + 0.10, dt + 0.01)),
            material="asphalt",
            name="road_surface", material_class_id=("asphalt.weathered_damaged" if r.palette_theme == "rural_iron" else "asphalt.plain_road"),
        )
        p.visual(
            Box((0.05, span * 0.85, 0.005)),
            origin=Origin(xyz=(0.0, span * 0.5 + 0.10, dt + 0.022)),
            material="warning",
            name="lane_marking", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        for sign, side in ((+1, "right"), (-1, "left")):
            p.visual(
                Box((0.08, span * 0.92, 0.06)),
                origin=Origin(xyz=(sign * dw * 0.45, span * 0.5 + 0.10, dt + 0.030)),
                material="stone",
                name=f"curb_cap_{side}", material_class_id="stone.cut_sedimentary",
            )
    elif style == "mesh_girder_leaf":
        # Stiffer mesh — additional center girder
        p.visual(
            Box((0.14, span * 0.95, dt * 1.8)),
            origin=Origin(xyz=(0.0, span * 0.5 + 0.10, 0.0)),
            material="steel",
            name="center_girder", material_class_id="metal.paint_coated",
        )
    elif style == "bascule_counterweight_leaf":
        # Counterweight box BEHIND the trunnion (y < 0)
        cw_w = dw
        cw_d = span * 0.35
        cw_h = max(0.30, dt * 2.0)
        p.visual(
            Box((cw_w, cw_d, cw_h)),
            origin=Origin(xyz=(0.0, -cw_d * 0.5 - 0.10, -cw_h * 0.5 + 0.05)),
            material="stone_dark",
            name="counterweight", material_class_id="concrete.rough_weathered",
        )
        # Cross brace from trunnion area to counterweight (vertical Box)
        p.visual(
            Box((dw * 0.50, 0.10, max(0.20, dt * 1.5))),
            origin=Origin(xyz=(0.0, -0.10, 0.0)),
            material="steel",
            name="brace_neck", material_class_id="metal.paint_coated",
        )

    # Slot D: topside extras (baked)
    if r.topside_extras == "rail_balustrade":
        # Rail posts on both sides
        post_count = max(4, int(span / 0.8))
        for sign, side in ((+1, "right"), (-1, "left")):
            for k in range(post_count):
                frac = (k + 0.5) / post_count
                p.visual(
                    Box((0.04, 0.04, 0.50)),
                    origin=Origin(xyz=(sign * dw * 0.46, span * frac + 0.10, dt + 0.25)),
                    material="rail",
                    name=f"rail_post_{side}_{k}", material_class_id="metal.paint_coated",
                )
            # Top rail running along y
            p.visual(
                Box((0.04, span * 0.95, 0.04)),
                origin=Origin(xyz=(sign * dw * 0.46, span * 0.5 + 0.10, dt + 0.50)),
                material="rail",
                name=f"top_rail_{side}", material_class_id="metal.paint_coated",
            )
    elif r.topside_extras == "tread_underside_ribs":
        # Underside ribs (additional cross ribs)
        for i in range(6):
            frac = (i + 1) / 7.0
            p.visual(
                Box((dw * 0.90, 0.08, dt * 0.6)),
                origin=Origin(xyz=(0.0, span * frac, -dt * 0.5)),
                material="steel",
                name=f"underside_rib_{i}", material_class_id="metal.paint_coated",
            )
    else:  # curb_guard (default)
        for sign, side in ((+1, "right"), (-1, "left")):
            p.visual(
                Box((0.10, span * 0.92, 0.10)),
                origin=Origin(xyz=(sign * dw * 0.44, span * 0.5 + 0.10, dt + 0.05)),
                material="warning",
                name=f"curb_{side}", material_class_id="metal.paint_coated",
            )

    p.inertial = Inertial.from_geometry(
        Box((dw, span + 0.40, dt + girder_h + 0.30)),
        mass=20.0,
        origin=Origin(xyz=(0.0, deck_cy, girder_z)),
    )


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #


def build_singleleaf_drawbridge(
    config: SingleleafDrawbridgeConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="singleleaf_drawbridge", assets=assets)
    for material, rgba in r.palette.items():
        model.material(material, rgba=rgba)

    _build_support(model, r)
    support = model.get_part("fixed_support")

    # Slot C: optional separate bearing parts.
    if r.hinge_bearing == "separate_bearing_parts":
        for sign, name in ((+1, "right_bearing"), (-1, "left_bearing")):
            _build_bearing_part(model, r, side=sign, name=name)
            # Place each bearing FIXED at the trunnion line, offset along x.
            model.articulation(
                f"frame_to_{name}",
                ArticulationType.FIXED,
                parent=support,
                child=model.get_part(name),
                origin=Origin(xyz=(sign * r.deck_width * 0.45, 0.0, r.support_height)),
            )

    _build_leaf(model, r)
    leaf = model.get_part("bridge_leaf")
    model.articulation(
        "leaf_hinge",
        ArticulationType.REVOLUTE,
        parent=support,
        child=leaf,
        origin=Origin(xyz=(0.0, 0.0, r.support_height)),
        # +X axis: 0 rad == horizontal closed deck, positive lifts the leaf UP,
        # negative dips it DOWN below horizontal.
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=50.0,
            velocity=0.5,
            lower=r.leaf_open_lower,
            upper=r.leaf_open_upper,
        ),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_singleleaf_drawbridge(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_singleleaf_drawbridge(config_from_seed(seed), assets=assets)


def slot_choices_for_config(
    r: ResolvedSingleleafDrawbridgeConfig,
) -> list[tuple[str, str]]:
    return [
        ("support", r.support_style),
        ("leaf", r.leaf_style),
        ("hinge_bearing", r.hinge_bearing),
        ("topside_extras", r.topside_extras),
        ("shore_context", r.shore_context),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    name_set = {p.name for p in model.parts}
    # Trunnion captured by bearing housing on support
    if "bridge_leaf" in name_set and "fixed_support" in name_set:
        ctx.allow_overlap(
            model.get_part("fixed_support"),
            model.get_part("bridge_leaf"),
            reason="trunnion / shaft collar are seated in the support bearing geometry (captured pivot)",
        )
    for nm in ("left_bearing", "right_bearing"):
        if nm in name_set:
            ctx.allow_overlap(
                model.get_part("fixed_support"),
                model.get_part(nm),
                reason=f"{nm} sits on the support hinge block (FIXED mounted bearing)",
            )
            if "bridge_leaf" in name_set:
                ctx.allow_overlap(
                    model.get_part(nm),
                    model.get_part("bridge_leaf"),
                    reason=f"leaf trunnion seats inside {nm} shell (press-fit pivot)",
                )
    if "left_bearing" in name_set and "right_bearing" in name_set:
        ctx.allow_overlap(
            model.get_part("left_bearing"),
            model.get_part("right_bearing"),
            reason="bearings share the trunnion centerline footprint",
        )


def run_singleleaf_drawbridge_tests(
    object_model: ArticulatedObject, config: SingleleafDrawbridgeConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlaps(ctx, object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.030)
    ctx.fail_if_joint_mating_has_gap()

    parts = {p.name for p in object_model.parts}
    ctx.check("support_present", "fixed_support" in parts)
    ctx.check("leaf_present", "bridge_leaf" in parts)
    revolutes = [
        j for j in object_model.articulations if j.articulation_type == ArticulationType.REVOLUTE
    ]
    ctx.check(
        "exactly_one_revolute_hinge",
        len(revolutes) == 1,
        details=f"expected 1 REVOLUTE leaf_hinge, got {len(revolutes)}",
    )
    if r.hinge_bearing == "separate_bearing_parts":
        ctx.check("left_bearing_present", "left_bearing" in parts)
        ctx.check("right_bearing_present", "right_bearing" in parts)
    return ctx.report()


__all__ = [
    "HingeBearing",
    "LeafStyle",
    "PaletteTheme",
    "ResolvedSingleleafDrawbridgeConfig",
    "ShoreContext",
    "SingleleafDrawbridgeConfig",
    "SupportStyle",
    "TopsideExtras",
    "__modular__",
    "build_seeded_singleleaf_drawbridge",
    "build_singleleaf_drawbridge",
    "config_from_seed",
    "resolve_config",
    "run_singleleaf_drawbridge_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
