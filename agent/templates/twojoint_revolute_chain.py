# SPDX-License-Identifier: Apache-2.0

"""Two-joint serial revolute chain — modular procedural template.

This template uses the slot/module/assembler abstraction in
``agent.templates._modular``. Three slots — **base**, **links**, **terminal**
— each pick from a candidate pool sourced from the 5-star
``twojoint_revolute_chain`` sample family. The assembler wires the base to
the link pair with a single ``MatingContract``-backed REVOLUTE chain joint
(``joint_1``); the link pair carries its own internal REVOLUTE ``joint_2``;
the terminal slot (when separate) is FIXED to ``link_2`` (``joint_3``).

Core identity (per spec): the smallest serial hinge chain — a grounded /
fixed base that supports ``link_1``, which in turn supports ``link_2``,
with **exactly two serial revolute joints** whose axes are strictly
parallel and swing in the same plane. ``link_2``'s tip carries a compact
end tab/pad, either fused into ``link_2`` (integral, 3 parts / 2 joints)
or as a separate FIXED part (4 parts / +1 fixed joint).

Slot graph (mixed: linear chain + terminal multiplicity)::

    [base]  --joint_1 REVOLUTE-->  [link_1] --joint_2 REVOLUTE--> [link_2]
                                                         ┊ joint_3 FIXED (only if separate terminal)
                                                         v
                                              [terminal: integral | separate pad | separate clamp]

Candidates:

  base (Slot A, 5 — root supporting joint_1):
    - pedestal_column          (anchor; rec_..._785b L72-L87: foot plate +
                                vertical column + top ears)
    - grounded_clevis_bracket  (rec_..._9bd9 L92-L139: base plate + rear web
                                + dual ears forming a clevis)
    - wall_backplate           (rec_..._98f91b L31-L53: vertical wall plate +
                                forward root_mount lug + lag bolts)
    - broad_mounting_plate     (rec_..._4fc35 L74-L93: wide low-profile plate
                                + four countersunk screws, planar-yaw friendly)
    - side_cheek_plate         (rec_..._140c L99-L133: single D-nosed side
                                cheek + boss + pin, planar side-mount)

  links (Slot B, 6 — cross-section/hinge construction shared by BOTH links):
    - solid_box_beam           (anchor; rec_..._0001 L41-L52: solid box beam +
                                end blocks — simplest)
    - clevis_ear_bore          (rec_..._56e0 L156-L220: cadquery proximal eye +
                                strap + distal dual-ear, bored pin holes)
    - windowed_open_frame      (rec_..._785b L89-L111: cadquery box body with a
                                central window cut + tip yoke slot)
    - dual_sideplate_ladder    (rec_..._9bd9 L48-L89: two parallel side plates +
                                end caps + central windows, ladder frame)
    - flat_extrude_capsule     (rec_..._140c L35-L69: ExtrudeWithHoles capsule /
                                tapered flat link, rounded pin ends)
    - primitive_lug_barrel     (rec_..._0004 L84-L152: primitive Box lug +
                                Cylinder barrel/boss hinge block)

  terminal (Slot C, 3 — link_2 tip form):
    - integral_end_tab         (anchor; rec_..._140c L128-L152: end tab fused
                                into link_2 — no extra part, exactly 2 joints)
    - separate_fixed_pad       (rec_..._0001 L55-L59: independent tool/pad part,
                                FIXED to link_2 tip — 4 parts)
    - separate_fixed_clamp     (rec_..._98f91b L100-L132: independent clamp plate
                                + jaw pads + bolts, FIXED to link_2 — 4 parts)

Cross-cutting ``axis_family`` gates the two revolute axes (which are always
identical tuples):
  - vertical_pitch (anchor): both axes = (0, -1, 0); base lifts joint_1 to
    ``joint1_axis_z``; the chain swings in the X-Z plane.
  - planar_yaw: both axes = (0, 0, 1); low-profile base; the chain swings in
    the X-Y plane.

seed == 0 always picks the anchor combination (pedestal_column +
solid_box_beam + integral_end_tab + vertical_pitch).

Mating model: every chain/internal hinge mates a parent knuckle (+z face)
to the child link's ``*_hub`` (-z face) at the pivot via a MatingContract;
the intentional capture overlap is allow-listed in ``run_*_tests``. The
knuckle *shape and vertical spacing are axis-family-specific* (see the
``_emit_parent_clevis`` helper):

  - ``vertical_pitch`` (axis -y): a boxy clevis (top_lug + lower_lug) that
    straddles the pivot. The swing lifts the child clear, so the layered
    clevis-height spacing reads as a normal hinge.
  - ``planar_yaw`` (axis +z): a **coaxial cylinder boss** (rotation does not
    sweep any off-axis corner) and a **small parallel-deck step** sized to the
    two link body half-thicknesses, so consecutive links sit in tight parallel
    planes — never coplanar (which interpenetrates) and never a clevis-height
    apart (which reads as floating). This mirrors the 5-star planar sample
    (``rec_..._140c``), whose links sit in stacked planes joined by vertical
    pins/bosses.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from agent.templates._modular import (
    InterfaceSpec,
    ModuleBuild,
    ModuleBuildContext,
    SlotSpec,
    assemble,
)
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeWithHolesGeometry,
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


BaseModule = Literal[
    "pedestal_column",
    "grounded_clevis_bracket",
    "wall_backplate",
    "broad_mounting_plate",
    "side_cheek_plate",
]
LinkModule = Literal[
    "solid_box_beam",
    "clevis_ear_bore",
    "windowed_open_frame",
    "dual_sideplate_ladder",
    "flat_extrude_capsule",
    "primitive_lug_barrel",
]
TerminalModule = Literal[
    "integral_end_tab",
    "separate_fixed_pad",
    "separate_fixed_clamp",
]
AxisFamily = Literal["vertical_pitch", "planar_yaw"]
DetailLevel = Literal["plain", "pins", "pins_bolts"]

ChainPaletteTheme = Literal[
    "satin_steel",
    "dark_powder",
    "anodized_blue",
    "bronze_bushed",
    "machine_gray",
]


# --------------------------------------------------------------------------- #
# Palette presets. Each theme provides body / dark / accent / pin / bolt /
# pad color tokens pulled by the module factories from the resolved palette.
# --------------------------------------------------------------------------- #


CHAIN_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "satin_steel": {
        "body": (0.62, 0.65, 0.68, 1.0),
        "dark": (0.20, 0.22, 0.25, 1.0),
        "accent": (0.74, 0.76, 0.79, 1.0),
        "pin": (0.80, 0.78, 0.72, 1.0),
        "bolt": (0.05, 0.05, 0.05, 1.0),
        "pad": (0.16, 0.17, 0.18, 1.0),
    },
    "dark_powder": {
        "body": (0.16, 0.17, 0.19, 1.0),
        "dark": (0.08, 0.08, 0.09, 1.0),
        "accent": (0.30, 0.31, 0.33, 1.0),
        "pin": (0.70, 0.71, 0.73, 1.0),
        "bolt": (0.02, 0.02, 0.02, 1.0),
        "pad": (0.04, 0.05, 0.05, 1.0),
    },
    "anodized_blue": {
        "body": (0.22, 0.34, 0.52, 1.0),
        "dark": (0.10, 0.15, 0.24, 1.0),
        "accent": (0.40, 0.54, 0.72, 1.0),
        "pin": (0.78, 0.80, 0.82, 1.0),
        "bolt": (0.04, 0.05, 0.07, 1.0),
        "pad": (0.10, 0.11, 0.13, 1.0),
    },
    "bronze_bushed": {
        "body": (0.54, 0.40, 0.24, 1.0),
        "dark": (0.26, 0.19, 0.12, 1.0),
        "accent": (0.72, 0.54, 0.30, 1.0),
        "pin": (0.82, 0.66, 0.38, 1.0),
        "bolt": (0.10, 0.07, 0.05, 1.0),
        "pad": (0.18, 0.14, 0.10, 1.0),
    },
    "machine_gray": {
        "body": (0.43, 0.45, 0.46, 1.0),
        "dark": (0.18, 0.19, 0.21, 1.0),
        "accent": (0.58, 0.60, 0.61, 1.0),
        "pin": (0.75, 0.76, 0.77, 1.0),
        "bolt": (0.06, 0.06, 0.07, 1.0),
        "pad": (0.12, 0.13, 0.14, 1.0),
    },
}


# Axis-family swing axes (both joints share the same tuple).
_AXIS_FOR_FAMILY: dict[str, tuple[float, float, float]] = {
    "vertical_pitch": (0.0, -1.0, 0.0),
    "planar_yaw": (0.0, 0.0, 1.0),
}


@dataclass(frozen=True)
class TwojointRevoluteChainConfig:
    """Public template config. Module selection is opt-in: leave any module
    field ``None`` to let ``config_from_seed`` / ``resolve_config`` fill it
    from the seed-driven RNG.
    """

    base_module: BaseModule | None = None
    link_module: LinkModule | None = None
    terminal_module: TerminalModule | None = None
    axis_family: AxisFamily | None = None
    detail_level: DetailLevel = "pins"
    palette_theme: ChainPaletteTheme = "satin_steel"

    # Chain geometry (distance(joint_1, joint_2) == link1_len; distance(
    # joint_2, end_datum) == link2_len).
    link1_len: float = 0.180
    link2_len: float = 0.140
    joint1_axis_z: float = 0.120
    link_width: float = 0.034
    link_height: float = 0.040
    taper_ratio: float = 0.82

    # Hinge sizing (hub straddles the clevis gap).
    hub_radius: float = 0.020
    lug_radius: float = 0.026
    lug_thickness: float = 0.010

    # Joint limits (rest pose 0 must be within range).
    joint_limit: float = 1.35

    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(CHAIN_PALETTE_PRESETS["satin_steel"])
    )


@dataclass(frozen=True)
class ResolvedTwojointRevoluteChainConfig:
    """Dimension-clamped + module-resolved config consumed by builders."""

    base_module: BaseModule
    link_module: LinkModule
    terminal_module: TerminalModule
    axis_family: AxisFamily
    detail_level: DetailLevel
    palette_theme: ChainPaletteTheme

    link1_len: float
    link2_len: float
    joint1_axis_z: float
    link_width: float
    link_height: float
    taper_ratio: float

    hub_radius: float
    lug_radius: float
    lug_thickness: float

    joint_limit: float

    palette: dict[str, tuple[float, float, float, float]]

    @property
    def axis(self) -> tuple[float, float, float]:
        return _AXIS_FOR_FAMILY[self.axis_family]


# --------------------------------------------------------------------------- #
# seed -> config
# --------------------------------------------------------------------------- #


_BASE_NAMES: tuple[BaseModule, ...] = (
    "pedestal_column",
    "grounded_clevis_bracket",
    "wall_backplate",
    "broad_mounting_plate",
    "side_cheek_plate",
)
_LINK_NAMES: tuple[LinkModule, ...] = (
    "solid_box_beam",
    "clevis_ear_bore",
    "windowed_open_frame",
    "dual_sideplate_ladder",
    "flat_extrude_capsule",
    "primitive_lug_barrel",
)
_TERMINAL_NAMES: tuple[TerminalModule, ...] = (
    "integral_end_tab",
    "separate_fixed_pad",
    "separate_fixed_clamp",
)
_AXIS_NAMES: tuple[AxisFamily, ...] = ("vertical_pitch", "planar_yaw")
_DETAIL_NAMES: tuple[DetailLevel, ...] = ("plain", "pins", "pins_bolts")


def config_from_seed(seed: int) -> TwojointRevoluteChainConfig:
    """Sample a chain configuration for the given seed.

    seed == 0 returns the anchor combination (pedestal_column +
    solid_box_beam + integral_end_tab + vertical_pitch) at canonical
    dimensions. Other seeds pick modules uniformly per slot and sample
    continuous dimensions across the spec ranges.
    """

    if seed == 0:
        return TwojointRevoluteChainConfig(
            base_module="pedestal_column",
            link_module="solid_box_beam",
            terminal_module="integral_end_tab",
            axis_family="vertical_pitch",
            detail_level="pins",
            palette_theme="satin_steel",
        )

    rng = random.Random(seed)
    base: BaseModule = rng.choice(_BASE_NAMES)
    link: LinkModule = rng.choice(_LINK_NAMES)
    terminal: TerminalModule = rng.choice(_TERMINAL_NAMES)
    axis_family: AxisFamily = rng.choice(_AXIS_NAMES)
    detail: DetailLevel = rng.choice(_DETAIL_NAMES)
    palette_theme: ChainPaletteTheme = rng.choice(tuple(CHAIN_PALETTE_PRESETS.keys()))

    return TwojointRevoluteChainConfig(
        base_module=base,
        link_module=link,
        terminal_module=terminal,
        axis_family=axis_family,
        detail_level=detail,
        palette_theme=palette_theme,
        link1_len=round(rng.uniform(0.11, 0.48), 4),
        link2_len=round(rng.uniform(0.09, 0.34), 4),
        joint1_axis_z=round(rng.uniform(0.08, 0.20), 4),
        link_width=round(rng.uniform(0.018, 0.060), 4),
        link_height=round(rng.uniform(0.026, 0.058), 4),
        taper_ratio=round(rng.uniform(0.70, 0.95), 4),
        hub_radius=round(rng.uniform(0.015, 0.026), 4),
        lug_radius=round(rng.uniform(0.022, 0.034), 4),
        joint_limit=round(rng.uniform(0.9, 1.7), 4),
    )


def resolve_config(
    config: TwojointRevoluteChainConfig,
) -> ResolvedTwojointRevoluteChainConfig:
    """Validate enums (raise ValueError), clamp floats, fill any None module
    fields with anchors."""

    base = config.base_module or "pedestal_column"
    link = config.link_module or "solid_box_beam"
    terminal = config.terminal_module or "integral_end_tab"
    axis_family = config.axis_family or "vertical_pitch"
    detail = config.detail_level or "pins"

    if base not in _BASE_NAMES:
        raise ValueError(f"Unsupported base_module: {base}")
    if link not in _LINK_NAMES:
        raise ValueError(f"Unsupported link_module: {link}")
    if terminal not in _TERMINAL_NAMES:
        raise ValueError(f"Unsupported terminal_module: {terminal}")
    if axis_family not in _AXIS_NAMES:
        raise ValueError(f"Unsupported axis_family: {axis_family}")
    if detail not in _DETAIL_NAMES:
        raise ValueError(f"Unsupported detail_level: {detail}")
    if str(config.palette_theme) not in CHAIN_PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    link1_len = max(0.11, min(float(config.link1_len), 0.48))
    link2_len = max(0.09, min(float(config.link2_len), 0.34))
    joint1_axis_z = max(0.08, min(float(config.joint1_axis_z), 0.20))
    link_width = max(0.018, min(float(config.link_width), 0.060))
    link_height = max(0.026, min(float(config.link_height), 0.058))
    taper_ratio = max(0.65, min(float(config.taper_ratio), 0.98))

    hub_radius = max(0.013, min(float(config.hub_radius), 0.028))
    lug_radius = max(hub_radius + 0.004, min(float(config.lug_radius), 0.036))
    lug_thickness = max(0.008, min(float(config.lug_thickness), 0.016))

    joint_limit = max(0.4, min(float(config.joint_limit), 0.70))

    palette = dict(CHAIN_PALETTE_PRESETS[config.palette_theme])

    return ResolvedTwojointRevoluteChainConfig(
        base_module=base,
        link_module=link,
        terminal_module=terminal,
        axis_family=axis_family,
        detail_level=detail,
        palette_theme=config.palette_theme,
        link1_len=link1_len,
        link2_len=link2_len,
        joint1_axis_z=joint1_axis_z,
        link_width=link_width,
        link_height=link_height,
        taper_ratio=taper_ratio,
        hub_radius=hub_radius,
        lug_radius=lug_radius,
        lug_thickness=lug_thickness,
        joint_limit=joint_limit,
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Shared hinge helpers.
#
# Every chain/internal pivot mates a parent "knuckle" (whose +z face is the
# mating face) to the child link's ``*_hub`` cylinder (centred on the child
# part-frame origin so (0,0,0) lies in its AABB and the -z face is the mating
# face). Two things are family-dependent:
#
#   - SHAPE. vertical_pitch (axis -y) uses a boxy clevis (top_lug + lower_lug):
#     the swing lifts the child off the parent, so square lugs never sweep into
#     a neighbour. planar_yaw (axis +z) rotates *about* the stack axis, so a
#     square lug's corners would sweep through the neighbour; the parent
#     knuckle is therefore a **coaxial cylinder boss** (rotation-invariant),
#     mirroring the 5-star planar sample's pin/boss construction.
#   - DECK HEIGHT. The child link body sits ``deck`` above the parent body. For
#     the inter-link joints this is sized to the two body half-thicknesses (+ a
#     small clearance) so consecutive links sit in tight parallel planes —
#     never coplanar (which interpenetrates) and never a clevis-height apart
#     (which reads as floating, especially for the thin flat-plate modules).
#     The base->link_1 joint keeps the legacy clevis height (link_1 rests on
#     the base, which fills the gap).
# --------------------------------------------------------------------------- #


def _is_yaw(r: ResolvedTwojointRevoluteChainConfig) -> bool:
    """planar_yaw rotates about +z, so joints must be coaxial (no swept corners)."""
    return r.axis_family == "planar_yaw"


def _half_gap(r: ResolvedTwojointRevoluteChainConfig) -> float:
    hub_len = 2.0 * r.hub_radius * 1.05
    return 0.5 * hub_len * 1.10


def _link_body_halfz(r: ResolvedTwojointRevoluteChainConfig, *, child: bool) -> float:
    """Half the z-thickness of a link body for the chosen link module. ``child``
    selects link_2 (tapered) vs link_1. Used to size the parallel-deck step so
    consecutive link bodies just clear each other."""
    if r.link_module == "flat_extrude_capsule":
        return 0.5 * max(0.006, r.link_height * 0.30)
    base_h = r.link_height * 0.55 if r.link_module == "clevis_ear_bore" else r.link_height
    return 0.5 * base_h * (r.taper_ratio if child else 1.0)


_DECK_CLEARANCE = 0.006


def _joint2_deck(r: ResolvedTwojointRevoluteChainConfig) -> float:
    """Vertical step from the link_1 body plane up to the link_2 body plane."""
    return _link_body_halfz(r, child=False) + _link_body_halfz(r, child=True) + _DECK_CLEARANCE


def _joint3_deck(r: ResolvedTwojointRevoluteChainConfig) -> float:
    """Vertical step from the link_2 body plane up to the terminal body plane."""
    return _link_body_halfz(r, child=True) + 0.5 * r.link_height * 0.55 + _DECK_CLEARANCE


def _emit_parent_clevis(
    part,
    *,
    r: ResolvedTwojointRevoluteChainConfig,
    pivot_x: float,
    pivot_z: float,
    half_gap: float,
    top_name: str,
    bottom_name: str,
    material: str,
    deck: float | None = None,
) -> float:
    """Emit the parent-side knuckle centred on ``(pivot_x, 0, pivot_z)`` and
    return the world-local z of its **+z mating face**.

    ``deck`` is how far above ``pivot_z`` the mating face sits; ``None`` keeps
    the legacy clevis height (``half_gap + lug_t``, used by the base->link_1
    joint). For planar_yaw the knuckle is a coaxial cylinder boss
    (rotation-invariant); for vertical_pitch it is a boxy top_lug + lower_lug
    pair.
    """
    lug_t = r.lug_thickness
    lug_r = r.lug_radius

    if _is_yaw(r):
        # planar_yaw: a coaxial cylinder boss from just below the body plane up
        # to the mating face, plus a coaxial pin-head collar beneath — nothing
        # off-axis to sweep when the child rotates about this +z pin. ``deck``
        # sizes the parallel-plane step (small for inter-link joints; the base
        # passes None and keeps the legacy clevis height).
        lift = (half_gap + lug_t) if deck is None else deck
        top_face_z = pivot_z + lift
        boss_bottom = pivot_z - lug_t
        part.visual(
            Cylinder(radius=lug_r, length=top_face_z - boss_bottom),
            origin=Origin(xyz=(pivot_x, 0.0, 0.5 * (boss_bottom + top_face_z))),
            material=material,
            name=top_name, material_class_id="metal.paint_coated",
        )
        part.visual(
            Cylinder(radius=lug_r * 0.92, length=lug_t),
            origin=Origin(xyz=(pivot_x, 0.0, boss_bottom - 0.5 * lug_t)),
            material=material,
            name=bottom_name, material_class_id="metal.paint_coated",
        )
        return top_face_z

    # vertical_pitch: boxy clevis straddling the pivot. The pitch swing (axis
    # -y) lifts the child clear, so a clevis-height layered spacing is correct
    # here — ``deck`` is intentionally not applied; only planar_yaw needs the
    # compact parallel-plane spacing.
    top_face_z = pivot_z + half_gap + lug_t
    part.visual(
        Box((2.0 * lug_r, 2.0 * lug_r, lug_t)),
        origin=Origin(xyz=(pivot_x, 0.0, pivot_z + half_gap + 0.5 * lug_t)),
        material=material,
        name=top_name, material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((2.0 * lug_r, 2.0 * lug_r, lug_t)),
        origin=Origin(xyz=(pivot_x, 0.0, pivot_z - half_gap - 0.5 * lug_t)),
        material=material,
        name=bottom_name, material_class_id="metal.paint_coated",
    )
    return top_face_z


def _emit_child_hub(
    part,
    *,
    r: ResolvedTwojointRevoluteChainConfig,
    hub_name: str,
    material: str,
) -> None:
    """Emit the child link's proximal hub at the part-frame origin.

    The hub is a short cylinder spanning z = 0 .. +hub_len so its **-z face**
    is exactly at the joint origin (z=0). That makes the mating-face gap
    against the parent's +z mating face zero, and (0,0,0) lies on the hub AABB
    (satisfying articulation_origin_far_from_geometry). The hub rises as a
    coaxial boss above the parent knuckle — a captured-pin overlap declared in
    tests.
    """
    hub_r = r.hub_radius
    hub_len = 2.0 * hub_r * 1.05
    part.visual(
        Cylinder(radius=hub_r, length=hub_len),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * hub_len)),
        material=material,
        name=hub_name, material_class_id="metal.paint_coated",
    )


def _emit_distal_riser(
    part,
    *,
    r: ResolvedTwojointRevoluteChainConfig,
    pivot_x: float,
    width: float,
    deck: float,
    material: str,
    name: str,
) -> None:
    """Bridge a link body (plane z=0) across its distal clevis gap so the lugs
    are connected (not floating islands).

    vertical_pitch straddles the pivot, so the riser spans the full gap
    (±(half_gap + lug_t)). planar_yaw's coaxial boss already spans the body
    plane, so no riser is emitted (a boxy riser would stick up off-axis and
    sweep when the link rotates). ``deck`` is accepted for call-site symmetry
    but only planar_yaw uses a deck (and emits no riser).
    """
    if _is_yaw(r):
        return
    del deck
    riser_h = 2.0 * (_half_gap(r) + r.lug_thickness)
    part.visual(
        Box((0.028, width, riser_h)),
        origin=Origin(xyz=(pivot_x, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _maybe_pin_detail(
    part,
    *,
    r: ResolvedTwojointRevoluteChainConfig,
    pivot_x: float,
    pivot_z: float,
    half_gap: float,
    name_prefix: str,
) -> None:
    """Optional pin-cap detail above the top lug (Slot detail_level)."""
    if r.detail_level == "plain":
        return
    cap_z = pivot_z + half_gap + r.lug_thickness + 0.002
    part.visual(
        Cylinder(radius=r.hub_radius * 0.8, length=0.004),
        origin=Origin(xyz=(pivot_x, 0.0, cap_z)),
        material="pin",
        name=f"{name_prefix}_pin_cap", material_class_id="metal.stainless_matte",
    )


# --------------------------------------------------------------------------- #
# Slot A — base / root support module factories.
#
# Each base exposes a downstream interface whose ``*_top_lug`` (+z) face
# sits at the joint_1 pivot. For ``vertical_pitch`` the pivot is lifted to
# z = joint1_axis_z; for ``planar_yaw`` the pivot sits at a low z so the
# chain lies flat. The base's body actually grounds / backs the pivot.
# --------------------------------------------------------------------------- #


def _pivot_z_for(r: ResolvedTwojointRevoluteChainConfig) -> float:
    """The joint_1 pivot z (in base frame). Lifted for pitch, low for yaw."""
    if r.axis_family == "vertical_pitch":
        return r.joint1_axis_z
    return 0.026 + _half_gap(r) + r.lug_thickness


def _downstream_iface(
    part_name: str,
    top_lug_name: str,
    pivot_x: float,
    pivot_z: float,
    top_face_z: float,
    r: ResolvedTwojointRevoluteChainConfig,
) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name=part_name,
        visual_name=top_lug_name,
        face_side="positive_z",
        anchor_local=(pivot_x, 0.0, top_face_z),
        face_extents_uv=(2.0 * r.lug_radius, 2.0 * r.lug_radius),
        extents_tol=0.60,
        contact_tol=0.0030,
    )


def _build_pedestal_column_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Anchor base — foot plate + vertical column + top ear/clevis.

    Adapted from rec_..._785b L72-L87 (``_pedestal_shape``): a wide foot box,
    a tall narrow column, and a pair of top ears at the first joint axis.
    Implemented with primitive Box/Cylinder; the clevis lugs replace the
    cadquery ears so the MatingContract fits.
    """
    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]

    base = model.part("base")
    pivot_z = _pivot_z_for(r)
    half_gap = _half_gap(r)

    foot_h = 0.018
    base.visual(
        Box((0.090, 0.072, foot_h)),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * foot_h)),
        material="dark",
        name="foot_plate", material_class_id="metal.paint_coated",
    )
    # Column rises from the foot up to just below the pivot.
    col_top = pivot_z - half_gap - r.lug_thickness
    col_top = max(col_top, foot_h + 0.010)
    col_h = col_top - foot_h
    base.visual(
        Box((0.034, 0.030, col_h)),
        origin=Origin(xyz=(0.0, 0.0, foot_h + 0.5 * col_h)),
        material="body",
        name="column", material_class_id="metal.paint_coated",
    )
    # Riser web bridges the column top up through the clevis gap so the
    # lower lug connects back to the column (no island).
    riser_bottom = col_top - 0.002
    riser_top = pivot_z + half_gap + r.lug_thickness
    riser_h = riser_top - riser_bottom
    base.visual(
        Box((0.030, 0.026, riser_h)),
        origin=Origin(xyz=(0.0, 0.0, riser_bottom + 0.5 * riser_h)),
        material="body",
        name="pivot_riser", material_class_id="metal.paint_coated",
    )
    top_face_z = _emit_parent_clevis(
        base,
        r=r,
        pivot_x=0.0,
        pivot_z=pivot_z,
        half_gap=half_gap,
        top_name="joint1_top_lug",
        bottom_name="joint1_lower_lug",
        material="dark",
    )
    _maybe_pin_detail(
        base, r=r, pivot_x=0.0, pivot_z=pivot_z, half_gap=half_gap, name_prefix="joint1"
    )

    base.inertial = Inertial.from_geometry(
        Box((0.090, 0.072, pivot_z + half_gap)),
        mass=2.6,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (pivot_z + half_gap))),
    )

    return ModuleBuild(
        module_name="pedestal_column",
        parts_emitted=["base"],
        internal_articulations=[],
        interfaces={
            "downstream": _downstream_iface("base", "joint1_top_lug", 0.0, pivot_z, top_face_z, r)
        },
    )


def _build_grounded_clevis_bracket_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt base — base plate + rear web + dual-ear clevis.

    Adapted from rec_..._9bd9 L92-L139 (``_make_root_bracket_shape``): a wide
    base plate, a tall rear web, a crown / pivot bar, and dual side ears.
    Primitive Box geometry; the clevis lugs carry the pivot.
    """
    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]

    base = model.part("base")
    pivot_z = _pivot_z_for(r)
    half_gap = _half_gap(r)

    plate_h = 0.014
    base.visual(
        Box((0.110, 0.130, plate_h)),
        origin=Origin(xyz=(-0.020, 0.0, 0.5 * plate_h)),
        material="dark",
        name="base_plate", material_class_id="metal.paint_coated",
    )
    # Rear web rises behind the pivot.
    web_top = pivot_z + half_gap + r.lug_thickness
    web_h = web_top - plate_h
    base.visual(
        Box((0.032, 0.110, web_h)),
        origin=Origin(xyz=(-0.044, 0.0, plate_h + 0.5 * web_h)),
        material="body",
        name="rear_web", material_class_id="metal.paint_coated",
    )
    # Pivot bar / shoulder pad reaches forward to the pivot column.
    bar_bottom = pivot_z - half_gap - r.lug_thickness
    bar_bottom = max(bar_bottom, plate_h + 0.004)
    bar_h = web_top - bar_bottom
    base.visual(
        Box((0.052, 0.070, bar_h)),
        origin=Origin(xyz=(-0.018, 0.0, bar_bottom + 0.5 * bar_h)),
        material="body",
        name="pivot_bar", material_class_id="metal.paint_coated",
    )
    top_face_z = _emit_parent_clevis(
        base,
        r=r,
        pivot_x=0.0,
        pivot_z=pivot_z,
        half_gap=half_gap,
        top_name="joint1_top_lug",
        bottom_name="joint1_lower_lug",
        material="dark",
    )
    _maybe_pin_detail(
        base, r=r, pivot_x=0.0, pivot_z=pivot_z, half_gap=half_gap, name_prefix="joint1"
    )

    base.inertial = Inertial.from_geometry(
        Box((0.130, 0.130, web_top)),
        mass=2.4,
        origin=Origin(xyz=(-0.020, 0.0, 0.5 * web_top)),
    )

    return ModuleBuild(
        module_name="grounded_clevis_bracket",
        parts_emitted=["base"],
        internal_articulations=[],
        interfaces={
            "downstream": _downstream_iface("base", "joint1_top_lug", 0.0, pivot_z, top_face_z, r)
        },
    )


def _build_wall_backplate_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt base — vertical wall plate + forward root_mount lug + lag bolts.

    Adapted from rec_..._98f91b L31-L53: a tall thin backplate sitting in the
    Y-Z plane (against the wall at -x), a boxy welded root_mount reaching
    forward, and four visible lag-bolt heads. Primitive Box/Cylinder.
    """
    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]

    base = model.part("base")
    pivot_z = _pivot_z_for(r)
    half_gap = _half_gap(r)

    plate_t = 0.026
    plate_h = pivot_z + half_gap + r.lug_thickness + 0.080
    plate_w = 0.180
    # Backplate is set well behind the pivot plane so the pitching link never
    # sweeps into it; the root_mount below is lengthened to bridge the gap.
    base.visual(
        Box((plate_t, plate_w, plate_h)),
        origin=Origin(xyz=(-plate_t * 0.5 - 0.075, 0.0, 0.5 * plate_h)),
        material="dark",
        name="wall_backplate", material_class_id="metal.paint_coated",
    )
    # Forward root_mount lug reaching to the pivot column.
    mount_bottom = pivot_z - half_gap - r.lug_thickness
    mount_bottom = max(mount_bottom, 0.004)
    mount_h = pivot_z + half_gap + r.lug_thickness - mount_bottom
    base.visual(
        Box((0.115, 0.090, mount_h)),
        origin=Origin(xyz=(-0.0375, 0.0, mount_bottom + 0.5 * mount_h)),
        material="body",
        name="root_mount", material_class_id="metal.paint_coated",
    )
    # Four lag-bolt heads on the backplate face.
    if r.detail_level == "pins_bolts":
        for i, (yy, zz) in enumerate(
            (
                (-0.060, plate_h * 0.30),
                (0.060, plate_h * 0.30),
                (-0.060, plate_h * 0.70),
                (0.060, plate_h * 0.70),
            )
        ):
            base.visual(
                Cylinder(radius=0.012, length=0.012),
                origin=Origin(xyz=(-0.075 - plate_t * 0.5, yy, zz), rpy=(0.0, math.pi / 2.0, 0.0)),
                material="bolt",
                name=f"wall_bolt_{i}", material_class_id="metal.blackened_gunmetal",
            )
    top_face_z = _emit_parent_clevis(
        base,
        r=r,
        pivot_x=0.0,
        pivot_z=pivot_z,
        half_gap=half_gap,
        top_name="joint1_top_lug",
        bottom_name="joint1_lower_lug",
        material="accent",
    )
    _maybe_pin_detail(
        base, r=r, pivot_x=0.0, pivot_z=pivot_z, half_gap=half_gap, name_prefix="joint1"
    )

    base.inertial = Inertial.from_geometry(
        Box((0.080, plate_w, plate_h)),
        mass=3.0,
        origin=Origin(xyz=(-0.030, 0.0, 0.5 * plate_h)),
    )

    return ModuleBuild(
        module_name="wall_backplate",
        parts_emitted=["base"],
        internal_articulations=[],
        interfaces={
            "downstream": _downstream_iface("base", "joint1_top_lug", 0.0, pivot_z, top_face_z, r)
        },
    )


def _build_broad_mounting_plate_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt base — wide low-profile mounting plate + four countersunk screws.

    Adapted from rec_..._4fc35 L74-L93: a rounded-rect ExtrudeWithHoles plate
    with four screw heads, sitting flat with a low knuckle/pin stack at the
    first joint. Preserves the ExtrudeWithHoles + Cylinder primitives.
    """
    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]

    base = model.part("base")
    pivot_z = _pivot_z_for(r)
    half_gap = _half_gap(r)

    plate_t = 0.012
    plate = _rounded_rect_profile(0.180, 0.130, 0.016)
    screw_centers = [(-0.060, -0.044), (-0.060, 0.044), (0.052, -0.044), (0.052, 0.044)]
    holes = [_circle_profile(0.0075, center=c) for c in screw_centers]
    base.visual(
        mesh_from_geometry(
            ExtrudeWithHolesGeometry(plate, holes, plate_t),
            "broad_plate_shell",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * plate_t)),
        material="dark",
        name="plate_shell", material_class_id="metal.paint_coated",
    )
    for i, (x, y) in enumerate(screw_centers):
        base.visual(
            Cylinder(radius=0.011, length=0.003),
            origin=Origin(xyz=(x, y, plate_t)),
            material="bolt",
            name=f"screw_head_{i}", material_class_id="metal.blackened_gunmetal",
        )
    # Pivot post rising from the plate up to the clevis.
    post_bottom = plate_t - 0.001
    post_top = pivot_z + half_gap + r.lug_thickness
    post_h = post_top - post_bottom
    base.visual(
        Box((0.046, 0.044, post_h)),
        origin=Origin(xyz=(0.0, 0.0, post_bottom + 0.5 * post_h)),
        material="body",
        name="pivot_post", material_class_id="metal.paint_coated",
    )
    top_face_z = _emit_parent_clevis(
        base,
        r=r,
        pivot_x=0.0,
        pivot_z=pivot_z,
        half_gap=half_gap,
        top_name="joint1_top_lug",
        bottom_name="joint1_lower_lug",
        material="accent",
    )
    _maybe_pin_detail(
        base, r=r, pivot_x=0.0, pivot_z=pivot_z, half_gap=half_gap, name_prefix="joint1"
    )

    base.inertial = Inertial.from_geometry(
        Box((0.180, 0.130, post_top)),
        mass=2.8,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * post_top)),
    )

    return ModuleBuild(
        module_name="broad_mounting_plate",
        parts_emitted=["base"],
        internal_articulations=[],
        interfaces={
            "downstream": _downstream_iface("base", "joint1_top_lug", 0.0, pivot_z, top_face_z, r)
        },
    )


def _build_side_cheek_plate_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt base — single D-nosed side cheek + boss, planar side-mount.

    Adapted from rec_..._140c L99-L133 (``fixed_cheek``): a flat D-shaped
    cheek plate with a central boss and mount bolts, sitting upright with the
    pivot at its rounded nose. ExtrudeWithHoles cheek profile + clevis lug.
    """
    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]

    base = model.part("base")
    pivot_z = _pivot_z_for(r)
    half_gap = _half_gap(r)

    # D-nosed cheek standing in the X-Z plane (thin in Y): rounded nose at the
    # pivot, flat rear edge dropping to the ground.
    radius = max(0.034, half_gap + r.lug_thickness + 0.014)
    rear_z = -(pivot_z - 0.006)
    cheek = _cheek_profile(radius=radius, rear_extent=rear_z)
    cheek_holes = [_circle_profile(0.006, center=(0.0, rear_z + 0.018))]
    cheek_t = 0.008
    base.visual(
        mesh_from_geometry(
            ExtrudeWithHolesGeometry(cheek, cheek_holes, cheek_t),
            "side_cheek_plate",
        ),
        # The profile is in X-Z; extrude along Y. Rotate so the extrusion
        # thickness lies in Y and lift to the pivot height.
        origin=Origin(xyz=(0.0, -0.5 * cheek_t, pivot_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark",
        name="cheek_plate", material_class_id="metal.paint_coated",
    )
    # Foot pad grounding the rear edge.
    base.visual(
        Box((2.0 * radius, 0.060, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        material="body",
        name="cheek_foot", material_class_id="metal.paint_coated",
    )
    # Riser linking the foot up to the clevis gap.
    riser_top = pivot_z + half_gap + r.lug_thickness
    riser_h = riser_top - 0.010
    base.visual(
        Box((0.030, 0.040, riser_h)),
        origin=Origin(xyz=(0.0, 0.0, 0.010 + 0.5 * riser_h)),
        material="body",
        name="cheek_riser", material_class_id="metal.paint_coated",
    )
    top_face_z = _emit_parent_clevis(
        base,
        r=r,
        pivot_x=0.0,
        pivot_z=pivot_z,
        half_gap=half_gap,
        top_name="joint1_top_lug",
        bottom_name="joint1_lower_lug",
        material="accent",
    )
    _maybe_pin_detail(
        base, r=r, pivot_x=0.0, pivot_z=pivot_z, half_gap=half_gap, name_prefix="joint1"
    )

    base.inertial = Inertial.from_geometry(
        Box((2.0 * radius, 0.060, riser_top)),
        mass=2.0,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * riser_top)),
    )

    return ModuleBuild(
        module_name="side_cheek_plate",
        parts_emitted=["base"],
        internal_articulations=[],
        interfaces={
            "downstream": _downstream_iface("base", "joint1_top_lug", 0.0, pivot_z, top_face_z, r)
        },
    )


# --------------------------------------------------------------------------- #
# Profile helpers (flat / cheek constructions).
# --------------------------------------------------------------------------- #


def _circle_profile(
    radius: float, *, center: tuple[float, float] = (0.0, 0.0), segments: int = 32
) -> list[tuple[float, float]]:
    cx, cy = center
    return [
        (
            cx + radius * math.cos(2.0 * math.pi * i / segments),
            cy + radius * math.sin(2.0 * math.pi * i / segments),
        )
        for i in range(segments)
    ]


def _rounded_rect_profile(
    width: float, depth: float, radius: float, *, corner_segments: int = 6
) -> list[tuple[float, float]]:
    hw = width * 0.5
    hd = depth * 0.5
    rr = min(radius, hw * 0.9, hd * 0.9)
    pts: list[tuple[float, float]] = []
    corners = [
        (hw - rr, hd - rr, 0.0),
        (-hw + rr, hd - rr, math.pi * 0.5),
        (-hw + rr, -hd + rr, math.pi),
        (hw - rr, -hd + rr, math.pi * 1.5),
    ]
    for cx, cy, a0 in corners:
        for i in range(corner_segments + 1):
            a = a0 + (math.pi * 0.5) * i / corner_segments
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def _capsule_profile(
    length: float, radius: float, *, arc_segments: int = 16
) -> list[tuple[float, float]]:
    """Flat-sided link outline with circular pin ends (rec_..._140c)."""
    points: list[tuple[float, float]] = []
    for i in range(arc_segments + 1):
        angle = -math.pi / 2.0 + math.pi * i / arc_segments
        points.append((length + radius * math.cos(angle), radius * math.sin(angle)))
    for i in range(arc_segments + 1):
        angle = math.pi / 2.0 + math.pi * i / arc_segments
        points.append((radius * math.cos(angle), radius * math.sin(angle)))
    return points


def _tapered_tab_profile(
    length: float, root_radius: float, tab_radius: float, *, arc_segments: int = 16
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for i in range(arc_segments + 1):
        angle = -math.pi / 2.0 + math.pi * i / arc_segments
        points.append((length + tab_radius * math.cos(angle), tab_radius * math.sin(angle)))
    for i in range(arc_segments + 1):
        angle = math.pi / 2.0 + math.pi * i / arc_segments
        points.append((root_radius * math.cos(angle), root_radius * math.sin(angle)))
    return points


def _cheek_profile(*, radius: float, rear_extent: float) -> list[tuple[float, float]]:
    """D-nosed cheek: rounded pin nose at origin, flat rear edge at z=rear_extent.

    Profile in (x, z) — the nose arc is centred on the origin; the rear edge
    is a straight line at z = rear_extent (negative). Adapted from
    rec_..._140c ``_cheek_profile``.
    """
    points: list[tuple[float, float]] = []
    for i in range(19):
        angle = math.pi * i / 18  # 0 .. pi (upper half arc)
        points.append((radius * math.cos(angle), radius * math.sin(angle)))
    points.append((-radius, rear_extent))
    points.append((radius, rear_extent))
    return points


# --------------------------------------------------------------------------- #
# Slot B — links construction module factories.
#
# Each emits BOTH link_1 and link_2 + the internal REVOLUTE joint_2, sharing
# the SAME construction. Layout (in each link's local frame): the proximal
# hub sits at the origin, the body runs along +x, and the distal clevis sits
# at x = link_len. link_1 exposes upstream (joint_1) + emits joint_2 with a
# MatingContract; link_2 exposes downstream only when the terminal is
# separate. For integral terminals link_2 fuses the end tab in.
# --------------------------------------------------------------------------- #


def _link_upstream_iface(
    part_name: str, hub_name: str, r: ResolvedTwojointRevoluteChainConfig
) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="upstream",
        part_name=part_name,
        visual_name=hub_name,
        face_side="negative_z",
        anchor_local=(0.0, 0.0, 0.0),
        face_extents_uv=(2.0 * r.hub_radius, 2.0 * r.hub_radius),
        extents_tol=0.60,
        contact_tol=0.0030,
        consumer_joint_type=ArticulationType.REVOLUTE,
        consumer_joint_axis=r.axis,
        consumer_motion_limits=MotionLimits(
            effort=24.0, velocity=1.6, lower=-r.joint_limit, upper=r.joint_limit
        ),
    )


def _link_downstream_iface(
    part_name: str,
    top_lug_name: str,
    pivot_x: float,
    top_face_z: float,
    r: ResolvedTwojointRevoluteChainConfig,
) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name=part_name,
        visual_name=top_lug_name,
        face_side="positive_z",
        anchor_local=(pivot_x, 0.0, top_face_z),
        face_extents_uv=(2.0 * r.lug_radius, 2.0 * r.lug_radius),
        extents_tol=0.60,
        contact_tol=0.0030,
    )


def _emit_joint2_and_interfaces(
    ctx: ModuleBuildContext,
    *,
    r: ResolvedTwojointRevoluteChainConfig,
    link1,
    link2,
    link1_top_face_z: float,
) -> dict[str, InterfaceSpec]:
    """Emit the shared joint_2 (link_1 -> link_2 REVOLUTE) with a
    MatingContract, plus the upstream interface dict.

    The link factory adds the ``downstream`` entry (link_2's distal clevis)
    itself when the terminal is separate; for integral terminals there is no
    downstream entry and the terminal module exposes no upstream interface,
    so the assembler emits no extra joint.
    """
    model = ctx.model

    model.articulation(
        "joint_2",
        ArticulationType.REVOLUTE,
        parent=link1,
        child=link2,
        origin=Origin(xyz=(r.link1_len, 0.0, link1_top_face_z)),
        axis=r.axis,
        motion_limits=MotionLimits(
            effort=18.0, velocity=1.8, lower=-r.joint_limit, upper=r.joint_limit
        ),
        mating=MatingContract(
            parent_face_geometry="link1_distal_top_lug",
            parent_face_side="positive_z",
            child_face_geometry="link2_hub",
            child_face_side="negative_z",
            contact_tol=0.0030,
        ),
    )

    return {"upstream": _link_upstream_iface("link_1", "link1_hub", r)}


def _emit_link2_distal_clevis(
    link2, *, r: ResolvedTwojointRevoluteChainConfig, material: str
) -> InterfaceSpec | None:
    """For separate terminals, emit a distal clevis on link_2 at x=link2_len
    and return its downstream interface. For integral terminals return None."""
    if r.terminal_module == "integral_end_tab":
        return None
    half_gap = _half_gap(r)
    _emit_distal_riser(
        link2,
        r=r,
        pivot_x=r.link2_len,
        width=max(0.018, r.link_width * r.taper_ratio * 0.85),
        deck=_joint3_deck(r),
        material="body",
        name="link2_distal_riser",
    )
    top_face_z = _emit_parent_clevis(
        link2,
        r=r,
        pivot_x=r.link2_len,
        pivot_z=0.0,
        half_gap=half_gap,
        top_name="link2_distal_top_lug",
        bottom_name="link2_distal_lower_lug",
        material=material,
        deck=_joint3_deck(r),
    )
    return _link_downstream_iface("link_2", "link2_distal_top_lug", r.link2_len, top_face_z, r)


def _emit_integral_end_tab(link2, *, r: ResolvedTwojointRevoluteChainConfig, material: str) -> None:
    """Fuse a compact end tab into link_2 (integral terminal).

    Adapted from rec_..._140c L128-L152 / rec_..._0004 tip_pad: a small pad at
    the link_2 tip, fused as a named visual on the same part (Rule 1)."""
    if r.terminal_module != "integral_end_tab":
        return
    tab_len = max(0.020, r.link2_len * 0.18)
    tab_h = r.link_height * r.taper_ratio * 0.9
    tab_w = r.link_width * r.taper_ratio
    base_w2 = r.link_width * r.taper_ratio
    base_h2 = r.link_height * r.taper_ratio
    # Tab body extending past the link tip; overlaps the link body so it is
    # one connected island.
    link2.visual(
        Box((tab_len, tab_w, tab_h)),
        origin=Origin(xyz=(r.link2_len - 0.002 + 0.5 * tab_len, 0.0, 0.0)),
        material=material,
        name="integral_end_tab", material_class_id="metal.paint_coated",
    )
    # Small rounded nose pad.
    link2.visual(
        Cylinder(
            radius=tab_h * 0.5,
            length=tab_w,
        ),
        origin=Origin(xyz=(r.link2_len - 0.002 + tab_len, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="pad",
        name="integral_end_nose", material_class_id="rubber.smooth_plain",
    )
    _ = (base_w2, base_h2)


# ---- solid_box_beam ---- #


def _build_solid_box_beam_links(ctx: ModuleBuildContext) -> ModuleBuild:
    """Anchor links — solid box beam + end hub blocks (rec_..._0001 L41-L52).

    upper_arm / forearm of the simple_robot_arm: a shoulder block, a box
    beam, an elbow block. Primitive Box geometry, parameterized lengths.
    """
    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]
    half_gap = _half_gap(r)

    # ---- link_1 ----
    link1 = model.part("link_1")
    _emit_child_hub(link1, r=r, hub_name="link1_hub", material="accent")
    beam_w, beam_h = r.link_width, r.link_height
    # Beam runs from inside the hub out to the distal clevis.
    beam_start = -r.hub_radius * 0.4
    beam_end = r.link1_len - 0.004
    beam_len = max(0.040, beam_end - beam_start)
    beam_cx = 0.5 * (beam_start + beam_end)
    link1.visual(
        Box((beam_len, beam_w, beam_h)),
        origin=Origin(xyz=(beam_cx, 0.0, 0.0)),
        material="body",
        name="link1_beam", material_class_id="metal.paint_coated",
    )
    # Riser bridging the beam down into the distal clevis gap.
    _emit_distal_riser(
        link1,
        r=r,
        pivot_x=r.link1_len - 0.004,
        width=beam_w * 0.8,
        deck=_joint2_deck(r),
        material="body",
        name="link1_distal_riser",
    )
    l1_top_face = _emit_parent_clevis(
        link1,
        r=r,
        pivot_x=r.link1_len,
        pivot_z=0.0,
        half_gap=half_gap,
        top_name="link1_distal_top_lug",
        bottom_name="link1_distal_lower_lug",
        material="dark",
        deck=_joint2_deck(r),
    )
    link1.inertial = Inertial.from_geometry(
        Box((r.link1_len + 0.04, beam_w * 1.4, max(beam_h, 2 * half_gap))),
        mass=0.7,
        origin=Origin(xyz=(0.5 * r.link1_len, 0.0, 0.0)),
    )

    # ---- link_2 ----
    link2 = model.part("link_2")
    _emit_child_hub(link2, r=r, hub_name="link2_hub", material="accent")
    beam2_w = r.link_width * r.taper_ratio
    beam2_h = r.link_height * r.taper_ratio
    beam2_start = -r.hub_radius * 0.4
    beam2_end = r.link2_len - 0.002
    beam2_len = max(0.030, beam2_end - beam2_start)
    beam2_cx = 0.5 * (beam2_start + beam2_end)
    link2.visual(
        Box((beam2_len, beam2_w, beam2_h)),
        origin=Origin(xyz=(beam2_cx, 0.0, 0.0)),
        material="body",
        name="link2_beam", material_class_id="metal.paint_coated",
    )
    _emit_integral_end_tab(link2, r=r, material="body")
    link2_downstream = _emit_link2_distal_clevis(link2, r=r, material="dark")
    link2.inertial = Inertial.from_geometry(
        Box((r.link2_len + 0.04, beam2_w * 1.4, max(beam2_h, 2 * half_gap))),
        mass=0.4,
        origin=Origin(xyz=(0.5 * r.link2_len, 0.0, 0.0)),
    )

    interfaces = _emit_joint2_and_interfaces(
        ctx, r=r, link1=link1, link2=link2, link1_top_face_z=l1_top_face
    )
    if link2_downstream is not None:
        interfaces["downstream"] = link2_downstream
    return ModuleBuild(
        module_name="solid_box_beam",
        parts_emitted=["link_1", "link_2"],
        internal_articulations=["joint_2"],
        interfaces=interfaces,
    )


# ---- primitive_lug_barrel ---- #


def _build_primitive_lug_barrel_links(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt links — primitive Box lug + Cylinder barrel/boss hinge block.

    Adapted from rec_..._0004 L84-L152: arm_bar Box + cylinder bosses at each
    hinge. Primitive Box/Cylinder; bosses ring the hubs/clevis."""
    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]
    half_gap = _half_gap(r)

    link1 = model.part("link_1")
    _emit_child_hub(link1, r=r, hub_name="link1_hub", material="accent")
    bar_w = r.link_width * 0.8
    bar_h = r.link_height
    bar_start = -r.hub_radius * 0.4
    bar_end = r.link1_len - 0.004
    bar_len = max(0.040, bar_end - bar_start)
    bar_cx = 0.5 * (bar_start + bar_end)
    link1.visual(
        Box((bar_len, bar_w, bar_h)),
        origin=Origin(xyz=(bar_cx, 0.0, 0.0)),
        material="body",
        name="link1_bar", material_class_id="metal.paint_coated",
    )
    # Cylindrical barrel boss around the proximal hub (axis along z).
    link1.visual(
        Cylinder(radius=r.hub_radius * 1.5, length=r.link_width * 0.5),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="body",
        name="link1_prox_barrel", material_class_id="metal.paint_coated",
    )
    _emit_distal_riser(
        link1,
        r=r,
        pivot_x=r.link1_len - 0.004,
        width=bar_w * 0.9,
        deck=_joint2_deck(r),
        material="body",
        name="link1_distal_riser",
    )
    l1_top_face = _emit_parent_clevis(
        link1,
        r=r,
        pivot_x=r.link1_len,
        pivot_z=0.0,
        half_gap=half_gap,
        top_name="link1_distal_top_lug",
        bottom_name="link1_distal_lower_lug",
        material="dark",
        deck=_joint2_deck(r),
    )
    link1.inertial = Inertial.from_geometry(
        Box((r.link1_len + 0.04, bar_w * 1.6, max(bar_h, 2 * half_gap))),
        mass=0.65,
        origin=Origin(xyz=(0.5 * r.link1_len, 0.0, 0.0)),
    )

    link2 = model.part("link_2")
    _emit_child_hub(link2, r=r, hub_name="link2_hub", material="accent")
    bar2_w = r.link_width * 0.8 * r.taper_ratio
    bar2_h = r.link_height * r.taper_ratio
    bar2_start = -r.hub_radius * 0.4
    bar2_end = r.link2_len - 0.002
    bar2_len = max(0.030, bar2_end - bar2_start)
    bar2_cx = 0.5 * (bar2_start + bar2_end)
    link2.visual(
        Box((bar2_len, bar2_w, bar2_h)),
        origin=Origin(xyz=(bar2_cx, 0.0, 0.0)),
        material="body",
        name="link2_bar", material_class_id="metal.paint_coated",
    )
    link2.visual(
        Cylinder(radius=r.hub_radius * 1.4, length=r.link_width * 0.45),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="body",
        name="link2_prox_barrel", material_class_id="metal.paint_coated",
    )
    _emit_integral_end_tab(link2, r=r, material="body")
    link2_downstream = _emit_link2_distal_clevis(link2, r=r, material="dark")
    link2.inertial = Inertial.from_geometry(
        Box((r.link2_len + 0.04, bar2_w * 1.6, max(bar2_h, 2 * half_gap))),
        mass=0.36,
        origin=Origin(xyz=(0.5 * r.link2_len, 0.0, 0.0)),
    )

    interfaces = _emit_joint2_and_interfaces(
        ctx, r=r, link1=link1, link2=link2, link1_top_face_z=l1_top_face
    )
    if link2_downstream is not None:
        interfaces["downstream"] = link2_downstream
    return ModuleBuild(
        module_name="primitive_lug_barrel",
        parts_emitted=["link_1", "link_2"],
        internal_articulations=["joint_2"],
        interfaces=interfaces,
    )


# ---- flat_extrude_capsule ---- #


def _build_flat_extrude_capsule_links(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt links — ExtrudeWithHoles flat capsule / tapered tab links.

    Adapted from rec_..._140c L35-L69: a capsule-outline first link and a
    tapered-tab second link, extruded flat in z with bored pin holes. The
    plate is extruded in z (thickness) and centred on z=0 so the hub
    straddles. Preserves the ExtrudeWithHoles primitive."""
    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]
    half_gap = _half_gap(r)

    plate_t = max(0.006, r.link_height * 0.30)
    plate_r = max(r.lug_radius, r.link_width)
    pin_hole = r.hub_radius * 0.7

    link1 = model.part("link_1")
    _emit_child_hub(link1, r=r, hub_name="link1_hub", material="accent")
    prof = _capsule_profile(r.link1_len, plate_r)
    holes = [
        _circle_profile(pin_hole, center=(0.0, 0.0)),
        _circle_profile(pin_hole, center=(r.link1_len, 0.0)),
    ]
    link1.visual(
        mesh_from_geometry(
            ExtrudeWithHolesGeometry(prof, holes, plate_t),
            "l1_capsule_plate",
        ),
        origin=Origin(xyz=(0.0, 0.0, -0.5 * plate_t)),
        material="body",
        name="link1_plate", material_class_id="metal.paint_coated",
    )
    # Riser bridging the plate down into the distal clevis gap.
    _emit_distal_riser(
        link1,
        r=r,
        pivot_x=r.link1_len - 0.004,
        width=plate_r * 0.9,
        deck=_joint2_deck(r),
        material="body",
        name="link1_distal_riser",
    )
    l1_top_face = _emit_parent_clevis(
        link1,
        r=r,
        pivot_x=r.link1_len,
        pivot_z=0.0,
        half_gap=half_gap,
        top_name="link1_distal_top_lug",
        bottom_name="link1_distal_lower_lug",
        material="dark",
        deck=_joint2_deck(r),
    )
    link1.inertial = Inertial.from_geometry(
        Box((r.link1_len + 0.04, 2 * plate_r, max(plate_t, 2 * half_gap))),
        mass=0.55,
        origin=Origin(xyz=(0.5 * r.link1_len, 0.0, 0.0)),
    )

    link2 = model.part("link_2")
    _emit_child_hub(link2, r=r, hub_name="link2_hub", material="accent")
    plate2_r = plate_r * r.taper_ratio
    tab_r = plate2_r * 0.62
    prof2 = _tapered_tab_profile(r.link2_len, plate2_r, tab_r)
    holes2 = [_circle_profile(pin_hole, center=(0.0, 0.0))]
    link2.visual(
        mesh_from_geometry(
            ExtrudeWithHolesGeometry(prof2, holes2, plate_t),
            "l2_tapered_plate",
        ),
        origin=Origin(xyz=(0.0, 0.0, -0.5 * plate_t)),
        material="body",
        name="link2_plate", material_class_id="metal.paint_coated",
    )
    _emit_integral_end_tab(link2, r=r, material="body")
    link2_downstream = _emit_link2_distal_clevis(link2, r=r, material="dark")
    link2.inertial = Inertial.from_geometry(
        Box((r.link2_len + 0.04, 2 * plate2_r, max(plate_t, 2 * half_gap))),
        mass=0.30,
        origin=Origin(xyz=(0.5 * r.link2_len, 0.0, 0.0)),
    )

    interfaces = _emit_joint2_and_interfaces(
        ctx, r=r, link1=link1, link2=link2, link1_top_face_z=l1_top_face
    )
    if link2_downstream is not None:
        interfaces["downstream"] = link2_downstream
    return ModuleBuild(
        module_name="flat_extrude_capsule",
        parts_emitted=["link_1", "link_2"],
        internal_articulations=["joint_2"],
        interfaces=interfaces,
    )


# ---- cadquery-backed constructions ---- #


def _cq_y_cylinder(radius: float, center: tuple[float, float, float], length_y: float):
    import cadquery as cq

    return cq.Workplane(
        obj=cq.Solid.makeCylinder(
            radius,
            length_y,
            cq.Vector(center[0], center[1] - 0.5 * length_y, center[2]),
            cq.Vector(0.0, 1.0, 0.0),
        )
    )


def _build_clevis_ear_bore_links(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt links — cadquery proximal eye + strap + distal dual-ear, bored.

    Adapted from rec_..._56e0 L156-L220 (``make_first_link`` / ``make_second_link``):
    a proximal eye cylinder (axis y), a flat strap, and distal dual ears with
    bored pin holes. Preserves the cadquery mesh construction; the strap runs
    along +x and the bore axis is y."""
    import cadquery as cq

    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]
    half_gap = _half_gap(r)

    strap_h = r.link_height * 0.55
    ear_w = r.link_width
    bore_r = r.hub_radius * 0.7

    def first_link_shape():
        prox_eye = _cq_y_cylinder(r.hub_radius * 1.3, (0.0, 0.0, 0.0), ear_w)
        strap = cq.Workplane(
            obj=cq.Solid.makeBox(
                r.link1_len, ear_w, strap_h, cq.Vector(0.0, -0.5 * ear_w, -0.5 * strap_h)
            )
        )
        link = prox_eye.union(strap)
        # Distal twin ears straddling the elbow gap.
        ear_y = half_gap + 0.5 * (ear_w * 0.5)
        # Tip yoke: a full-width crossbar at the strap tip that bridges the
        # strap out to both ears. Without it the ears sit beyond the strap's
        # half-width (half_gap > 0.5*ear_w) and float off as a disconnected
        # island.
        yoke_y = ear_y + 0.25 * ear_w
        yoke = cq.Workplane(
            obj=cq.Solid.makeBox(
                r.lug_radius * 1.4,
                2.0 * yoke_y,
                strap_h,
                cq.Vector(r.link1_len - r.lug_radius * 0.7, -yoke_y, -0.5 * strap_h),
            )
        )
        link = link.union(yoke)
        for yc in (-ear_y, ear_y):
            ear = cq.Workplane(
                obj=cq.Solid.makeBox(
                    r.lug_radius * 1.4,
                    ear_w * 0.5,
                    2 * (half_gap + r.lug_thickness),
                    cq.Vector(
                        r.link1_len - r.lug_radius * 0.7,
                        yc - 0.25 * ear_w,
                        -(half_gap + r.lug_thickness),
                    ),
                )
            )
            eye = _cq_y_cylinder(r.lug_radius, (r.link1_len, yc, 0.0), ear_w * 0.5)
            link = link.union(ear).union(eye)
        bore = _cq_y_cylinder(bore_r, (0.0, 0.0, 0.0), ear_w + 0.01)
        return link.cut(bore)

    link1 = model.part("link_1")
    link1.visual(
        mesh_from_cadquery(first_link_shape(), "l1_clevis_strap"),
        material="body",
        name="link1_shell", material_class_id="metal.paint_coated",
    )
    # An explicit hub cylinder (axis z) anchors the upstream mating face and
    # guarantees (0,0,0) is in the AABB along z.
    _emit_child_hub(link1, r=r, hub_name="link1_hub", material="accent")
    l1_top_face = _emit_parent_clevis(
        link1,
        r=r,
        pivot_x=r.link1_len,
        pivot_z=0.0,
        half_gap=half_gap,
        top_name="link1_distal_top_lug",
        bottom_name="link1_distal_lower_lug",
        material="dark",
        deck=_joint2_deck(r),
    )
    link1.inertial = Inertial.from_geometry(
        Box((r.link1_len + 0.04, ear_w * 2.2, max(strap_h, 2 * half_gap))),
        mass=0.6,
        origin=Origin(xyz=(0.5 * r.link1_len, 0.0, 0.0)),
    )

    def second_link_shape():
        prox_eye = _cq_y_cylinder(r.hub_radius * 1.2, (0.0, 0.0, 0.0), ear_w * 0.9)
        strap = cq.Workplane(
            obj=cq.Solid.makeBox(
                r.link2_len,
                ear_w * 0.9,
                strap_h * r.taper_ratio,
                cq.Vector(0.0, -0.45 * ear_w, -0.5 * strap_h * r.taper_ratio),
            )
        )
        end_cap = _cq_y_cylinder(r.hub_radius * 1.0, (r.link2_len, 0.0, 0.0), ear_w * 0.9)
        link = prox_eye.union(strap).union(end_cap)
        bore = _cq_y_cylinder(bore_r, (0.0, 0.0, 0.0), ear_w + 0.01)
        return link.cut(bore)

    link2 = model.part("link_2")
    link2.visual(
        mesh_from_cadquery(second_link_shape(), "l2_clevis_strap"),
        material="body",
        name="link2_shell", material_class_id="metal.paint_coated",
    )
    _emit_child_hub(link2, r=r, hub_name="link2_hub", material="accent")
    _emit_integral_end_tab(link2, r=r, material="body")
    link2_downstream = _emit_link2_distal_clevis(link2, r=r, material="dark")
    link2.inertial = Inertial.from_geometry(
        Box((r.link2_len + 0.04, ear_w * 2.0, max(strap_h, 2 * half_gap))),
        mass=0.34,
        origin=Origin(xyz=(0.5 * r.link2_len, 0.0, 0.0)),
    )

    interfaces = _emit_joint2_and_interfaces(
        ctx, r=r, link1=link1, link2=link2, link1_top_face_z=l1_top_face
    )
    if link2_downstream is not None:
        interfaces["downstream"] = link2_downstream
    return ModuleBuild(
        module_name="clevis_ear_bore",
        parts_emitted=["link_1", "link_2"],
        internal_articulations=["joint_2"],
        interfaces=interfaces,
    )


def _build_windowed_open_frame_links(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt links — cadquery box body with a central window cut + tip yoke.

    Adapted from rec_..._785b L89-L111 (``_link1_shape`` / ``_link2_shape``):
    a box body with a central window cut for a skeletal look, with the body
    running along +x. Preserves the cadquery box + cut construction."""
    import cadquery as cq

    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]
    half_gap = _half_gap(r)

    def windowed_body(length: float, width: float, height: float):
        body = cq.Workplane(
            obj=cq.Solid.makeBox(length, width, height, cq.Vector(0.0, -0.5 * width, -0.5 * height))
        )
        win_l = length * 0.55
        win_h = height * 0.45
        window = cq.Workplane(
            obj=cq.Solid.makeBox(
                win_l,
                width + 0.01,
                win_h,
                cq.Vector(length * 0.25, -0.5 * width - 0.005, -0.5 * win_h),
            )
        )
        return body.cut(window)

    link1 = model.part("link_1")
    link1.visual(
        mesh_from_cadquery(
            windowed_body(r.link1_len, r.link_width, r.link_height), "l1_windowed_body"
        ),
        material="body",
        name="link1_shell", material_class_id="metal.paint_coated",
    )
    _emit_child_hub(link1, r=r, hub_name="link1_hub", material="accent")
    _emit_distal_riser(
        link1,
        r=r,
        pivot_x=r.link1_len - 0.004,
        width=r.link_width * 0.8,
        deck=_joint2_deck(r),
        material="body",
        name="link1_distal_riser",
    )
    l1_top_face = _emit_parent_clevis(
        link1,
        r=r,
        pivot_x=r.link1_len,
        pivot_z=0.0,
        half_gap=half_gap,
        top_name="link1_distal_top_lug",
        bottom_name="link1_distal_lower_lug",
        material="dark",
        deck=_joint2_deck(r),
    )
    link1.inertial = Inertial.from_geometry(
        Box((r.link1_len + 0.04, r.link_width * 1.4, max(r.link_height, 2 * half_gap))),
        mass=0.5,
        origin=Origin(xyz=(0.5 * r.link1_len, 0.0, 0.0)),
    )

    link2 = model.part("link_2")
    w2 = r.link_width * r.taper_ratio
    h2 = r.link_height * r.taper_ratio
    link2.visual(
        mesh_from_cadquery(windowed_body(r.link2_len, w2, h2), "l2_windowed_body"),
        material="body",
        name="link2_shell", material_class_id="metal.paint_coated",
    )
    _emit_child_hub(link2, r=r, hub_name="link2_hub", material="accent")
    _emit_integral_end_tab(link2, r=r, material="body")
    link2_downstream = _emit_link2_distal_clevis(link2, r=r, material="dark")
    link2.inertial = Inertial.from_geometry(
        Box((r.link2_len + 0.04, w2 * 1.4, max(h2, 2 * half_gap))),
        mass=0.28,
        origin=Origin(xyz=(0.5 * r.link2_len, 0.0, 0.0)),
    )

    interfaces = _emit_joint2_and_interfaces(
        ctx, r=r, link1=link1, link2=link2, link1_top_face_z=l1_top_face
    )
    if link2_downstream is not None:
        interfaces["downstream"] = link2_downstream
    return ModuleBuild(
        module_name="windowed_open_frame",
        parts_emitted=["link_1", "link_2"],
        internal_articulations=["joint_2"],
        interfaces=interfaces,
    )


def _build_dual_sideplate_ladder_links(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt links — two parallel side plates + end caps + central windows.

    Adapted from rec_..._9bd9 L48-L89 (``_capsule_plate`` / ``_make_link1_shape``):
    a ladder frame of two side plates joined by root/tip bridges, each plate
    windowed. Preserves the cadquery dual-plate + window cut construction.
    The two plates are bridged so the part is one connected island."""
    import cadquery as cq

    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]
    half_gap = _half_gap(r)

    def ladder_shape(length: float, width: float, height: float):
        plate_t = max(0.006, width * 0.20)
        offset = 0.5 * width - 0.5 * plate_t
        root_bridge = cq.Workplane(
            obj=cq.Solid.makeBox(0.024, width, height, cq.Vector(0.0, -0.5 * width, -0.5 * height))
        )
        tip_bridge = cq.Workplane(
            obj=cq.Solid.makeBox(
                0.024, width, height, cq.Vector(length - 0.024, -0.5 * width, -0.5 * height)
            )
        )
        shape = root_bridge.union(tip_bridge)
        for yc in (-offset, offset):
            plate = cq.Workplane(
                obj=cq.Solid.makeBox(
                    length, plate_t, height, cq.Vector(0.0, yc - 0.5 * plate_t, -0.5 * height)
                )
            )
            win = cq.Workplane(
                obj=cq.Solid.makeBox(
                    length * 0.5,
                    plate_t + 0.01,
                    height * 0.45,
                    cq.Vector(length * 0.27, yc - 0.5 * plate_t - 0.005, -0.5 * height * 0.45),
                )
            )
            shape = shape.union(plate.cut(win))
        return shape

    link1 = model.part("link_1")
    link1.visual(
        mesh_from_cadquery(
            ladder_shape(r.link1_len, max(r.link_width, 0.05), r.link_height), "l1_ladder"
        ),
        material="body",
        name="link1_shell", material_class_id="metal.paint_coated",
    )
    _emit_child_hub(link1, r=r, hub_name="link1_hub", material="accent")
    _emit_distal_riser(
        link1,
        r=r,
        pivot_x=r.link1_len - 0.004,
        width=max(r.link_width, 0.05) * 0.9,
        deck=_joint2_deck(r),
        material="body",
        name="link1_distal_riser",
    )
    l1_top_face = _emit_parent_clevis(
        link1,
        r=r,
        pivot_x=r.link1_len,
        pivot_z=0.0,
        half_gap=half_gap,
        top_name="link1_distal_top_lug",
        bottom_name="link1_distal_lower_lug",
        material="dark",
        deck=_joint2_deck(r),
    )
    link1.inertial = Inertial.from_geometry(
        Box((r.link1_len + 0.04, max(r.link_width, 0.05) * 1.2, max(r.link_height, 2 * half_gap))),
        mass=0.6,
        origin=Origin(xyz=(0.5 * r.link1_len, 0.0, 0.0)),
    )

    link2 = model.part("link_2")
    w2 = max(r.link_width, 0.05) * r.taper_ratio
    h2 = r.link_height * r.taper_ratio
    link2.visual(
        mesh_from_cadquery(ladder_shape(r.link2_len, w2, h2), "l2_ladder"),
        material="body",
        name="link2_shell", material_class_id="metal.paint_coated",
    )
    _emit_child_hub(link2, r=r, hub_name="link2_hub", material="accent")
    _emit_integral_end_tab(link2, r=r, material="body")
    link2_downstream = _emit_link2_distal_clevis(link2, r=r, material="dark")
    link2.inertial = Inertial.from_geometry(
        Box((r.link2_len + 0.04, w2 * 1.2, max(h2, 2 * half_gap))),
        mass=0.32,
        origin=Origin(xyz=(0.5 * r.link2_len, 0.0, 0.0)),
    )

    interfaces = _emit_joint2_and_interfaces(
        ctx, r=r, link1=link1, link2=link2, link1_top_face_z=l1_top_face
    )
    if link2_downstream is not None:
        interfaces["downstream"] = link2_downstream
    return ModuleBuild(
        module_name="dual_sideplate_ladder",
        parts_emitted=["link_1", "link_2"],
        internal_articulations=["joint_2"],
        interfaces=interfaces,
    )


# --------------------------------------------------------------------------- #
# Slot C — terminal module factories.
#
# integral_end_tab emits NO part and NO upstream interface (the tab was fused
# into link_2 by the links factory); the assembler therefore emits no joint.
# The separate terminals emit an independent part with an upstream hub
# (consumer FIXED), which the assembler chains to link_2's distal clevis.
# --------------------------------------------------------------------------- #


def _build_integral_end_tab_terminal(ctx: ModuleBuildContext) -> ModuleBuild:
    """Integral terminal — no separate part (tab fused into link_2)."""
    return ModuleBuild(
        module_name="integral_end_tab",
        parts_emitted=[],
        internal_articulations=[],
        interfaces={},  # no upstream -> assembler emits no chain joint
    )


def _terminal_upstream_iface(r: ResolvedTwojointRevoluteChainConfig) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="upstream",
        part_name="end_effector",
        visual_name="end_hub",
        face_side="negative_z",
        anchor_local=(0.0, 0.0, 0.0),
        face_extents_uv=(2.0 * r.hub_radius, 2.0 * r.hub_radius),
        extents_tol=0.60,
        contact_tol=0.0030,
        consumer_joint_type=ArticulationType.FIXED,
        consumer_joint_axis=r.axis,
        consumer_motion_limits=None,
    )


def _build_separate_fixed_pad_terminal(ctx: ModuleBuildContext) -> ModuleBuild:
    """Separate terminal — an independent tool/pad part, FIXED to link_2.

    Adapted from rec_..._0001 L55-L59 (``_build_tool_shape``): a mount + body
    + nose pad. Primitive Box; FIXED at the link_2 tip clevis."""
    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]
    half_gap = _half_gap(r)

    end = model.part("end_effector")
    _emit_child_hub(end, r=r, hub_name="end_hub", material="accent")
    pad_h = r.link_height * 0.9
    pad_w = r.link_width * 1.1
    # Mount block sits over the hub then a body and nose extend +x.
    mount_len = max(0.018, half_gap * 2 + 0.006)
    end.visual(
        Box((mount_len, pad_w * 0.7, pad_h * 0.7)),
        origin=Origin(xyz=(0.5 * mount_len - r.hub_radius * 0.3, 0.0, 0.0)),
        material="body",
        name="pad_mount", material_class_id="metal.paint_coated",
    )
    body_len = 0.055
    nose_len = 0.020
    # Anchor each segment to overlap the previous one so the pad is one
    # connected part (the mount front is pulled back over the hub, so the body
    # must reach back to it — otherwise pad_body/pad_nose float off as islands).
    mount_front = mount_len - r.hub_radius * 0.3
    body_back = mount_front - 0.006
    body_front = body_back + body_len
    end.visual(
        Box((body_len, pad_w, pad_h)),
        origin=Origin(xyz=(body_back + 0.5 * body_len, 0.0, 0.0)),
        material="body",
        name="pad_body", material_class_id="metal.paint_coated",
    )
    end.visual(
        Box((nose_len, pad_w * 0.6, pad_h * 0.6)),
        origin=Origin(xyz=(body_front - 0.006 + 0.5 * nose_len, 0.0, 0.0)),
        material="pad",
        name="pad_nose", material_class_id="rubber.smooth_plain",
    )
    end.inertial = Inertial.from_geometry(
        Box((mount_len + body_len + 0.03, pad_w, pad_h)),
        mass=0.18,
        origin=Origin(xyz=(0.5 * (mount_len + body_len), 0.0, 0.0)),
    )

    return ModuleBuild(
        module_name="separate_fixed_pad",
        parts_emitted=["end_effector"],
        internal_articulations=[],
        interfaces={"upstream": _terminal_upstream_iface(r)},
    )


def _build_separate_fixed_clamp_terminal(ctx: ModuleBuildContext) -> ModuleBuild:
    """Separate terminal — clamp plate + jaw pads + bolts, FIXED to link_2.

    Adapted from rec_..._98f91b L100-L132: a clamp adapter, a broad clamp
    plate, two jaw pads, and four clamp bolts. Primitive Box/Cylinder."""
    model = ctx.model
    r: ResolvedTwojointRevoluteChainConfig = ctx.config  # type: ignore[assignment]
    half_gap = _half_gap(r)

    end = model.part("end_effector")
    _emit_child_hub(end, r=r, hub_name="end_hub", material="accent")
    adapter_len = max(0.020, half_gap * 2 + 0.008)
    end.visual(
        Box((adapter_len, r.link_width * 0.9, r.link_height * 0.9)),
        origin=Origin(xyz=(0.5 * adapter_len - r.hub_radius * 0.3, 0.0, 0.0)),
        material="body",
        name="clamp_adapter", material_class_id="metal.paint_coated",
    )
    # Seat the plate against the adapter front (the adapter front is pulled
    # back over the hub) so the clamp head is connected, not a floating island.
    adapter_front = adapter_len - r.hub_radius * 0.3
    plate_x = adapter_front + 0.002
    plate_w = r.link_width * 3.0
    plate_h = r.link_height * 2.4
    end.visual(
        Box((0.014, plate_w, plate_h)),
        origin=Origin(xyz=(plate_x, 0.0, 0.0)),
        material="body",
        name="clamp_plate", material_class_id="metal.paint_coated",
    )
    for zz, name in ((plate_h * 0.30, "upper_jaw_pad"), (-plate_h * 0.30, "lower_jaw_pad")):
        end.visual(
            Box((0.008, plate_w * 0.7, plate_h * 0.22)),
            origin=Origin(xyz=(plate_x + 0.010, 0.0, zz)),
            material="pad",
            name=name, material_class_id="rubber.smooth_plain",
        )
    if r.detail_level != "plain":
        for i, (yy, zz) in enumerate(
            (
                (-plate_w * 0.3, plate_h * 0.3),
                (plate_w * 0.3, plate_h * 0.3),
                (-plate_w * 0.3, -plate_h * 0.3),
                (plate_w * 0.3, -plate_h * 0.3),
            )
        ):
            end.visual(
                Cylinder(radius=0.006, length=0.010),
                origin=Origin(xyz=(plate_x + 0.004, yy, zz), rpy=(0.0, math.pi / 2.0, 0.0)),
                material="bolt",
                name=f"clamp_bolt_{i}", material_class_id="metal.blackened_gunmetal",
            )
    end.inertial = Inertial.from_geometry(
        Box((plate_x + 0.04, plate_w, plate_h)),
        mass=0.22,
        origin=Origin(xyz=(0.5 * plate_x, 0.0, 0.0)),
    )

    return ModuleBuild(
        module_name="separate_fixed_clamp",
        parts_emitted=["end_effector"],
        internal_articulations=[],
        interfaces={"upstream": _terminal_upstream_iface(r)},
    )


# --------------------------------------------------------------------------- #
# Slot graph + entry points
# --------------------------------------------------------------------------- #


BASE_FACTORIES = {
    "pedestal_column": _build_pedestal_column_base,
    "grounded_clevis_bracket": _build_grounded_clevis_bracket_base,
    "wall_backplate": _build_wall_backplate_base,
    "broad_mounting_plate": _build_broad_mounting_plate_base,
    "side_cheek_plate": _build_side_cheek_plate_base,
}

LINK_FACTORIES = {
    "solid_box_beam": _build_solid_box_beam_links,
    "clevis_ear_bore": _build_clevis_ear_bore_links,
    "windowed_open_frame": _build_windowed_open_frame_links,
    "dual_sideplate_ladder": _build_dual_sideplate_ladder_links,
    "flat_extrude_capsule": _build_flat_extrude_capsule_links,
    "primitive_lug_barrel": _build_primitive_lug_barrel_links,
}

TERMINAL_FACTORIES = {
    "integral_end_tab": _build_integral_end_tab_terminal,
    "separate_fixed_pad": _build_separate_fixed_pad_terminal,
    "separate_fixed_clamp": _build_separate_fixed_clamp_terminal,
}


def _slots_for_config(r: ResolvedTwojointRevoluteChainConfig) -> list[SlotSpec]:
    """Build the slot graph pinned to the chosen modules (so the assembler
    doesn't re-roll for non-zero seeds).

    Strict chain: base -> links -> terminal. The anchor combination (seed=0)
    is pedestal_column / solid_box_beam / integral_end_tab + vertical_pitch.
    """
    return [
        SlotSpec(
            slot_name="base",
            candidates={r.base_module: BASE_FACTORIES[r.base_module]},
            anchor_choice=r.base_module,
        ),
        SlotSpec(
            slot_name="links",
            candidates={r.link_module: LINK_FACTORIES[r.link_module]},
            anchor_choice=r.link_module,
        ),
        SlotSpec(
            slot_name="terminal",
            candidates={r.terminal_module: TERMINAL_FACTORIES[r.terminal_module]},
            anchor_choice=r.terminal_module,
        ),
    ]


def build_twojoint_revolute_chain(
    config: TwojointRevoluteChainConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    """Compose a two-joint revolute chain by running each slot's module
    factory and joining them with `MatingContract`-backed articulations."""

    r = resolve_config(config)
    model = ArticulatedObject(name="twojoint_revolute_chain", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    rng = random.Random(0)
    assemble(
        model,
        slots=_slots_for_config(r),
        rng=rng,
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_twojoint_revolute_chain(seed: int) -> ArticulatedObject:
    return build_twojoint_revolute_chain(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Return the (slot, module) picks for inspection — consumed by the
    `module_topology_diversity` gate to count unique topologies."""
    cfg = config_from_seed(seed)
    r = resolve_config(cfg)
    return [
        ("base", r.base_module),
        ("links", r.link_module),
        ("terminal", r.terminal_module),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC — captured-pivot overlap allowances + chain sanity.
# --------------------------------------------------------------------------- #


def _allow_internal_pivot_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    """Declare the intentional clevis-lug ↔ hub captured-pin overlaps that
    the rest-pose overlap QC would otherwise flag. Module-aware: only the
    part pairs that the chosen modules emitted are referenced."""
    part_names = {p.name for p in model.parts}

    # joint_1: base clevis lugs ↔ link_1 hub (+ link_1 body near the hub).
    if "base" in part_names and "link_1" in part_names:
        base = model.get_part("base")
        link1 = model.get_part("link_1")
        link1_visuals = {v.name for v in link1.visuals}
        link1_body_candidates = [
            n
            for n in (
                "link1_hub",
                "link1_beam",
                "link1_bar",
                "link1_plate",
                "link1_shell",
                "link1_prox_barrel",
            )
            if n in link1_visuals
        ]
        for parent_elem in (
            "joint1_top_lug",
            "joint1_lower_lug",
            "joint1_pin_cap",
            "pivot_riser",
            "pivot_bar",
            "root_mount",
            "pivot_post",
            "cheek_riser",
            "cheek_plate",
            "rear_web",
            "column",
        ):
            if parent_elem not in {v.name for v in base.visuals}:
                continue
            for child_elem in link1_body_candidates:
                ctx.allow_overlap(
                    base,
                    link1,
                    elem_a=parent_elem,
                    elem_b=child_elem,
                    reason=f"{parent_elem} captures {child_elem} at joint_1",
                )

    # joint_2: link_1 distal clevis lugs ↔ link_2 hub / body.
    if "link_1" in part_names and "link_2" in part_names:
        link1 = model.get_part("link_1")
        link2 = model.get_part("link_2")
        l1_visuals = {v.name for v in link1.visuals}
        l2_visuals = {v.name for v in link2.visuals}
        l1_distal = [
            n
            for n in (
                "link1_distal_top_lug",
                "link1_distal_lower_lug",
                "link1_distal_riser",
                "link1_beam",
                "link1_bar",
                "link1_plate",
                "link1_shell",
            )
            if n in l1_visuals
        ]
        l2_prox = [
            n
            for n in (
                "link2_hub",
                "link2_beam",
                "link2_bar",
                "link2_plate",
                "link2_shell",
                "link2_prox_barrel",
            )
            if n in l2_visuals
        ]
        for parent_elem in l1_distal:
            for child_elem in l2_prox:
                ctx.allow_overlap(
                    link1,
                    link2,
                    elem_a=parent_elem,
                    elem_b=child_elem,
                    reason=f"{parent_elem} captures {child_elem} at joint_2",
                )

    # joint_3 (separate terminal): link_2 distal clevis lugs ↔ end_effector hub.
    if "link_2" in part_names and "end_effector" in part_names:
        link2 = model.get_part("link_2")
        end = model.get_part("end_effector")
        l2_visuals = {v.name for v in link2.visuals}
        end_visuals = {v.name for v in end.visuals}
        l2_distal = [
            n
            for n in (
                "link2_distal_top_lug",
                "link2_distal_lower_lug",
                "link2_distal_riser",
                "link2_beam",
                "link2_bar",
                "link2_plate",
                "link2_shell",
            )
            if n in l2_visuals
        ]
        end_prox = [n for n in ("end_hub", "pad_mount", "clamp_adapter") if n in end_visuals]
        for parent_elem in l2_distal:
            for child_elem in end_prox:
                ctx.allow_overlap(
                    link2,
                    end,
                    elem_a=parent_elem,
                    elem_b=child_elem,
                    reason=f"{parent_elem} captures {child_elem} at joint_3",
                )


def _expect_joint1_moves_link2(ctx: TestContext, model: ArticulatedObject) -> None:
    """Rotating joint_1 must measurably move the distal link/end."""
    part_names = {p.name for p in model.parts}
    tail = "end_effector" if "end_effector" in part_names else "link_2"
    if tail not in part_names:
        return
    tail_part = model.get_part(tail)
    try:
        joint1 = model.get_articulation("base_to_links")
    except Exception:  # noqa: BLE001
        return
    rest = ctx.part_world_position(tail_part)
    with ctx.pose({joint1: 0.5}):
        moved = ctx.part_world_position(tail_part)
    if rest is None or moved is None:
        return
    delta = sum((moved[i] - rest[i]) ** 2 for i in range(3)) ** 0.5
    ctx.check(
        "joint_1_moves_distal_link",
        delta > 0.02,
        f"rest={rest}, moved={moved}, |delta|={delta:.4f}",
    )


def run_twojoint_revolute_chain_tests(
    model: ArticulatedObject,
    config: TwojointRevoluteChainConfig,
) -> TestReport:
    """Author-layer QC for the modular two-joint revolute chain.

    The compiler-owned baseline runs validity / isolated-parts / overlap /
    mating-gap / origin-proximity / island checks separately. This function
    only adds the module-aware captured-pin overlap allowances + a chain
    motion sanity check that generic gates don't cover.
    """
    ctx = TestContext(model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    _allow_internal_pivot_overlaps(ctx, model)
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    _expect_joint1_moves_link2(ctx, model)

    return ctx.report()


# --------------------------------------------------------------------------- #
# Modular template authoring notes
# --------------------------------------------------------------------------- #
# Slot roster:
#   base (Slot A, 5): pedestal_column [anchor] / grounded_clevis_bracket /
#       wall_backplate / broad_mounting_plate / side_cheek_plate
#   links (Slot B, 6): solid_box_beam [anchor] / clevis_ear_bore /
#       windowed_open_frame / dual_sideplate_ladder / flat_extrude_capsule /
#       primitive_lug_barrel  (shared construction for link_1 AND link_2)
#   terminal (Slot C, 3): integral_end_tab [anchor] / separate_fixed_pad /
#       separate_fixed_clamp
#   axis_family (cross-cutting): vertical_pitch [anchor, axis (0,-1,0)] /
#       planar_yaw [axis (0,0,1)] — both joint axes identical & parallel.
#
# Topology: base --[base_to_links REVOLUTE = joint_1]--> link_1
#                --[joint_2 REVOLUTE internal]--> link_2
#                --[links_to_terminal FIXED = joint_3, only if separate]--> end
#
# Combinations: 5 bases x 6 links x 3 terminals = 90 (x2 axis_family).
# module_topology_diversity counts distinct (base, links, terminal) tuples.


__all__ = [
    "AxisFamily",
    "BaseModule",
    "ChainPaletteTheme",
    "DetailLevel",
    "LinkModule",
    "ResolvedTwojointRevoluteChainConfig",
    "TerminalModule",
    "TwojointRevoluteChainConfig",
    "build_seeded_twojoint_revolute_chain",
    "build_twojoint_revolute_chain",
    "config_from_seed",
    "resolve_config",
    "run_twojoint_revolute_chain_tests",
    "slot_choices_for_seed",
]
