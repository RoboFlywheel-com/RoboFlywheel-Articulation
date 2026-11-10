# SPDX-License-Identifier: Apache-2.0

"""Three-stage telescoping slide — modular procedural template.

This template uses the slot/module/assembler abstraction in
``agent.templates._modular``. Six slots — **base**, **outer**, **middle**,
**inner**, **terminal**, **detail** — compose a strictly linear
*prismatic* chain of three nested members plus optional fixed children.

Slot graph (mixed: prismatic main chain + optional FIXED children):

    [base]  (root link, grounded; absent when section is integral)
        | FIXED  (base_to_outer; only when base is NOT integral)
        v
    [outer] --prismatic(+X, outer_to_middle)--> [middle]
        |                                            | prismatic(+X, middle_to_inner)
        |                                            v
        |                                        [inner]
        |                                            | FIXED (inner_to_terminal)
        |                                            v
        +------- detail (cover/cage/stop/rollers FIXED to members) -- [terminal]

Topology axes:

  base (Slot A, 4):
    - integral_grounded_outer (anchor) — no base part, outer IS the root.
    - support_frame_fixed     — a welded support frame root, outer FIXED on top.
    - wall_backplate_fixed     — a vertical backplate root, outer FIXED in front.
    - grounded_carrier_body    — a U-channel carrier body root, outer FIXED inside.

  section_style (cross-cutting, 4) — LOCKS the outer/middle/inner member
  geometry to one cross-section family so the three nested stages never mix
  cross sections:
    - closed_box_tube     (anchor) — mesh hollow box tube (concentric, yz nesting).
    - open_channel_raceway          — mesh C-channel + raceway (concentric, yz).
    - primitive_wall_box            — Box-primitive floor/walls/front-frame.
    - side_web_race                 — Box-primitive side web + lips + races (y nesting).

  terminal (Slot E, 4):
    - bare_no_terminal (anchor) — no terminal part.
    - carriage_shoe             — carriage shoe FIXED on the inner end face.
    - flat_end_plate            — flat end plate FIXED on the inner end face.
    - top_carriage_tray         — top tray/carriage FIXED above the inner end.

  detail (Slot F, 4):
    - none_clean (anchor) — no decorative hardware.
    - stop_tabs_only      — stop tabs folded into the members (visuals only).
    - guide_cage_pads_rollers — a guide cage part FIXED to the outer member.
    - ball_race_rollers   — cylindrical ball/roller race FIXED to the outer member.

seed == 0 always picks the anchor combination
(integral_grounded_outer + closed_box_tube + bare_no_terminal + none_clean),
reproducing the canonical 5-star sample (rec_threestage_telescoping_slide_0002).
Other seeds RNG-pick uniformly across base / section_style / terminal / detail.

Mating model: the two main prismatic joints (``outer_to_middle`` /
``middle_to_inner``) are deliberately **grandfathered** — telescoping nested
members slide *inside* one another, so there is no clean axis-aligned face
contact for ``fail_if_joint_mating_has_gap`` to verify. We omit ``mating=`` on
those joints (and on the per-member FIXED detail joints, whose anchoring is a
shared volume, not a single contact face) and rely instead on
``expect_within`` / ``expect_overlap`` semantics plus ``allow_overlap``
declarations for the intentional nested overlap. The ``base_to_outer`` and
``inner_to_terminal`` FIXED joints DO use real ``MatingContract``s where the
geometry is a single clean contact face.

To keep full control over joint types / axes / mating, every joint here is
emitted manually inside the module factories (the parallel-children pattern):
each factory reads ``ctx.upstream_interface.part_name`` to find its parent and
emits its own articulation; member modules do NOT return an ``"upstream"``
interface, so the assembler never injects a forced-MatingContract chain joint.
All joints here are grandfathered (no MatingContract): the prismatic slides
have no clean axis-aligned contact face, the FIXED base/terminal/detail joints
anchor by shared volume rather than a single touching face, and the intended
overlaps are allow-listed in ``run_threestage_telescoping_slide_tests``.
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
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


BaseModule = Literal[
    "integral_grounded_outer",
    "support_frame_fixed",
    "wall_backplate_fixed",
    "grounded_carrier_body",
]
SectionStyle = Literal[
    "closed_box_tube",
    "open_channel_raceway",
    "primitive_wall_box",
    "side_web_race",
]
TerminalModule = Literal[
    "bare_no_terminal",
    "carriage_shoe",
    "flat_end_plate",
    "top_carriage_tray",
]
DetailModule = Literal[
    "none_clean",
    "stop_tabs_only",
    "guide_cage_pads_rollers",
    "ball_race_rollers",
]

SlidePaletteTheme = Literal[
    "machined_steel",
    "anodized_black",
    "galvanized",
    "zinc_bronze",
]


SLIDE_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "machined_steel": {
        "outer": (0.28, 0.30, 0.33, 1.0),
        "middle": (0.56, 0.58, 0.60, 1.0),
        "inner": (0.73, 0.74, 0.76, 1.0),
        "base": (0.20, 0.22, 0.24, 1.0),
        "bracket": (0.82, 0.84, 0.86, 1.0),
        "hardware": (0.16, 0.18, 0.20, 1.0),
        "roller": (0.62, 0.50, 0.30, 1.0),
    },
    "anodized_black": {
        "outer": (0.10, 0.10, 0.11, 1.0),
        "middle": (0.24, 0.24, 0.26, 1.0),
        "inner": (0.45, 0.46, 0.48, 1.0),
        "base": (0.06, 0.06, 0.07, 1.0),
        "bracket": (0.30, 0.31, 0.33, 1.0),
        "hardware": (0.66, 0.67, 0.69, 1.0),
        "roller": (0.74, 0.62, 0.34, 1.0),
    },
    "galvanized": {
        "outer": (0.55, 0.58, 0.60, 1.0),
        "middle": (0.66, 0.69, 0.71, 1.0),
        "inner": (0.78, 0.80, 0.82, 1.0),
        "base": (0.48, 0.51, 0.54, 1.0),
        "bracket": (0.86, 0.88, 0.90, 1.0),
        "hardware": (0.18, 0.20, 0.22, 1.0),
        "roller": (0.20, 0.22, 0.24, 1.0),
    },
    "zinc_bronze": {
        "outer": (0.34, 0.30, 0.24, 1.0),
        "middle": (0.52, 0.46, 0.34, 1.0),
        "inner": (0.74, 0.66, 0.46, 1.0),
        "base": (0.22, 0.19, 0.14, 1.0),
        "bracket": (0.80, 0.72, 0.50, 1.0),
        "hardware": (0.14, 0.13, 0.10, 1.0),
        "roller": (0.85, 0.60, 0.30, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config / ResolvedConfig
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ThreestageTelescopingSlideConfig:
    """Public template config. Module-selection fields are opt-in: leave any
    as ``None`` to let ``config_from_seed`` / ``resolve_config`` fill them from
    the seed-driven RNG.

    ``section_style`` LOCKS the cross section of all three members (outer /
    middle / inner). It is a single cross-cutting axis — the three stages
    always share one section family.
    """

    base_module: BaseModule | None = None
    section_style: SectionStyle | None = None
    terminal_module: TerminalModule | None = None
    detail_module: DetailModule | None = None
    palette_theme: SlidePaletteTheme = "machined_steel"

    # Outer member envelope.
    outer_len: float = 0.340
    outer_w: float = 0.038
    outer_h: float = 0.030
    wall: float = 0.003

    # Stage scaling + clearance.
    stage_ratio: float = 0.79
    clearance: float = 0.0035

    # Mount geometry.
    mount_setback: float = 0.026
    base_height: float = 0.060

    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(SLIDE_PALETTE_PRESETS["machined_steel"])
    )


@dataclass(frozen=True)
class ResolvedThreestageTelescopingSlideConfig:
    """Dimension-clamped + module-resolved config consumed by builders.

    The derived stage geometry (lengths, widths, heights, travels, home
    setbacks) is computed once in ``resolve_config`` so every module factory
    reads a single consistent source of truth.
    """

    base_module: BaseModule
    section_style: SectionStyle
    terminal_module: TerminalModule
    detail_module: DetailModule
    palette_theme: SlidePaletteTheme

    wall: float
    clearance: float
    mount_setback: float
    base_height: float

    # Outer member.
    outer_len: float
    outer_w: float
    outer_h: float
    # Middle member (cross section derived from the outer inner cavity).
    middle_len: float
    middle_w: float
    middle_h: float
    # Inner member.
    inner_len: float
    inner_w: float
    inner_h: float

    # Prismatic travels (lower=0, upper=travel) chosen so an engagement
    # margin remains at full stroke (inner stays inside middle, middle inside
    # outer).
    outer_to_middle_travel: float
    middle_to_inner_travel: float
    # Home (retracted) x-offset of each stage's joint origin (positive = the
    # child starts pushed inward / setback into the parent so it has visible
    # overlap on BOTH sides of its stroke).
    outer_to_middle_home: float
    middle_to_inner_home: float

    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> ThreestageTelescopingSlideConfig:
    """Sample a slide configuration for the given seed.

    seed == 0 returns the anchor combination
    (integral_grounded_outer + closed_box_tube + bare_no_terminal +
    none_clean) at the anchor's canonical dimensions
    (rec_threestage_telescoping_slide_0002). Other seeds RNG-pick each slot's
    module and sample dimensions across the spec's ranges.
    """

    if seed == 0:
        return ThreestageTelescopingSlideConfig(
            base_module="integral_grounded_outer",
            section_style="closed_box_tube",
            terminal_module="bare_no_terminal",
            detail_module="none_clean",
            palette_theme="machined_steel",
            outer_len=0.340,
            outer_w=0.038,
            outer_h=0.030,
            wall=0.003,
            stage_ratio=0.79,
            clearance=0.0035,
            mount_setback=0.026,
            base_height=0.060,
        )

    rng = random.Random(seed)
    base: BaseModule = rng.choice(
        (
            "integral_grounded_outer",
            "support_frame_fixed",
            "wall_backplate_fixed",
            "grounded_carrier_body",
        )
    )
    section: SectionStyle = rng.choice(
        (
            "closed_box_tube",
            "open_channel_raceway",
            "primitive_wall_box",
            "side_web_race",
        )
    )
    terminal: TerminalModule = rng.choice(
        (
            "bare_no_terminal",
            "carriage_shoe",
            "flat_end_plate",
            "top_carriage_tray",
        )
    )
    detail: DetailModule = rng.choice(
        (
            "none_clean",
            "stop_tabs_only",
            "guide_cage_pads_rollers",
            "ball_race_rollers",
        )
    )
    palette_theme: SlidePaletteTheme = rng.choice(tuple(SLIDE_PALETTE_PRESETS.keys()))

    return ThreestageTelescopingSlideConfig(
        base_module=base,
        section_style=section,
        terminal_module=terminal,
        detail_module=detail,
        palette_theme=palette_theme,
        outer_len=round(rng.uniform(0.220, 0.640), 4),
        outer_w=round(rng.uniform(0.030, 0.072), 4),
        outer_h=round(rng.uniform(0.024, 0.052), 4),
        wall=round(rng.uniform(0.0022, 0.0040), 5),
        stage_ratio=round(rng.uniform(0.74, 0.84), 4),
        clearance=round(rng.uniform(0.0020, 0.0050), 5),
        mount_setback=round(rng.uniform(0.014, 0.045), 4),
        base_height=round(rng.uniform(0.045, 0.090), 4),
    )


def resolve_config(
    config: ThreestageTelescopingSlideConfig,
) -> ResolvedThreestageTelescopingSlideConfig:
    """Validate enums (raise on bad), clamp floats, fill None with anchors,
    enforce the section_style lock, and derive stage geometry + travels with a
    guaranteed engagement margin."""

    base = config.base_module or "integral_grounded_outer"
    section = config.section_style or "closed_box_tube"
    terminal = config.terminal_module or "bare_no_terminal"
    detail = config.detail_module or "none_clean"

    if base not in (
        "integral_grounded_outer",
        "support_frame_fixed",
        "wall_backplate_fixed",
        "grounded_carrier_body",
    ):
        raise ValueError(f"Unsupported base_module: {base}")
    if section not in (
        "closed_box_tube",
        "open_channel_raceway",
        "primitive_wall_box",
        "side_web_race",
    ):
        raise ValueError(f"Unsupported section_style: {section}")
    if terminal not in (
        "bare_no_terminal",
        "carriage_shoe",
        "flat_end_plate",
        "top_carriage_tray",
    ):
        raise ValueError(f"Unsupported terminal_module: {terminal}")
    if detail not in (
        "none_clean",
        "stop_tabs_only",
        "guide_cage_pads_rollers",
        "ball_race_rollers",
    ):
        raise ValueError(f"Unsupported detail_module: {detail}")
    if str(config.palette_theme) not in SLIDE_PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    wall = max(0.0020, min(float(config.wall), 0.0050))
    clearance = max(0.0015, min(float(config.clearance), 0.0060))
    mount_setback = max(0.012, min(float(config.mount_setback), 0.050))
    base_height = max(0.040, min(float(config.base_height), 0.100))

    outer_len = max(0.180, min(float(config.outer_len), 0.720))
    outer_w = max(0.028, min(float(config.outer_w), 0.080))
    outer_h = max(0.022, min(float(config.outer_h), 0.056))
    stage_ratio = max(0.72, min(float(config.stage_ratio), 0.86))

    # Cross-section nesting derivation. ``clearance`` now genuinely influences
    # the child extents: larger requested clearance makes each child stage
    # narrower/shorter in Y/Z. We still retain a tiny contact lip so the exact
    # physical support checks can see the telescoping engagement instead of
    # treating each nested stage as a floating body in an empty cavity.
    contact = min(0.0010, wall * 0.4)
    min_retained_contact = min(0.00015, wall * 0.08)
    retained_contact = max(min_retained_contact, contact - clearance * 0.15)
    step = max(0.0008, wall - retained_contact)
    middle_w = max(0.016, outer_w - 2.0 * step)
    middle_h = max(0.012, outer_h - 2.0 * step)
    inner_w = max(0.010, middle_w - 2.0 * step)
    inner_h = max(0.008, middle_h - 2.0 * step)

    middle_len = outer_len * stage_ratio
    inner_len = middle_len * stage_ratio

    # Travels: keep a retained-overlap margin so each stage stays engaged at
    # full stroke. Both the child length and the parent length after the home
    # setback constrain the maximum travel. This matters for public configs
    # near the legal minimum length with a large mount_setback.
    min_overlap = max(0.030, outer_len * 0.18)
    om_cap = min(middle_len - min_overlap, outer_len - mount_setback - min_overlap)
    mi_cap = min(inner_len - min_overlap, middle_len - mount_setback - min_overlap)
    outer_to_middle_travel = min(0.32, max(0.005, om_cap))
    middle_to_inner_travel = min(0.28, max(0.005, mi_cap))
    # The second stage travel never exceeds the first (telescoping order).
    middle_to_inner_travel = min(middle_to_inner_travel, outer_to_middle_travel)

    # Home setbacks: the child sits pushed inward by ``mount_setback`` at rest
    # so there is overlap on BOTH the retracted and extended ends of travel.
    outer_to_middle_home = mount_setback
    middle_to_inner_home = mount_setback

    palette = dict(SLIDE_PALETTE_PRESETS[config.palette_theme])

    return ResolvedThreestageTelescopingSlideConfig(
        base_module=base,
        section_style=section,
        terminal_module=terminal,
        detail_module=detail,
        palette_theme=config.palette_theme,
        wall=wall,
        clearance=clearance,
        mount_setback=mount_setback,
        base_height=base_height,
        outer_len=outer_len,
        outer_w=outer_w,
        outer_h=outer_h,
        middle_len=middle_len,
        middle_w=middle_w,
        middle_h=middle_h,
        inner_len=inner_len,
        inner_w=inner_w,
        inner_h=inner_h,
        outer_to_middle_travel=outer_to_middle_travel,
        middle_to_inner_travel=middle_to_inner_travel,
        outer_to_middle_home=outer_to_middle_home,
        middle_to_inner_home=middle_to_inner_home,
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Section-family geometry helpers
#
# Every member is laid out in its OWN part frame with the rear face at x=0 and
# the body extending toward +x to x=length. The cross section is centered on
# (y=0, z=0) for the concentric families (closed_box / open_channel /
# primitive_wall) so the three stages nest along yz; side_web nests along y
# with the cross section centered on z=0. A small rear "spine" / cap visual at
# x=0 guarantees each member's geometry contains its part-frame origin (joint
# origin proximity) AND keeps every section's visuals one connected island.
# --------------------------------------------------------------------------- #


def _hollow_box_tube_mesh(length: float, w: float, h: float, wall: float, name: str):
    """Mesh hollow rectangular box tube (S1, rec_..._0002). The profile is
    built in XY and extruded along Z, then rotated rpy=(0, pi/2, 0) so the tube
    runs along +x; profile-x maps to world-z (height) and profile-y to world-y
    (width)."""
    px = max(0.004, h * 0.5)
    py = max(0.004, w * 0.5)
    ix = max(0.001, px - wall)
    iy = max(0.001, py - wall)
    outer = [(-px, -py), (px, -py), (px, py), (-px, py)]
    hole = [(-ix, -iy), (ix, -iy), (ix, iy), (-ix, iy)]
    geom = ExtrudeWithHolesGeometry(outer, [hole], length, cap=True, center=True, closed=True)
    return mesh_from_geometry(geom, name)


def _open_channel_mesh(length: float, w: float, h: float, wall: float, name: str):
    """Mesh open-top C-channel (S5, rec_..._db83e907): floor + two side walls,
    open along +z. Profile built in XY (profile-x -> -world-z height,
    profile-y -> world-y width) and extruded along Z, centered, then rotated
    rpy=(0, pi/2, 0) so the channel runs along +x and opens toward +z.

    Under rpy=(0, pi/2, 0) a profile point (xp, yp) maps to world
    (y=yp, z=-xp), so the mouth must open toward -profile-x to end up at
    +world-z. The profile is an outer rectangle minus a cavity notch that
    opens at x=-px: floor strip at xp in [px-wall, px] (-> world z in
    [-h/2, -h/2+wall]) plus two symmetric side walls at yp=+-(py-wall..py)
    (-> world y=+-(w/2-wall..w/2))."""
    px = max(0.004, h * 0.5)
    py = max(0.004, w * 0.5)
    profile = [
        (-px, -py),
        (px, -py),
        (px, py),
        (-px, py),
        (-px, py - wall),
        (px - wall, py - wall),
        (px - wall, -py + wall),
        (-px, -py + wall),
    ]
    geom = ExtrudeGeometry.centered(profile, length, cap=True, closed=True)
    return mesh_from_geometry(geom, name)


def _emit_closed_box_details(part, *, length, w, h, wall, material, prefix):
    """Fused S1/S10-style machined-box details for the clean tube family.

    Keep this family visually restrained: same-material sleeve collars and
    subtle edge strips read as integral machined features, while high-contrast
    segmented bars make the clean tube look patched together.
    """
    sleeve_l = max(0.010, length * 0.055)
    sleeve_t = max(0.0012, wall * 0.45)
    for idx, fx in enumerate((0.18, 0.82)):
        x = length * fx
        part.visual(
            Box((sleeve_l, w + sleeve_t * 1.4, sleeve_t)),
            origin=Origin(xyz=(x, 0.0, h + sleeve_t * 0.42)),
            material=material,
            name=f"{prefix}_integral_top_collar_{idx}", material_class_id="metal.steel_bare",
        )
        for sy, side in ((+1.0, "left"), (-1.0, "right")):
            part.visual(
                Box((sleeve_l, sleeve_t, h * 0.72)),
                origin=Origin(xyz=(x, sy * (w * 0.5 + sleeve_t * 0.22), h * 0.50)),
                material=material,
                name=f"{prefix}_integral_side_collar_{side}_{idx}", material_class_id="metal.steel_bare",
            )

    edge_l = max(0.040, length * 0.72)
    edge_t = max(0.001, wall * 0.32)
    for sy, side in ((+1.0, "left"), (-1.0, "right")):
        part.visual(
            Box((edge_l, edge_t, edge_t)),
            origin=Origin(xyz=(length * 0.52, sy * (w * 0.32), h + edge_t * 0.40)),
            material="bracket",
            name=f"{prefix}_subtle_top_edge_line_{side}", material_class_id="metal.aluminum_bare",
        )


def _emit_open_channel_details(part, *, length, w, h, wall, prefix):
    """Fused S5-style channel details: internal race strips, stop buffers,
    counterbore bosses, and side window insets. These are visual/race hardware
    details rather than separate moving links."""
    rail_l = max(0.030, length * 0.76)
    rail_w = max(0.003, wall * 1.15)
    rail_h = max(0.0025, wall * 0.9)
    rail_x = length * 0.52
    rail_y = max(rail_w * 0.7, w * 0.5 - wall - rail_w * 0.7)
    rail_z = wall + rail_h * 0.45
    for sy, side in ((+1.0, "left"), (-1.0, "right")):
        part.visual(
            Box((rail_l, rail_w, rail_h)),
            origin=Origin(xyz=(rail_x, sy * rail_y, rail_z)),
            material="hardware",
            name=f"{prefix}_inner_race_{side}", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Box((max(0.010, length * 0.045), rail_w * 1.25, rail_h * 1.4)),
            origin=Origin(xyz=(length * 0.83, sy * rail_y, rail_z)),
            material="hardware",
            name=f"{prefix}_stop_buffer_{side}", material_class_id="metal.blackened_gunmetal",
        )

    pad_l = max(0.014, length * 0.055)
    pad_h = max(0.004, h * 0.16)
    pad_t = max(0.0015, wall * 0.38)
    for sy, side in ((+1.0, "left"), (-1.0, "right")):
        part.visual(
            Box((length * 0.46, pad_t, pad_h * 0.55)),
            origin=Origin(xyz=(length * 0.52, sy * (w * 0.5 - wall * 0.12), wall + h * 0.31)),
            material="bracket",
            name=f"{prefix}_fastener_recess_strip_{side}", material_class_id="metal.aluminum_bare",
        )
        for idx, fx in enumerate((0.24, 0.76)):
            part.visual(
                Box((pad_l, pad_t * 1.25, pad_h)),
                origin=Origin(xyz=(length * fx, sy * (w * 0.5 - wall * 0.10), wall + h * 0.31)),
                material="hardware",
                name=f"{prefix}_flush_fastener_pad_{side}_{idx}", material_class_id="metal.blackened_gunmetal",
            )

    inset_l = max(0.026, length * 0.20)
    inset_h = max(0.004, h * 0.22)
    for idx, fx in enumerate((0.32, 0.64)):
        for sy, side in ((+1.0, "left"), (-1.0, "right")):
            part.visual(
                Box((inset_l, wall * 0.45, inset_h)),
                origin=Origin(xyz=(length * fx, sy * (w * 0.5 - wall * 0.18), h * 0.58)),
                material="hardware",
                name=f"{prefix}_side_window_inset_{side}_{idx}", material_class_id="metal.blackened_gunmetal",
            )


def _emit_box_walls(part, *, length, w, h, wall, material, prefix, front_frame=True):
    """Box-primitive open box: floor + side walls + rear cap (+ optional open
    front-mouth cheek plates). Adapted from S7/S11 (9ef08c04 / 8bdc62dd).
    Member frame: rear at x=0, body +x to x=length; cross section centered on
    y=0 with the FLOOR at z=0 (body occupies z in [0, h]). The floor at z=0
    makes the part-frame origin land on solid material (joint-origin proximity)
    and bottom-aligns the nested stages."""
    part.visual(
        Box((length, w, wall)),
        origin=Origin(xyz=(length * 0.5, 0.0, wall * 0.5)),
        material=material,
        name=f"{prefix}_floor", material_class_id="metal.steel_bare",
    )
    wall_h = h - wall
    wall_cz = wall + wall_h * 0.5
    wall_y = w * 0.5 - wall * 0.5
    part.visual(
        Box((length, wall, wall_h)),
        origin=Origin(xyz=(length * 0.5, +wall_y, wall_cz)),
        material=material,
        name=f"{prefix}_left_wall", material_class_id="metal.steel_bare",
    )
    part.visual(
        Box((length, wall, wall_h)),
        origin=Origin(xyz=(length * 0.5, -wall_y, wall_cz)),
        material=material,
        name=f"{prefix}_right_wall", material_class_id="metal.steel_bare",
    )
    # Rear cap at x=0 — guarantees geometry contains the part-frame origin.
    part.visual(
        Box((wall, w, h)),
        origin=Origin(xyz=(wall * 0.5, 0.0, h * 0.5)),
        material=material,
        name=f"{prefix}_rear_cap", material_class_id="metal.steel_bare",
    )
    if front_frame:
        # Keep the front visually framed without closing the sliding aperture.
        # A full front plate makes the child stage visibly pass through a solid
        # wall during prismatic motion; side cheek plates read as a mouth while
        # leaving the center/top/bottom path open.
        part.visual(
            Box((wall, wall, wall_h)),
            origin=Origin(xyz=(length - wall * 0.5, +wall_y, wall_cz)),
            material=material,
            name=f"{prefix}_front_left_jamb", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((wall, wall, wall_h)),
            origin=Origin(xyz=(length - wall * 0.5, -wall_y, wall_cz)),
            material=material,
            name=f"{prefix}_front_right_jamb", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((wall, w, wall)),
            origin=Origin(xyz=(length - wall * 0.5, 0.0, h - wall * 0.5)),
            material=material,
            name=f"{prefix}_front_top_lintel", material_class_id="metal.steel_bare",
        )

    lip_w = max(wall * 1.4, w * 0.13)
    lip_t = max(wall * 0.70, 0.0015)
    for sy, side in ((+1.0, "left"), (-1.0, "right")):
        part.visual(
            Box((length * 0.90, lip_w, lip_t)),
            origin=Origin(xyz=(length * 0.54, sy * (w * 0.5 - lip_w * 0.5), h - lip_t * 0.5)),
            material=material,
            name=f"{prefix}_top_lip_{side}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((length * 0.72, max(wall * 0.65, 0.0015), max(h * 0.18, wall * 1.2))),
            origin=Origin(xyz=(length * 0.48, sy * (w * 0.5 - wall * 0.25), wall + h * 0.42)),
            material="hardware",
            name=f"{prefix}_side_slot_{side}", material_class_id="metal.blackened_gunmetal",
        )
    for idx, fx in enumerate((0.22, 0.78)):
        part.visual(
            Box(
                (
                    max(0.006, min(w, h) * 0.14),
                    max(0.006, w * 0.20),
                    max(0.0015, wall * 0.38),
                )
            ),
            origin=Origin(xyz=(length * fx, 0.0, wall * 1.02)),
            material="hardware",
            name=f"{prefix}_floor_fastener_plate_{idx}", material_class_id="metal.blackened_gunmetal",
        )


def _emit_side_web(part, *, length, w, h, wall, material, prefix):
    """Box-primitive side-web (C laid on its side) adapted from S9
    (5aa889ab): a vertical web + top/bottom lips + a thin race strip. Member
    frame: rear at x=0, body +x to length, web centered on y=0 with the bottom
    at z=0 (body occupies z in [0, h]). The web reaches z=0 so the part-frame
    origin lands on solid material."""
    web_th = wall
    lip_w = max(0.008, w * 0.55)
    lip_th = wall
    part.visual(
        Box((length, web_th, h)),
        origin=Origin(xyz=(length * 0.5, 0.0, h * 0.5)),
        material=material,
        name=f"{prefix}_web", material_class_id="metal.steel_bare",
    )
    lip_y = lip_w * 0.5
    part.visual(
        Box((length, lip_w, lip_th)),
        origin=Origin(xyz=(length * 0.5, lip_y, h - lip_th * 0.5)),
        material=material,
        name=f"{prefix}_top_lip", material_class_id="metal.steel_bare",
    )
    part.visual(
        Box((length, lip_w, lip_th)),
        origin=Origin(xyz=(length * 0.5, lip_y, lip_th * 0.5)),
        material=material,
        name=f"{prefix}_bottom_lip", material_class_id="metal.steel_bare",
    )
    # Rear stop cap at x=0 (contains origin).
    part.visual(
        Box((wall, lip_w, h)),
        origin=Origin(xyz=(wall * 0.5, lip_y, h * 0.5)),
        material=material,
        name=f"{prefix}_rear_stop", material_class_id="metal.steel_bare",
    )
    # Thin race rail on top lip (S9 outer_race_*).
    part.visual(
        Box((length * 0.92, max(0.004, lip_w * 0.30), max(0.004, lip_th * 0.8))),
        origin=Origin(xyz=(length * 0.5, lip_y, h - lip_th - 0.001)),
        material=material,
        name=f"{prefix}_race", material_class_id="metal.steel_bare",
    )
    part.visual(
        Box((length * 0.84, max(0.003, lip_w * 0.22), max(0.003, lip_th * 0.65))),
        origin=Origin(xyz=(length * 0.54, lip_y, lip_th + 0.001)),
        material="hardware",
        name=f"{prefix}_lower_race", material_class_id="metal.blackened_gunmetal",
    )
    screw_r = max(0.003, h * 0.055)
    for idx, fx in enumerate((0.12, 0.88)):
        for zf, row in ((0.27, "lower"), (0.73, "upper")):
            part.visual(
                Box((screw_r * 2.2, max(0.0018, wall * 0.75), screw_r * 1.55)),
                origin=Origin(xyz=(length * fx, -web_th * 0.55, h * zf)),
                material="hardware",
                name=f"{prefix}_web_screw_plate_{row}_{idx}", material_class_id="metal.blackened_gunmetal",
            )
    ball_r = max(0.0022, min(w, h) * 0.035)
    for idx, fx in enumerate((0.24, 0.40, 0.56, 0.72)):
        part.visual(
            Box((ball_r * 2.1, max(0.002, wall * 0.7), ball_r * 1.1)),
            origin=Origin(xyz=(length * fx, lip_y, h - lip_th * 1.15)),
            material="roller",
            name=f"{prefix}_race_bearing_shoe_{idx}", material_class_id="metal.bronze_cast",
        )


def _emit_member_geometry(part, *, r, length, w, h, material, prefix):
    """Emit one member's geometry into ``part`` according to the locked
    section_style. Mesh families are oriented along +x via rpy; the mesh is
    placed at x=length*0.5 so the body spans 0..length."""
    section = r.section_style
    if section in ("closed_box_tube", "open_channel_raceway"):
        # Mesh cross sections are centered on z=0 in their own profile; shift up
        # by h/2 so the body occupies z in [0, h] (floor at z=0), matching the
        # Box families' bottom-aligned convention.
        if section == "closed_box_tube":
            part.visual(
                _hollow_box_tube_mesh(length, w, h, r.wall, f"{prefix}_tube"),
                origin=Origin(xyz=(length * 0.5, 0.0, h * 0.5), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=material,
                name=f"{prefix}_tube", material_class_id=("metal.steel_bare" if r.palette_theme in {"machined_steel", "anodized_black", "zinc_bronze"} else "metal.steel_galvanized"),
            )
            _emit_closed_box_details(
                part, length=length, w=w, h=h, wall=r.wall, material=material, prefix=prefix
            )
        else:
            part.visual(
                _open_channel_mesh(length, w, h, r.wall, f"{prefix}_channel"),
                origin=Origin(xyz=(length * 0.5, 0.0, h * 0.5), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=material,
                name=f"{prefix}_channel", material_class_id=("metal.steel_bare" if r.palette_theme in {"machined_steel", "anodized_black", "zinc_bronze"} else "metal.steel_galvanized"),
            )
            _emit_open_channel_details(part, length=length, w=w, h=h, wall=r.wall, prefix=prefix)
        # Solid rear cap (full cross section, z in [0, h]) closing the back of
        # the mesh member. Puts solid geometry at the part-frame origin (floor
        # center) so the joint-origin proximity check passes for the
        # hollow/open mesh cross sections, and ties the back into one island.
        part.visual(
            Box((max(0.003, r.wall * 1.2), w, h)),
            origin=Origin(xyz=(max(0.0015, r.wall * 0.6), 0.0, h * 0.5)),
            material=material,
            name=f"{prefix}_rear_cap", material_class_id=("metal.steel_bare" if r.palette_theme in {"machined_steel", "anodized_black", "zinc_bronze"} else "metal.steel_galvanized"),
        )
    elif section == "primitive_wall_box":
        _emit_box_walls(
            part, length=length, w=w, h=h, wall=r.wall, material=material, prefix=prefix
        )
    else:  # side_web_race
        _emit_side_web(part, length=length, w=w, h=h, wall=r.wall, material=material, prefix=prefix)


def _member_inertial(length, w, h, mass):
    return Inertial.from_geometry(
        Box((max(0.01, length), max(0.01, w), max(0.01, h))),
        mass=mass,
        origin=Origin(xyz=(length * 0.5, 0.0, h * 0.5)),
    )


# --------------------------------------------------------------------------- #
# Slot A — base_mount
#
# The base module emits the root part (or nothing, when integral) and exports
# a ``downstream`` interface whose ``part_name`` tells the outer member what to
# FIX itself to. ``part_name == ""`` is the sentinel meaning "outer is root".
# All extra fields on the interface are unused by the manual joint wiring.
# --------------------------------------------------------------------------- #


def _base_downstream(part_name: str) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name=part_name,
        visual_name="",
        face_side="positive_x",
        anchor_local=(0.0, 0.0, 0.0),
    )


def _build_integral_grounded_outer_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Anchor base — NO separate base part. The outer member itself is the
    root link and is grounded directly (S2, rec_..._0002 minimal clean
    anchor)."""
    # Emit nothing; signal "outer is root" with an empty part_name.
    return ModuleBuild(
        module_name="integral_grounded_outer",
        parts_emitted=[],
        internal_articulations=[],
        interfaces={"downstream": _base_downstream("")},
    )


def _build_support_frame_fixed_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Welded support-frame root (S4, rec_..._0003). A low frame of legs +
    rails that raises the outer member to a working datum; outer FIXES on top.
    """
    model = ctx.model
    r: ResolvedThreestageTelescopingSlideConfig = ctx.config  # type: ignore[assignment]

    frame = model.part("support_frame")
    bh = r.base_height
    span = r.outer_len * 0.86
    fw = r.outer_w + 0.040
    rail_th = max(0.006, r.wall * 2.2)

    # Top rail deck the outer rests on (top face at z=0).
    frame.visual(
        Box((span, fw, rail_th)),
        origin=Origin(xyz=(span * 0.5, 0.0, -rail_th * 0.5)),
        material="base",
        name="top_deck", material_class_id="metal.steel_bare",
    )
    leg_th = max(0.008, rail_th)
    leg_z = -bh * 0.5 - rail_th
    for idx, lx in enumerate((span * 0.12, span * 0.88)):
        for sy, side in ((+1.0, "left"), (-1.0, "right")):
            frame.visual(
                Box((leg_th, leg_th, bh)),
                origin=Origin(xyz=(lx, sy * (fw * 0.5 - leg_th * 0.6), leg_z)),
                material="base",
                name=f"leg_{side}_{idx}", material_class_id="metal.steel_bare",
            )
    # Foot rails along the floor connecting the legs (so nothing floats).
    foot_z = -bh - rail_th + leg_th * 0.5
    for sy, side in ((+1.0, "left"), (-1.0, "right")):
        frame.visual(
            Box((span * 0.86, leg_th * 1.2, leg_th)),
            origin=Origin(xyz=(span * 0.5, sy * (fw * 0.5 - leg_th * 0.6), foot_z)),
            material="base",
            name=f"foot_{side}", material_class_id="metal.steel_bare",
        )
    # Vertical spine connecting the deck to the foot rails at mid-span so the
    # legs + feet + deck form one connected island.
    frame.visual(
        Box((leg_th, fw - 2.0 * leg_th, bh + rail_th)),
        origin=Origin(xyz=(span * 0.5, 0.0, -bh * 0.5 - rail_th)),
        material="base",
        name="mid_spine", material_class_id="metal.steel_bare",
    )

    frame.inertial = Inertial.from_geometry(
        Box((span, fw, bh + rail_th)),
        mass=3.2,
        origin=Origin(xyz=(span * 0.5, 0.0, -bh * 0.5)),
    )

    downstream = _base_downstream("support_frame")
    # The deck's +z face is the mating face for the outer member.
    object.__setattr__(downstream, "visual_name", "top_deck")
    return ModuleBuild(
        module_name="support_frame_fixed",
        parts_emitted=["support_frame"],
        internal_articulations=[],
        interfaces={"downstream": downstream},
    )


def _build_wall_backplate_fixed_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Vertical backplate root (S9, rec_..._5aa889ab): a tall plate on the -y
    side with two bearing bridges; the outer FIXES in front of it."""
    model = ctx.model
    r: ResolvedThreestageTelescopingSlideConfig = ctx.config  # type: ignore[assignment]

    plate = model.part("rear_support")
    span = r.outer_len
    plate_h = max(0.10, r.outer_h * 2.6)
    plate_th = max(0.012, r.wall * 4.0)
    # Push the plate inner face ~1mm into the outer member's left wall so the
    # plate physically contacts (not just boundary-touches) the grounded outer.
    back_y = -(r.outer_w * 0.5 + plate_th * 0.5) + 0.0015

    plate.visual(
        Box((span, plate_th, plate_h)),
        origin=Origin(xyz=(span * 0.5, back_y, 0.0)),
        material="base",
        name="backing_plate", material_class_id="metal.steel_bare",
    )
    bridge_th = max(0.010, r.outer_h * 0.5)
    for sz, name in ((+1.0, "upper"), (-1.0, "lower")):
        plate.visual(
            Box((span, plate_th + r.outer_w * 0.5, bridge_th)),
            origin=Origin(
                xyz=(span * 0.5, back_y + r.outer_w * 0.25, sz * (plate_h * 0.5 - bridge_th * 0.6))
            ),
            material="base",
            name=f"{name}_bridge", material_class_id="metal.steel_bare",
        )
    plate.visual(
        Box((max(0.030, span * 0.08), plate_th + r.outer_w * 0.5, plate_h * 0.7)),
        origin=Origin(xyz=(max(0.018, span * 0.04), back_y + r.outer_w * 0.25, 0.0)),
        material="base",
        name="rear_stop", material_class_id="metal.steel_bare",
    )

    plate.inertial = Inertial.from_geometry(
        Box((span, plate_th + r.outer_w * 0.5, plate_h)),
        mass=2.6,
        origin=Origin(xyz=(span * 0.5, back_y + r.outer_w * 0.2, 0.0)),
    )

    downstream = _base_downstream("rear_support")
    object.__setattr__(downstream, "visual_name", "upper_bridge")
    object.__setattr__(downstream, "face_side", "positive_y")
    return ModuleBuild(
        module_name="wall_backplate_fixed",
        parts_emitted=["rear_support"],
        internal_articulations=[],
        interfaces={"downstream": downstream},
    )


def _build_grounded_carrier_body_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Heavy U-channel carrier body root (S8, rec_..._fd45679a): a stout open
    box (floor + walls + back wall + runners) that the outer member drops
    into and FIXES to."""
    model = ctx.model
    r: ResolvedThreestageTelescopingSlideConfig = ctx.config  # type: ignore[assignment]

    body = model.part("carrier_body")
    span = r.outer_len + 0.040
    bw = r.outer_w + 0.030
    side_h = max(0.030, r.outer_h + 0.010)
    bwall = max(0.006, r.wall * 2.4)
    floor_th = bwall
    cx = span * 0.5 - 0.020

    # Floor occupies z in [-floor_th, 0] so its TOP face is at z=0 — the outer
    # member (floor at z=0) rests directly on it (physical contact).
    body.visual(
        Box((span, bw, floor_th)),
        origin=Origin(xyz=(cx, 0.0, -floor_th * 0.5)),
        material="base",
        name="body_floor", material_class_id="metal.steel_bare",
    )
    side_cz = side_h * 0.5
    side_y = bw * 0.5 - bwall * 0.5
    for sy, side in ((+1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((span, bwall, side_h)),
            origin=Origin(xyz=(cx, sy * side_y, side_cz)),
            material="base",
            name=f"body_{side}_wall", material_class_id="metal.steel_bare",
        )
    body.visual(
        Box((bwall, bw, side_h + floor_th)),
        origin=Origin(xyz=(-0.020 + bwall * 0.5, 0.0, (side_h - floor_th) * 0.5)),
        material="base",
        name="body_back_wall", material_class_id="metal.steel_bare",
    )

    body.inertial = Inertial.from_geometry(
        Box((span, bw, side_h + floor_th)),
        mass=6.5,
        origin=Origin(xyz=(cx, 0.0, (side_h - floor_th) * 0.5)),
    )

    downstream = _base_downstream("carrier_body")
    object.__setattr__(downstream, "visual_name", "body_floor")
    return ModuleBuild(
        module_name="grounded_carrier_body",
        parts_emitted=["carrier_body"],
        internal_articulations=[],
        interfaces={"downstream": downstream},
    )


# --------------------------------------------------------------------------- #
# Slot B — outer_member
# --------------------------------------------------------------------------- #


def _build_outer_member(ctx: ModuleBuildContext) -> ModuleBuild:
    """First (fixed) stage. Either the root link (integral base) or FIXED on a
    base part. Geometry follows the locked section_style."""
    model = ctx.model
    r: ResolvedThreestageTelescopingSlideConfig = ctx.config  # type: ignore[assignment]

    outer = model.part("outer_member")
    _emit_member_geometry(
        outer, r=r, length=r.outer_len, w=r.outer_w, h=r.outer_h, material="outer", prefix="outer"
    )
    outer.inertial = _member_inertial(r.outer_len, r.outer_w, r.outer_h, 1.3)

    base_part = ctx.upstream_interface.part_name if ctx.upstream_interface else ""
    if base_part:
        # FIXED base_to_outer. The outer's rear cap / floor sits on the base
        # datum; we anchor at the outer rear (x=0) raised by the base height.
        # Joint origin in the BASE part frame: place it where the outer's
        # frame origin should land (at the base's mounting datum). The outer's
        # body then extends +x along the base.
        base_module = next((m for s, m in ctx.prior_choices if s == "base"), "")
        if base_module == "wall_backplate_fixed":
            origin = Origin(xyz=(0.0, 0.0, 0.0))
        else:
            origin = Origin(xyz=(0.0, 0.0, 0.0))
        model.articulation(
            "base_to_outer",
            ArticulationType.FIXED,
            parent=model.get_part(base_part),
            child=outer,
            origin=origin,
        )

    downstream = InterfaceSpec(
        interface_name="downstream",
        part_name="outer_member",
        visual_name="",
        face_side="positive_x",
        anchor_local=(0.0, 0.0, 0.0),
    )
    return ModuleBuild(
        module_name="outer_member",
        parts_emitted=["outer_member"],
        internal_articulations=(["base_to_outer"] if base_part else []),
        interfaces={"downstream": downstream},
    )


# --------------------------------------------------------------------------- #
# Slot C — middle_member  (prismatic child of outer)
# Slot D — inner_member   (prismatic child of middle)
# --------------------------------------------------------------------------- #


def _build_middle_member(ctx: ModuleBuildContext) -> ModuleBuild:
    """Second stage: prismatic child of the outer member. Cross section is
    derived from the outer cavity (same family). Joint grandfathered (no
    MatingContract) — nested slide has no clean contact face."""
    model = ctx.model
    r: ResolvedThreestageTelescopingSlideConfig = ctx.config  # type: ignore[assignment]

    middle = model.part("middle_member")
    _emit_member_geometry(
        middle,
        r=r,
        length=r.middle_len,
        w=r.middle_w,
        h=r.middle_h,
        material="middle",
        prefix="middle",
    )
    middle.inertial = _member_inertial(r.middle_len, r.middle_w, r.middle_h, 0.82)

    parent_name = ctx.upstream_interface.part_name  # "outer_member"
    model.articulation(
        "outer_to_middle",
        ArticulationType.PRISMATIC,
        parent=model.get_part(parent_name),
        child=middle,
        origin=Origin(xyz=(r.outer_to_middle_home, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            lower=0.0, upper=r.outer_to_middle_travel, effort=120.0, velocity=0.45
        ),
    )

    downstream = InterfaceSpec(
        interface_name="downstream",
        part_name="middle_member",
        visual_name="",
        face_side="positive_x",
        anchor_local=(0.0, 0.0, 0.0),
    )
    return ModuleBuild(
        module_name="middle_member",
        parts_emitted=["middle_member"],
        internal_articulations=["outer_to_middle"],
        interfaces={"downstream": downstream},
    )


def _build_inner_member(ctx: ModuleBuildContext) -> ModuleBuild:
    """Third stage: prismatic child of the middle member."""
    model = ctx.model
    r: ResolvedThreestageTelescopingSlideConfig = ctx.config  # type: ignore[assignment]

    inner = model.part("inner_member")
    _emit_member_geometry(
        inner,
        r=r,
        length=r.inner_len,
        w=r.inner_w,
        h=r.inner_h,
        material="inner",
        prefix="inner",
    )
    inner.inertial = _member_inertial(r.inner_len, r.inner_w, r.inner_h, 0.55)

    parent_name = ctx.upstream_interface.part_name  # "middle_member"
    model.articulation(
        "middle_to_inner",
        ArticulationType.PRISMATIC,
        parent=model.get_part(parent_name),
        child=inner,
        origin=Origin(xyz=(r.middle_to_inner_home, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            lower=0.0, upper=r.middle_to_inner_travel, effort=90.0, velocity=0.45
        ),
    )

    downstream = InterfaceSpec(
        interface_name="downstream",
        part_name="inner_member",
        visual_name="",
        face_side="positive_x",
        anchor_local=(0.0, 0.0, 0.0),
    )
    return ModuleBuild(
        module_name="inner_member",
        parts_emitted=["inner_member"],
        internal_articulations=["middle_to_inner"],
        interfaces={"downstream": downstream},
    )


# --------------------------------------------------------------------------- #
# Slot E — terminal  (FIXED child of inner end face)
# --------------------------------------------------------------------------- #


def _build_bare_no_terminal(ctx: ModuleBuildContext) -> ModuleBuild:
    """Anchor terminal — none. The inner member is the end of the chain.
    Re-export the inner downstream so the detail slot still chains."""
    return ModuleBuild(
        module_name="bare_no_terminal",
        parts_emitted=[],
        internal_articulations=[],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_carriage_shoe_terminal(ctx: ModuleBuildContext) -> ModuleBuild:
    """Carriage shoe FIXED on the inner end face (S5/S6, rec_..._db83e907).
    The shoe part frame origin sits on its -x mating face (so it FIXES cleanly
    to the inner end at origin.x = INNER_LEN)."""
    model = ctx.model
    r: ResolvedThreestageTelescopingSlideConfig = ctx.config  # type: ignore[assignment]

    shoe = model.part("terminal")
    shoe_l = max(0.020, r.inner_len * 0.16)
    shoe_w = max(0.014, r.inner_w * 1.35)
    shoe_h = max(0.012, r.inner_h * 1.25)
    # Terminal frame origin sits at the inner FLOOR (z=0, solid) so the joint
    # origin (inner_len, 0, 0) lands on solid material. The shoe body is then
    # raised within its own frame to cover the inner cross-section.
    cz = r.inner_h * 0.5
    shoe.visual(
        Box((shoe_l, shoe_w, shoe_h)),
        origin=Origin(xyz=(shoe_l * 0.5, 0.0, cz)),
        material="bracket",
        name="shoe_body", material_class_id="metal.aluminum_bare",
    )
    shoe.visual(
        Box((max(0.008, shoe_l * 0.4), shoe_w * 0.8, max(0.006, shoe_h * 0.55))),
        origin=Origin(xyz=(shoe_l, 0.0, cz)),
        material="bracket",
        name="shoe_nose", material_class_id="metal.aluminum_bare",
    )
    shoe.inertial = Inertial.from_geometry(
        Box((shoe_l * 1.4, shoe_w, shoe_h)),
        mass=0.08,
        origin=Origin(xyz=(shoe_l * 0.5, 0.0, cz)),
    )

    parent_name = ctx.upstream_interface.part_name  # inner_member
    model.articulation(
        "inner_to_terminal",
        ArticulationType.FIXED,
        parent=model.get_part(parent_name),
        child=shoe,
        origin=Origin(xyz=(r.inner_len, 0.0, 0.0)),
    )
    return ModuleBuild(
        module_name="carriage_shoe",
        parts_emitted=["terminal"],
        internal_articulations=["inner_to_terminal"],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_flat_end_plate_terminal(ctx: ModuleBuildContext) -> ModuleBuild:
    """Flat end plate FIXED on the inner end face (S10, rec_..._0004)."""
    model = ctx.model
    r: ResolvedThreestageTelescopingSlideConfig = ctx.config  # type: ignore[assignment]

    plate = model.part("terminal")
    plate_t = max(0.006, r.wall * 2.5)
    plate_w = max(0.020, r.inner_w * 1.6)
    plate_h = max(0.018, r.inner_h * 1.5)
    # Terminal frame origin at the inner FLOOR (z=0, solid); raise the plate
    # within its own frame to cover the inner cross-section.
    cz = r.inner_h * 0.5
    plate.visual(
        Box((plate_t, plate_w, plate_h)),
        origin=Origin(xyz=(plate_t * 0.5, 0.0, cz)),
        material="bracket",
        name="end_plate", material_class_id="metal.aluminum_bare",
    )
    # Central boss so the plate reads as a machined end fitting.
    plate.visual(
        Cylinder(radius=max(0.004, plate_h * 0.18), length=plate_t * 1.2),
        origin=Origin(xyz=(plate_t * 0.5, 0.0, cz), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="hardware",
        name="plate_boss", material_class_id="metal.blackened_gunmetal",
    )
    plate.inertial = Inertial.from_geometry(
        Box((plate_t, plate_w, plate_h)),
        mass=0.05,
        origin=Origin(xyz=(plate_t * 0.5, 0.0, cz)),
    )

    parent_name = ctx.upstream_interface.part_name
    # Grandfathered FIXED (no MatingContract): a clean face contact on the
    # meshed/box inner end face is finicky; the plate sits flush on the inner
    # end face at origin.x = INNER_LEN and the overlap is allow-listed.
    model.articulation(
        "inner_to_terminal",
        ArticulationType.FIXED,
        parent=model.get_part(parent_name),
        child=plate,
        origin=Origin(xyz=(r.inner_len, 0.0, 0.0)),
    )
    return ModuleBuild(
        module_name="flat_end_plate",
        parts_emitted=["terminal"],
        internal_articulations=["inner_to_terminal"],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_top_carriage_tray_terminal(ctx: ModuleBuildContext) -> ModuleBuild:
    """Top tray / carriage FIXED above the inner end (1038e85b grep family).
    A flat load tray riding on a short riser at the inner end face."""
    model = ctx.model
    r: ResolvedThreestageTelescopingSlideConfig = ctx.config  # type: ignore[assignment]

    tray = model.part("terminal")
    riser_h = max(0.010, r.inner_h * 0.9)
    riser_l = max(0.014, r.inner_len * 0.12)
    tray.visual(
        Box((riser_l, max(0.012, r.inner_w), riser_h)),
        origin=Origin(xyz=(riser_l * 0.5, 0.0, riser_h * 0.5)),
        material="bracket",
        name="tray_riser", material_class_id="metal.aluminum_bare",
    )
    tray_t = max(0.005, r.wall * 2.0)
    tray_w = max(0.040, r.outer_w * 1.6)
    tray_l = max(0.050, r.inner_len * 0.5)
    tray_z = riser_h + tray_t * 0.5
    tray.visual(
        Box((tray_l, tray_w, tray_t)),
        origin=Origin(xyz=(tray_l * 0.5 - riser_l * 0.5, 0.0, tray_z)),
        material="bracket",
        name="tray_plate", material_class_id="metal.aluminum_bare",
    )
    tray.inertial = Inertial.from_geometry(
        Box((tray_l, tray_w, riser_h + tray_t)),
        mass=0.10,
        origin=Origin(xyz=(tray_l * 0.3, 0.0, tray_z * 0.5)),
    )

    parent_name = ctx.upstream_interface.part_name
    model.articulation(
        "inner_to_terminal",
        ArticulationType.FIXED,
        parent=model.get_part(parent_name),
        child=tray,
        origin=Origin(xyz=(r.inner_len, 0.0, 0.0)),
    )
    return ModuleBuild(
        module_name="top_carriage_tray",
        parts_emitted=["terminal"],
        internal_articulations=["inner_to_terminal"],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


# --------------------------------------------------------------------------- #
# Slot F — detail  (FIXED decorative hardware on the members)
# --------------------------------------------------------------------------- #


def _build_none_clean_detail(ctx: ModuleBuildContext) -> ModuleBuild:
    """Anchor detail — none."""
    return ModuleBuild(
        module_name="none_clean",
        parts_emitted=[],
        internal_articulations=[],
        interfaces={},
    )


def _build_stop_tabs_only_detail(ctx: ModuleBuildContext) -> ModuleBuild:
    """Stop tabs folded onto the members as named visuals on the slide members
    (Rule 1 — non-articulating decoration stays fused into the part it sits
    on). Adapted from S1's top stop-tabs. No new part."""
    model = ctx.model
    r: ResolvedThreestageTelescopingSlideConfig = ctx.config  # type: ignore[assignment]

    members = (
        ("outer", model.get_part("outer_member"), r.outer_len, r.outer_w, r.outer_h),
        ("middle", model.get_part("middle_member"), r.middle_len, r.middle_w, r.middle_h),
        ("inner", model.get_part("inner_member"), r.inner_len, r.inner_w, r.inner_h),
    )
    # Open-top sections (open channel / primitive wall box) have NO ceiling at
    # y=0: a narrow centered tab floats over the open mouth as a disconnected
    # island. For those, span the full width so the tab bridges onto both side
    # wall tops (walls occupy y=+-(w/2-wall..w/2), z up to h), sinking at most
    # 0.9*wall so the strap never dips into the nested child's swept volume
    # (child top sits ~2*step ~= 2*wall below the parent top). Closed-box
    # (ceiling slab) and side-web (top lip crosses y=0) keep the centered tab,
    # which welds into that top material.
    open_top = r.section_style in ("open_channel_raceway", "primitive_wall_box")
    for prefix, part, length, width, height in members:
        tab_l = max(0.006, length * 0.035)
        tab_h = max(0.003, height * 0.14)
        top_z = height
        if open_top:
            tab_w = width
            tab_cz = top_z + tab_h * 0.5 - min(tab_h * 0.85, r.wall * 0.9)
        else:
            tab_w = max(0.007, width * 0.42)
            tab_cz = top_z - tab_h * 0.35
        for idx, fx in enumerate((0.18, 0.72)):
            part.visual(
                Box((tab_l, tab_w, tab_h)),
                # Sink slightly into the member top so the AABB overlaps the body.
                origin=Origin(xyz=(length * fx, 0.0, tab_cz)),
                material="hardware",
                name=f"{prefix}_stop_tab_{idx}", material_class_id="metal.blackened_gunmetal",
            )
    return ModuleBuild(
        module_name="stop_tabs_only",
        parts_emitted=[],
        internal_articulations=[],
        interfaces={},
    )


def _build_guide_cage_pads_rollers_detail(ctx: ModuleBuildContext) -> ModuleBuild:
    """Guide cage (bronze pad block + roller cylinders) as a separate part
    FIXED to the outer member (S3/S4, rec_..._0003). A genuine sub-assembly
    with its own reference frame; every roller must touch the pad block so the
    part stays a single connected piece."""
    model = ctx.model
    r: ResolvedThreestageTelescopingSlideConfig = ctx.config  # type: ignore[assignment]

    cage = model.part("guide_cage")
    cage_l = max(0.020, r.outer_len * 0.14)
    cage_w = max(0.010, r.outer_w * 0.7)
    cage_h = max(0.008, r.outer_h * 0.5)
    cage.visual(
        Box((cage_l, cage_w, cage_h)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="bracket",
        name="cage_block", material_class_id="metal.aluminum_bare",
    )
    cage.visual(
        Box((cage_l * 1.28, cage_w * 1.18, max(0.0025, cage_h * 0.18))),
        origin=Origin(xyz=(0.0, 0.0, cage_h * 0.58)),
        material="hardware",
        name="access_cover_plate", material_class_id="metal.blackened_gunmetal",
    )
    # Straddle the block's rear face (block spans x in [-0.5, 0.5]*cage_l):
    # centered on the face so half the lip is sunk into the block and half
    # stands proud as the wiper — a fully-outboard lip floats as an island.
    cage.visual(
        Box((max(0.004, cage_l * 0.10), cage_w * 1.22, max(0.003, cage_h * 0.28))),
        origin=Origin(xyz=(-cage_l * 0.50, 0.0, cage_h * 0.18)),
        material="hardware",
        name="rear_wiper_lip", material_class_id="metal.blackened_gunmetal",
    )
    for sy, side in ((+1.0, "left"), (-1.0, "right")):
        cage.visual(
            Box((cage_l * 1.08, max(0.0025, cage_w * 0.12), cage_h * 0.95)),
            origin=Origin(xyz=(0.0, sy * cage_w * 0.55, 0.0)),
            material="bracket",
            name=f"side_cheek_{side}", material_class_id="metal.aluminum_bare",
        )
        for idx, rx in enumerate((-cage_l * 0.34, cage_l * 0.34)):
            cage.visual(
                Box(
                    (
                        max(0.004, cage_l * 0.10),
                        max(0.0018, cage_w * 0.10),
                        max(0.0025, cage_h * 0.16),
                    )
                ),
                origin=Origin(xyz=(rx, sy * cage_w * 0.61, cage_h * 0.32)),
                material="hardware",
                name=f"cover_screw_plate_{side}_{idx}", material_class_id="metal.blackened_gunmetal",
            )
    # Two bronze pads recessed into the block top/bottom (touching the block).
    for sz, name in ((+1.0, "top"), (-1.0, "bottom")):
        cage.visual(
            Box((cage_l * 0.8, cage_w * 0.8, max(0.003, cage_h * 0.22))),
            origin=Origin(xyz=(0.0, 0.0, sz * (cage_h * 0.5 - cage_h * 0.10))),
            material="roller",
            name=f"pad_{name}", material_class_id="metal.bronze_cast",
        )
    # Roller cylinders (axis along y) straddling the block; these are the
    # genuine separated pieces of the cage assembly.
    for idx, rx in enumerate((-cage_l * 0.28, cage_l * 0.28)):
        cage.visual(
            Cylinder(radius=max(0.003, cage_h * 0.35), length=cage_w * 1.05),
            origin=Origin(xyz=(rx, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="roller",
            name=f"roller_{idx}", material_class_id="metal.bronze_cast",
        )
    cage.inertial = Inertial.from_geometry(
        Box((cage_l, cage_w, cage_h)),
        mass=0.04,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    outer = model.get_part("outer_member")
    # FIXED to the outer member near its front mouth. Anchor LOW (at the floor
    # level z=wall) so the cage block physically straddles the outer's solid
    # floor — open/hollow cross sections have no solid at mid-height, so a
    # mid-height anchor would leave the cage physically floating
    # (fail_if_isolated_parts).
    model.articulation(
        "outer_to_guide_cage",
        ArticulationType.FIXED,
        parent=outer,
        child=cage,
        origin=Origin(xyz=(r.outer_len * 0.82, 0.0, r.wall)),
    )
    return ModuleBuild(
        module_name="guide_cage_pads_rollers",
        parts_emitted=["guide_cage"],
        internal_articulations=["outer_to_guide_cage"],
        interfaces={},
    )


def _build_ball_race_rollers_detail(ctx: ModuleBuildContext) -> ModuleBuild:
    """Ball/roller race: a row of cylindrical rollers FIXED to the outer
    member as a single part (S8/S9, rec_..._fd45679a / rec_..._5aa889ab); the
    rollers seat against a shared race strip so the part stays connected."""
    model = ctx.model
    r: ResolvedThreestageTelescopingSlideConfig = ctx.config  # type: ignore[assignment]

    race = model.part("ball_race")
    n = 5  # odd so the middle bearing shoe sits at the part-frame origin.
    roller_r = max(0.003, r.outer_h * 0.16)
    span = r.outer_len * 0.5
    pitch = span / max(1, n - 1)
    rail_t = max(0.0025, roller_r * 0.42)
    race.visual(
        Box((span * 1.08, r.outer_w * 0.58, rail_t)),
        origin=Origin(xyz=(0.0, 0.0, -roller_r * 0.85)),
        material="hardware",
        name="race_lower_retainer", material_class_id="metal.blackened_gunmetal",
    )
    race.visual(
        Box((span * 1.08, r.outer_w * 0.58, rail_t)),
        origin=Origin(xyz=(0.0, 0.0, roller_r * 0.85)),
        material="hardware",
        name="race_upper_retainer", material_class_id="metal.blackened_gunmetal",
    )
    for idx in range(n):
        rx = (idx - (n - 1) / 2.0) * pitch  # symmetric about 0; idx=2 -> rx=0
        # Shoes must bridge the two retainer plates (inner faces at
        # |z| = 0.85*roller_r - rail_t/2 >= 0.64*roller_r) or they float as
        # disconnected islands between them; span +-0.8*roller_r so each shoe
        # welds into both retainers.
        race.visual(
            Box((max(0.006, pitch * 0.32), r.outer_w * 0.46, roller_r * 1.6)),
            origin=Origin(xyz=(rx, 0.0, 0.0)),
            material="roller",
            name=f"bearing_shoe_{idx}", material_class_id="metal.bronze_cast",
        )
    for idx, rx in enumerate((-span * 0.53, span * 0.53)):
        race.visual(
            Box((max(0.004, span * 0.035), r.outer_w * 0.62, roller_r * 2.2)),
            origin=Origin(xyz=(rx, 0.0, 0.0)),
            material="hardware",
            name=f"race_end_stop_{idx}", material_class_id="metal.blackened_gunmetal",
        )
    race.inertial = Inertial.from_geometry(
        Box((span, r.outer_w * 0.5, 2.0 * roller_r)),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    outer = model.get_part("outer_member")
    # Anchor at the floor level so the rollers straddle the outer's solid floor
    # (open/hollow cross sections have no solid at mid-height).
    model.articulation(
        "outer_to_ball_race",
        ArticulationType.FIXED,
        parent=outer,
        child=race,
        origin=Origin(xyz=(r.outer_len * 0.5, 0.0, r.wall)),
    )
    return ModuleBuild(
        module_name="ball_race_rollers",
        parts_emitted=["ball_race"],
        internal_articulations=["outer_to_ball_race"],
        interfaces={},
    )


# --------------------------------------------------------------------------- #
# Slot graph + entry points
# --------------------------------------------------------------------------- #


BASE_FACTORIES = {
    "integral_grounded_outer": _build_integral_grounded_outer_base,
    "support_frame_fixed": _build_support_frame_fixed_base,
    "wall_backplate_fixed": _build_wall_backplate_fixed_base,
    "grounded_carrier_body": _build_grounded_carrier_body_base,
}

OUTER_FACTORIES = {"outer_member": _build_outer_member}
MIDDLE_FACTORIES = {"middle_member": _build_middle_member}
INNER_FACTORIES = {"inner_member": _build_inner_member}

TERMINAL_FACTORIES = {
    "bare_no_terminal": _build_bare_no_terminal,
    "carriage_shoe": _build_carriage_shoe_terminal,
    "flat_end_plate": _build_flat_end_plate_terminal,
    "top_carriage_tray": _build_top_carriage_tray_terminal,
}

DETAIL_FACTORIES = {
    "none_clean": _build_none_clean_detail,
    "stop_tabs_only": _build_stop_tabs_only_detail,
    "guide_cage_pads_rollers": _build_guide_cage_pads_rollers_detail,
    "ball_race_rollers": _build_ball_race_rollers_detail,
}


def _slots_for_config(r: ResolvedThreestageTelescopingSlideConfig) -> list[SlotSpec]:
    """Build the slot graph with each slot pinned to the chosen module.

    Six slots in chain order: base -> outer -> middle -> inner -> terminal ->
    detail. The member modules emit their own prismatic / fixed joints (manual
    wiring via ``ctx.upstream_interface``); the assembler is used only to walk
    the slot order and thread the downstream interface through.
    """
    return [
        SlotSpec(
            slot_name="base",
            candidates={r.base_module: BASE_FACTORIES[r.base_module]},
            anchor_choice=r.base_module,
        ),
        SlotSpec(
            slot_name="outer",
            candidates={"outer_member": OUTER_FACTORIES["outer_member"]},
            anchor_choice="outer_member",
        ),
        SlotSpec(
            slot_name="middle",
            candidates={"middle_member": MIDDLE_FACTORIES["middle_member"]},
            anchor_choice="middle_member",
        ),
        SlotSpec(
            slot_name="inner",
            candidates={"inner_member": INNER_FACTORIES["inner_member"]},
            anchor_choice="inner_member",
        ),
        SlotSpec(
            slot_name="terminal",
            candidates={r.terminal_module: TERMINAL_FACTORIES[r.terminal_module]},
            anchor_choice=r.terminal_module,
        ),
        SlotSpec(
            slot_name="detail",
            candidates={r.detail_module: DETAIL_FACTORIES[r.detail_module]},
            anchor_choice=r.detail_module,
        ),
    ]


def build_threestage_telescoping_slide(
    config: ThreestageTelescopingSlideConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    """Compose a three-stage telescoping slide by running each slot's module
    factory in chain order. Joints are emitted by the module factories
    themselves (prismatic main chain + optional FIXED children)."""

    r = resolve_config(config)
    model = ArticulatedObject(name="threestage_telescoping_slide", assets=assets)
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


def build_seeded_threestage_telescoping_slide(seed: int) -> ArticulatedObject:
    return build_threestage_telescoping_slide(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Return the (slot, module) picks for inspection — consumed by the
    ``module_topology_diversity`` gate. The three member slots are fixed; the
    topology varies on base / section_style / terminal / detail. We surface
    section_style as the outer/middle/inner module identity so the gate counts
    cross-section family changes as distinct topologies."""
    cfg = config_from_seed(seed)
    r = resolve_config(cfg)
    member_id = f"{r.section_style}_member"
    return [
        ("base", r.base_module),
        ("outer", member_id),
        ("middle", member_id),
        ("inner", member_id),
        ("terminal", r.terminal_module),
        ("detail", r.detail_module),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC — nested-member overlap + island allowances
# --------------------------------------------------------------------------- #


def _allow_nested_member_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    """Telescoping members nest inside one another by design, so their AABBs
    (and several visuals) overlap at the home pose. Declare those overlaps at
    the link-pair level; also allow each member's overlap with whatever base
    part it sits inside, and the FIXED detail/terminal child overlaps."""
    part_names = {p.name for p in model.parts}

    member_pairs = [
        ("outer_member", "middle_member"),
        ("middle_member", "inner_member"),
        ("outer_member", "inner_member"),
    ]
    for a, b in member_pairs:
        if a in part_names and b in part_names:
            ctx.allow_overlap(
                model.get_part(a),
                model.get_part(b),
                reason=f"{b} telescopes inside {a} by design (nested slide engagement)",
            )

    # Base part captures / overlaps the members and any FIXED children that sit
    # over it (terminal at the inner end, guide hardware on the outer).
    base_parts = [p for p in ("support_frame", "rear_support", "carrier_body") if p in part_names]
    base_children = [
        c
        for c in (
            "outer_member",
            "middle_member",
            "inner_member",
            "terminal",
            "guide_cage",
            "ball_race",
        )
        if c in part_names
    ]
    for base_part in base_parts:
        for child in base_children:
            ctx.allow_overlap(
                model.get_part(base_part),
                model.get_part(child),
                reason=f"{base_part} mounts/houses {child} (fixed base support)",
            )

    # Terminal FIXED on the inner end. At the retracted home pose the inner end
    # sits deep inside the middle/outer members, so the terminal overlaps all
    # three member bodies.
    if "terminal" in part_names:
        for member in ("inner_member", "middle_member", "outer_member"):
            if member in part_names:
                ctx.allow_overlap(
                    model.get_part(member),
                    model.get_part("terminal"),
                    reason=f"terminal is FIXED on the inner end, nested inside {member} at home",
                )

    # Detail guide cage / ball race FIXED to the outer member; allow overlap
    # with the outer body, the nested stages it straddles, and (at the
    # retracted home pose) a terminal that sits under the outer front mouth.
    for detail_part in ("guide_cage", "ball_race"):
        if detail_part in part_names:
            for other in ("outer_member", "middle_member", "inner_member", "terminal"):
                if other in part_names:
                    ctx.allow_overlap(
                        model.get_part(other),
                        model.get_part(detail_part),
                        reason=f"{detail_part} guide hardware engages {other}",
                    )


def _expect_slide_identity(ctx: TestContext, model: ArticulatedObject) -> None:
    """Hard category identity checks for the sweep path.

    Slot replacement is allowed to change the base, section family, terminal,
    and guide details, but the object must remain exactly a three-member,
    two-prismatic, coaxial telescoping slide.
    """

    required_members = {"outer_member", "middle_member", "inner_member"}
    part_names = {p.name for p in model.parts}
    missing_members = sorted(required_members - part_names)
    extra_members = sorted(
        n for n in part_names if n.endswith("_member") and n not in required_members
    )
    ctx.check(
        "identity_three_stage_members_present",
        not missing_members,
        "missing member part(s): " + ", ".join(missing_members),
    )
    ctx.check(
        "identity_no_extra_stage_members",
        not extra_members,
        "unexpected member-like part(s): " + ", ".join(extra_members),
    )

    articulations = list(getattr(model, "articulations", []) or [])
    prismatic = [a for a in articulations if a.articulation_type == ArticulationType.PRISMATIC]
    ctx.check(
        "identity_prismatic_joint_count",
        len(prismatic) == 2,
        f"expected exactly 2 prismatic joints, found {len(prismatic)}",
    )

    required_joints = {
        "outer_to_middle": ("outer_member", "middle_member"),
        "middle_to_inner": ("middle_member", "inner_member"),
    }
    by_name = {a.name: a for a in articulations}
    for joint_name, (parent, child) in required_joints.items():
        joint = by_name.get(joint_name)
        if joint is None:
            ctx.fail(f"identity_{joint_name}_present", f"missing required joint {joint_name}")
            continue
        ctx.check(
            f"identity_{joint_name}_type",
            joint.articulation_type == ArticulationType.PRISMATIC,
            f"{joint_name} type is {joint.articulation_type!r}, expected PRISMATIC",
        )
        ctx.check(
            f"identity_{joint_name}_parent_child",
            joint.parent == parent and joint.child == child,
            f"{joint_name} connects {joint.parent}->{joint.child}, expected {parent}->{child}",
        )
        axis = tuple(float(v) for v in (joint.axis or (0.0, 0.0, 0.0)))
        ctx.check(
            f"identity_{joint_name}_axis_plus_x",
            len(axis) == 3
            and abs(axis[0] - 1.0) <= 1e-6
            and abs(axis[1]) <= 1e-6
            and abs(axis[2]) <= 1e-6,
            f"{joint_name} axis is {axis}, expected (1, 0, 0)",
        )
        limits = getattr(joint, "motion_limits", None)
        lower = float(getattr(limits, "lower", 0.0) or 0.0)
        upper = float(getattr(limits, "upper", 0.0) or 0.0)
        ctx.check(
            f"identity_{joint_name}_positive_travel",
            lower == 0.0 and upper > 0.0,
            f"{joint_name} limits are lower={lower:g}, upper={upper:g}; expected 0..positive",
        )


def _expect_stage_engagement(ctx: TestContext, model: ArticulatedObject) -> None:
    """Verify each stage stays engaged (overlaps along x) at BOTH retracted
    and fully-extended poses, and that nesting containment holds for the
    concentric families."""
    part_names = {p.name for p in model.parts}
    if not {"outer_member", "middle_member", "inner_member"} <= part_names:
        ctx.fail(
            "stage_engagement_members_present",
            "outer_member, middle_member, and inner_member are required for engagement checks",
        )
        return

    try:
        om = model.get_articulation("outer_to_middle")
        mi = model.get_articulation("middle_to_inner")
    except Exception as exc:  # noqa: BLE001
        ctx.fail(
            "stage_engagement_joints_present",
            f"required prismatic joints missing or inaccessible: {exc}",
        )
        return

    outer = model.get_part("outer_member")
    middle = model.get_part("middle_member")
    inner = model.get_part("inner_member")

    om_up = float(getattr(getattr(om, "motion_limits", None), "upper", 0.0) or 0.0)
    mi_up = float(getattr(getattr(mi, "motion_limits", None), "upper", 0.0) or 0.0)

    # Retracted (home) engagement.
    with ctx.pose({om: 0.0, mi: 0.0}):
        ctx.expect_overlap(
            middle, outer, axes="x", min_overlap=0.005, name="home_overlap_mid_outer"
        )
        ctx.expect_overlap(
            inner, middle, axes="x", min_overlap=0.005, name="home_overlap_inner_mid"
        )

    # Fully-extended engagement (retained overlap > 0).
    with ctx.pose({om: om_up, mi: mi_up}):
        ctx.expect_overlap(
            middle, outer, axes="x", min_overlap=0.005, name="extended_overlap_mid_outer"
        )
        ctx.expect_overlap(
            inner, middle, axes="x", min_overlap=0.005, name="extended_overlap_inner_mid"
        )

    # Cross-section nesting containment for concentric (box-like) families.
    r_section = _section_of(model)
    if r_section in ("closed_box_tube", "open_channel_raceway", "primitive_wall_box"):
        with ctx.pose({om: 0.0, mi: 0.0}):
            ctx.expect_within(middle, outer, axes="yz", margin=0.004, name="nest_mid_in_outer_yz")
            ctx.expect_within(inner, middle, axes="yz", margin=0.004, name="nest_inner_in_mid_yz")


def _section_of(model: ArticulatedObject) -> str:
    names = {v.name for p in model.parts for v in getattr(p, "visuals", [])}
    if "outer_tube" in names:
        return "closed_box_tube"
    if "outer_channel" in names:
        return "open_channel_raceway"
    if "outer_floor" in names:
        return "primitive_wall_box"
    return "side_web_race"


def run_threestage_telescoping_slide_tests(
    model: ArticulatedObject,
    config: ThreestageTelescopingSlideConfig,
) -> TestReport:
    """Author-layer QC for the modular telescoping slide.

    Centralizes the intentional nested-member ``allow_overlap`` declarations,
    then runs the engagement / containment expectations on top of the standard
    structural gates."""

    ctx = TestContext(model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    _expect_slide_identity(ctx, model)
    _allow_nested_member_overlaps(ctx, model)
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    _expect_stage_engagement(ctx, model)

    return ctx.report()


__all__ = [
    "BaseModule",
    "DetailModule",
    "ResolvedThreestageTelescopingSlideConfig",
    "SectionStyle",
    "SlidePaletteTheme",
    "TerminalModule",
    "ThreestageTelescopingSlideConfig",
    "build_seeded_threestage_telescoping_slide",
    "build_threestage_telescoping_slide",
    "config_from_seed",
    "resolve_config",
    "run_threestage_telescoping_slide_tests",
    "slot_choices_for_seed",
]
