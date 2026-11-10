# SPDX-License-Identifier: Apache-2.0

"""Retractable patio awning — modular procedural template.

Single motion spine = the "001" folding-arm cassette awning
(`retractable_patio_awning_001`): a grounded/wall head (cassette) whose fabric
roller retracts a canopy, folding lateral support arms push out a front bar, and
a manual drive winds the mechanism. This is the faithful category identity; the
"002" cantilever-umbrella records (flagged as a classification mismatch in-record
and listed under `must_not_become: ordinary patio umbrella`) contribute only
their Box grounded-support geometry, adapted under AUTHORING §A Rule 3 into the
support_topology slot (same Box primitive family, same grounded support-base
part role).

Slots (see specs_modular_v1/retractable_patio_awning.md):
  - support_topology  (③ Primary Form Family + ①): wall_bracket / floor_uprights /
                       freestanding_dual_post / roof_curb_mount  — grounded visuals
                       on the head part.
  - extension_mechanism (② joint type + ①): folding_lateral_arms / telescoping_arms /
                       scissor_arms / guided_side_rails — arm sub-structure + shoulder/
                       elbow joint TYPE (REVOLUTE x vs PRISMATIC y).
  - drive             : plain_crank / chain_loop_drive / gearbox_crank /
                       spring_rewind_roller.
  - arm_count (mult)  : N in {2,3,4}, weighted (0.5,0.3,0.2); folding arm pairs
                       copied via `for i in range(n)`, each folding in its own
                       x=const vertical plane (adjacent arms never self-collide).

All captured mechanical pivots (shoulder pin in bracket, elbow pin in clevis,
arm tip in front-bar socket, drive spindle in housing, roller axle in end
bearing, spring mandrel in cartridge) are grandfathered (no MatingContract,
element-scoped `allow_overlap`), mirroring the 001 source record.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True

SupportTopology = Literal[
    "wall_bracket", "floor_uprights", "freestanding_dual_post", "roof_curb_mount"
]
ExtensionMechanism = Literal[
    "folding_lateral_arms", "telescoping_arms", "scissor_arms", "guided_side_rails"
]
Drive = Literal["plain_crank", "chain_loop_drive", "gearbox_crank", "spring_rewind_roller"]
PaletteStyle = Literal[
    "charcoal_awning",
    "cream_market",
    "forest_canvas",
    "terracotta_stripe",
    "sand_beige",
    "slate_blue",
]

SUPPORT_TOPOLOGIES: tuple[SupportTopology, ...] = (
    "wall_bracket",
    "floor_uprights",
    "freestanding_dual_post",
    "roof_curb_mount",
)
EXTENSION_MECHANISMS: tuple[ExtensionMechanism, ...] = (
    "folding_lateral_arms",
    "telescoping_arms",
    "scissor_arms",
    "guided_side_rails",
)
DRIVES: tuple[Drive, ...] = (
    "plain_crank",
    "chain_loop_drive",
    "gearbox_crank",
    "spring_rewind_roller",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "charcoal_awning",
    "cream_market",
    "forest_canvas",
    "terracotta_stripe",
    "sand_beige",
    "slate_blue",
)

ARM_COUNT_CHOICES: tuple[int, ...] = (2, 3, 4)
ARM_COUNT_WEIGHTS: tuple[float, ...] = (0.50, 0.30, 0.20)

# palette tokens: fabric (canopy), frame (housing/frame), metal (roller/aluminium),
# hardware (pivots/pins), accent (seams/valance detail). Real 001/002 colorways +
# realistic companion colorways (⑥ record_only / world_knowledge_extrapolation).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "charcoal_awning": {  # 001 source colorway
        "fabric": (0.105, 0.100, 0.105, 1.0),
        "frame": (0.145, 0.145, 0.155, 1.0),
        "metal": (0.58, 0.60, 0.62, 1.0),
        "hardware": (0.25, 0.26, 0.28, 1.0),
        "accent": (0.055, 0.060, 0.065, 1.0),
    },
    "cream_market": {  # 002 source colorway
        "fabric": (0.88, 0.84, 0.72, 1.0),
        "frame": (0.075, 0.080, 0.082, 1.0),
        "metal": (0.38, 0.39, 0.39, 1.0),
        "hardware": (0.25, 0.25, 0.24, 1.0),
        "accent": (0.76, 0.71, 0.59, 1.0),
    },
    "forest_canvas": {
        "fabric": (0.16, 0.28, 0.18, 1.0),
        "frame": (0.10, 0.11, 0.10, 1.0),
        "metal": (0.55, 0.57, 0.56, 1.0),
        "hardware": (0.22, 0.24, 0.22, 1.0),
        "accent": (0.10, 0.18, 0.12, 1.0),
    },
    "terracotta_stripe": {
        "fabric": (0.62, 0.28, 0.18, 1.0),
        "frame": (0.14, 0.13, 0.12, 1.0),
        "metal": (0.60, 0.60, 0.58, 1.0),
        "hardware": (0.28, 0.26, 0.24, 1.0),
        "accent": (0.86, 0.80, 0.70, 1.0),
    },
    "sand_beige": {
        "fabric": (0.80, 0.72, 0.56, 1.0),
        "frame": (0.30, 0.28, 0.24, 1.0),
        "metal": (0.62, 0.63, 0.62, 1.0),
        "hardware": (0.34, 0.32, 0.28, 1.0),
        "accent": (0.66, 0.58, 0.44, 1.0),
    },
    "slate_blue": {
        "fabric": (0.24, 0.30, 0.40, 1.0),
        "frame": (0.12, 0.14, 0.17, 1.0),
        "metal": (0.56, 0.59, 0.63, 1.0),
        "hardware": (0.26, 0.29, 0.33, 1.0),
        "accent": (0.18, 0.23, 0.31, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Base dimensions (m), adapted from 001 source (width=3.78, projection=2.35,
# cassette top z≈2.685).
# --------------------------------------------------------------------------- #
_EDGE_MARGIN = 0.30  # arm keep-out from the awning ends (m)
_ARM_X_WIDTH = 0.12  # arm x footprint incl. clearance (m)
_MAX_ARM_PITCH = 1.30  # max center-to-center arm spacing (m)


@dataclass(frozen=True)
class RetractablePatioAwningConfig:
    support_topology: SupportTopology | None = None
    extension_mechanism: ExtensionMechanism | None = None
    drive: Drive | None = None
    arm_count: int | None = None
    palette_style: PaletteStyle = "charcoal_awning"
    awning_width: float = 3.78
    projection: float = 2.35
    head_height: float = 2.685
    scallop_count: int = 10
    name: str = "retractable_patio_awning"


@dataclass(frozen=True)
class ResolvedRetractablePatioAwningConfig:
    support_topology: SupportTopology
    extension_mechanism: ExtensionMechanism
    drive: Drive
    arm_count: int
    palette_style: PaletteStyle
    awning_width: float
    projection: float
    head_height: float
    scallop_count: int
    arm_spacing: float
    shoulder_lower: float
    shoulder_upper: float
    elbow_lower: float
    elbow_upper: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> RetractablePatioAwningConfig:
    """Deterministic weighted procedural sampling (seed 0 not special)."""
    rng = random.Random(seed)
    return RetractablePatioAwningConfig(
        support_topology=rng.choice(SUPPORT_TOPOLOGIES),
        extension_mechanism=rng.choice(EXTENSION_MECHANISMS),
        drive=rng.choice(DRIVES),
        arm_count=rng.choices(ARM_COUNT_CHOICES, weights=ARM_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        awning_width=round(rng.uniform(3.30, 4.10), 4),
        projection=round(rng.uniform(2.00, 2.60), 4),
        head_height=round(rng.uniform(2.40, 2.85), 4),
        scallop_count=rng.choice((7, 9, 10, 12)),
        name=f"seeded_retractable_patio_awning_{seed}",
    )


def resolve_config(
    config: RetractablePatioAwningConfig | None = None,
) -> ResolvedRetractablePatioAwningConfig:
    cfg = config or RetractablePatioAwningConfig()

    support = _pick(cfg.support_topology, SUPPORT_TOPOLOGIES)
    extension = _pick(cfg.extension_mechanism, EXTENSION_MECHANISMS)
    drive = _pick(cfg.drive, DRIVES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    arm_count = int(cfg.arm_count) if cfg.arm_count is not None else 2
    arm_count = int(_clamp(arm_count, 2, 4))

    width = _clamp(float(cfg.awning_width), 3.30, 4.10)
    projection = _clamp(float(cfg.projection), 2.00, 2.60)
    head_height = _clamp(float(cfg.head_height), 2.40, 2.85)
    scallop_count = int(_clamp(int(cfg.scallop_count), 6, 14))

    # projection must not exceed ~0.85*width (canopy stays self-supportable).
    projection = min(projection, 0.85 * width)

    # arm_spacing (equation): even distribution across the usable span; then the
    # self-collision inequality caps it and re-checks it fits.
    spread = width - 2.0 * _EDGE_MARGIN
    if arm_count >= 2:
        arm_spacing = min(spread / (arm_count - 1), _MAX_ARM_PITCH)
    else:
        arm_spacing = 0.0
    # inequality: (n-1)*spacing + arm_x_width <= width - 2*edge_margin
    if arm_count >= 2:
        max_total = width - 2.0 * _EDGE_MARGIN - _ARM_X_WIDTH
        while (arm_count - 1) * arm_spacing > max_total and arm_spacing > 0.20:
            arm_spacing -= 0.02
        arm_spacing = max(arm_spacing, 0.20)

    # conditional joint travel. Motion is authored so arms only ever move DOWN /
    # OUT (away from the canopy and the cassette body): revolute folds droop the
    # arm (upper bound 0 = deployed rest, never rises into the fabric); prismatic
    # slides deploy outward (+, away from the body, never retracting into the
    # roller). This keeps the whole sampled-pose envelope collision-free.
    if extension == "guided_side_rails":
        # both prismatic; rest = deployed, motion RETRACTS inward (never
        # overshoots the front bar; shoulder retract capped to clear the roller).
        shoulder_lower, shoulder_upper = -0.09, 0.0
        elbow_lower, elbow_upper = -0.30, 0.0
    elif extension == "telescoping_arms":
        # shoulder revolute droop (rad), elbow prismatic RETRACT inward (m).
        shoulder_lower, shoulder_upper = -0.65, 0.0
        elbow_lower, elbow_upper = -0.35, 0.0
    else:
        # folding_lateral_arms / scissor_arms: both revolute droop (rad).
        shoulder_lower, shoulder_upper = -0.75, 0.0
        elbow_lower, elbow_upper = -1.10, 0.0
        if arm_count >= 4:
            shoulder_lower, elbow_lower = -0.62, -0.90

    return ResolvedRetractablePatioAwningConfig(
        support_topology=support,
        extension_mechanism=extension,
        drive=drive,
        arm_count=arm_count,
        palette_style=palette_style,
        awning_width=width,
        projection=projection,
        head_height=head_height,
        scallop_count=scallop_count,
        arm_spacing=arm_spacing,
        shoulder_lower=shoulder_lower,
        shoulder_upper=shoulder_upper,
        elbow_lower=elbow_lower,
        elbow_upper=elbow_upper,
        name=cfg.name or "retractable_patio_awning",
    )


def with_overrides(
    config: RetractablePatioAwningConfig, **kwargs: object
) -> RetractablePatioAwningConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: RetractablePatioAwningConfig | ResolvedRetractablePatioAwningConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedRetractablePatioAwningConfig)
        else resolve_config(config)
    )
    return (
        ("support_topology", r.support_topology),
        ("extension_mechanism", r.extension_mechanism),
        ("drive", r.drive),
        ("arm_count", f"n{r.arm_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #
def _fabric_geometry(
    width: float,
    rear_y: float,
    rear_z: float,
    front_y: float,
    front_z: float,
    valance_drop: float,
    scallop_depth: float,
    scallop_count: int,
) -> MeshGeometry:
    """Thin L-section canopy mesh: sloping cloth + scalloped valance.

    Adapted verbatim (primitive preserved: MeshGeometry) from 001 model.py
    L19-L68. The valance is derived per-station from the front edge so it hugs
    the canopy across ③/⑤ changes (Rule 4)."""
    geom = MeshGeometry()
    station_count = scallop_count * 2 + 1
    loops: list[list[int]] = []
    for index in range(station_count):
        u = index / (station_count - 1)
        x = -width / 2.0 + width * u
        scallop = abs(math.sin(math.pi * scallop_count * u))
        lower_z = front_z - valance_drop - scallop_depth * scallop
        section = (
            (rear_y, rear_z),
            (front_y, front_z),
            (front_y, lower_z),
            (front_y - 0.022, lower_z),
            (front_y - 0.022, front_z - 0.020),
            (rear_y, rear_z - 0.014),
        )
        loops.append([geom.add_vertex(x, y, z) for y, z in section])
    for index in range(station_count - 1):
        a = loops[index]
        b = loops[index + 1]
        for edge in range(6):
            nxt = (edge + 1) % 6
            geom.add_face(a[edge], b[edge], b[nxt])
            geom.add_face(a[edge], b[nxt], a[nxt])
    left = loops[0]
    right = loops[-1]
    for loop, reverse in ((left, True), (right, False)):
        cap_faces = ((0, 1, 4), (0, 4, 5), (1, 2, 3), (1, 3, 4))
        for a, b, c in cap_faces:
            if reverse:
                geom.add_face(loop[a], loop[c], loop[b])
            else:
                geom.add_face(loop[a], loop[b], loop[c])
    return geom


def _add_arm_segment(
    part,
    length: float,
    frame_mat: str,
    accent_mat: str,
    *,
    distal_name: str,
    mechanism: ExtensionMechanism,
) -> None:
    """One arm segment built along +y from the part origin. Adapted from 001
    model.py L71-L117. `mechanism` adds telescoping sleeve / scissor cross /
    guided rail flanges without changing the primitive family."""
    beam_depth = 0.058
    if mechanism == "telescoping_arms":
        beam_depth = 0.082  # outer sleeve
    part.visual(
        Box((beam_depth, length, 0.044)),
        origin=Origin(xyz=(0.0, length / 2.0, 0.0)),
        material=frame_mat,
        name="arm_beam", material_class_id="metal.paint_coated",
    )
    if distal_name == "elbow_clevis":
        part.visual(
            Cylinder(radius=0.038, length=0.054),
            origin=Origin(rpy=(0.0, 0.0, 0.0)),
            material=accent_mat,
            name="shoulder_pin", material_class_id="metal.stainless_matte",
        )
        part.visual(
            Box((0.100, 0.080, 0.060)),
            origin=Origin(xyz=(0.0, length - 0.020, 0.0)),
            material=accent_mat,
            name="elbow_clevis", material_class_id="metal.stainless_matte",
        )
    else:
        part.visual(
            Cylinder(radius=0.038, length=0.054),
            origin=Origin(rpy=(0.0, 0.0, 0.0)),
            material=accent_mat,
            name="elbow_pin", material_class_id="metal.stainless_matte",
        )
        part.visual(
            Box((0.100, 0.080, 0.060)),
            origin=Origin(xyz=(0.0, length - 0.020, 0.0)),
            material=accent_mat,
            name="front_pin", material_class_id="metal.stainless_matte",
        )
    # Parallel tension / spring member + mounting bridges. Kept back from the
    # very tip and root so only the beam + terminal pin engage the front bar.
    part.visual(
        Box((0.014, length * 0.54, 0.014)),
        origin=Origin(xyz=(0.044, length * 0.50, 0.026)),
        material=accent_mat,
        name="tension_link", material_class_id="metal.stainless_matte",
    )
    for index, y in enumerate((length * 0.28, length * 0.70)):
        part.visual(
            Box((0.050, 0.020, 0.026)),
            origin=Origin(xyz=(0.022, y, 0.013)),
            material=accent_mat,
            name=f"link_bridge_{index}", material_class_id="metal.stainless_matte",
        )
    if mechanism == "scissor_arms":
        # crossed scissor rail + centre pivot (structural distinction). Inset from
        # both ends so it does not reach the root bracket or the front-bar socket.
        part.visual(
            Box((0.030, length * 0.68, 0.020)),
            origin=Origin(xyz=(-0.036, length / 2.0, 0.006), rpy=(0.0, 0.20, 0.0)),
            material=frame_mat,
            name="scissor_cross", material_class_id="metal.paint_coated",
        )
        part.visual(
            Cylinder(radius=0.024, length=0.070),
            origin=Origin(xyz=(-0.006, length / 2.0, 0.010), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=accent_mat,
            name="scissor_pivot", material_class_id="metal.stainless_matte",
        )
    if mechanism == "guided_side_rails":
        # inset guide rails (do not reach the root bracket or front-bar socket);
        # overlap the beam edge so they stay connected to the arm geometry.
        for side_index, dx in enumerate((-(beam_depth / 2.0 - 0.002), beam_depth / 2.0 - 0.002)):
            part.visual(
                Box((0.012, length * 0.68, 0.052)),
                origin=Origin(xyz=(dx, length / 2.0, 0.0)),
                material=accent_mat,
                name=f"rail_flange_{side_index}", material_class_id="metal.paint_coated",
            )


def _drive_x(r: ResolvedRetractablePatioAwningConfig) -> float:
    """Drive housing centre x — just past the +x cassette end, beyond the roller
    tube (which ends at W/2-0.10), so the crank clears the roller (mirrors 001)."""
    return r.awning_width / 2.0 + 0.04


def _arm_x_positions(r: ResolvedRetractablePatioAwningConfig) -> list[float]:
    n = r.arm_count
    if n == 1:
        return [0.0]
    return [-(n - 1) * r.arm_spacing / 2.0 + i * r.arm_spacing for i in range(n)]


# --------------------------------------------------------------------------- #
# Support-topology builders (grounded visuals on the head part). Adapted from
# the four support_topology / origin records; Box primitives preserved.
# --------------------------------------------------------------------------- #
def _build_support(head, r: ResolvedRetractablePatioAwningConfig, mat: dict) -> None:
    # Support columns sit at y=-0.14 so they overlap the cassette_back face
    # (y in [-0.16,-0.10]) at the top and stay clear of the roller (y>=-0.031):
    # every support piece is chained into the connected head geometry (islands
    # gate is strict at 1e-6). Columns reach up INTO the cassette z-band.
    W = r.awning_width
    top = r.head_height
    cass_z = top - 0.13
    sy = -0.14
    col_top = cass_z + 0.06  # column top embeds into the cassette
    px = W * 0.39  # side support x position

    if r.support_topology == "wall_bracket":
        for index, x in enumerate((-px, px)):
            head.visual(
                Box((0.260, 0.055, 0.360)),
                origin=Origin(xyz=(x, sy, cass_z)),
                material=mat["accent"],
                name=f"wall_plate_{index}", material_class_id="metal.paint_coated",
            )
            head.visual(
                Box((0.150, 0.100, 0.140)),
                origin=Origin(xyz=(x, sy + 0.035, cass_z + 0.005)),
                material=mat["hardware"],
                name=f"wall_standoff_{index}", material_class_id="metal.paint_coated",
            )
            for bolt_index, z in enumerate((cass_z - 0.12, cass_z + 0.11)):
                head.visual(
                    Cylinder(radius=0.014, length=0.040),
                    origin=Origin(xyz=(x, sy - 0.02, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=mat["metal"],
                    name=f"wall_anchor_{index}_{bolt_index}", material_class_id="metal.stainless_matte",
                )
        return

    if r.support_topology == "floor_uprights":
        for index, x in enumerate((-px, px)):
            head.visual(
                Box((0.070, 0.090, col_top)),
                origin=Origin(xyz=(x, sy, col_top / 2.0)),
                material=mat["accent"],
                name=f"upright_{index}", material_class_id="metal.paint_coated",
            )
            head.visual(
                Box((0.22, 0.18, 0.050)),
                origin=Origin(xyz=(x, sy, 0.025)),
                material=mat["accent"],
                name=f"foot_plate_{index}", material_class_id="metal.paint_coated",
            )
            head.visual(
                Cylinder(radius=0.032, length=0.030),
                origin=Origin(xyz=(x, sy, 0.020)),
                material=mat["hardware"],
                name=f"leveling_pad_{index}", material_class_id="rubber.smooth_plain",
            )
            head.visual(
                Box((0.24, 0.030, 0.34)),
                origin=Origin(xyz=(x, sy + 0.045, cass_z)),
                material=mat["accent"],
                name=f"mount_plate_{index}", material_class_id="metal.paint_coated",
            )
        return

    if r.support_topology == "freestanding_dual_post":
        base_w = min(1.20, W * 0.34)
        head.visual(
            Box((base_w, 1.10, 0.12)),
            origin=Origin(xyz=(0.0, sy, 0.06)),
            material=mat["hardware"],
            name="base_slab", material_class_id="concrete.smooth_cast",
        )
        head.visual(
            Box((base_w - 0.10, 0.16, 0.12)),
            origin=Origin(xyz=(0.0, sy - 0.03, cass_z)),
            material=mat["frame"],
            name="top_header", material_class_id="metal.paint_coated",
        )
        post_x = base_w / 2.0 - 0.12  # posts sit on the base slab
        for index, x in enumerate((-post_x, post_x)):
            head.visual(
                Box((0.12, 0.12, col_top)),
                origin=Origin(xyz=(x, sy, col_top / 2.0)),
                material=mat["frame"],
                name=f"support_post_{index}", material_class_id="metal.paint_coated",
            )
            head.visual(
                Box((0.42, 0.34, 0.045)),
                origin=Origin(xyz=(x, sy, 0.14)),
                material=mat["frame"],
                name=f"mast_mount_plate_{index}", material_class_id="metal.paint_coated",
            )
        return

    # roof_curb_mount
    head.visual(
        Box((min(1.40, W * 0.40), 0.90, 0.100)),
        origin=Origin(xyz=(0.0, sy, 0.050)),
        material=mat["hardware"],
        name="roof_curb", material_class_id="metal.paint_coated",
    )
    head.visual(
        Box((0.62, 0.46, 0.060)),
        origin=Origin(xyz=(0.0, sy, 0.110)),
        material=mat["metal"],
        name="galvanized_mount", material_class_id="metal.steel_galvanized",
    )
    head.visual(
        Box((0.16, 0.16, col_top - 0.08)),
        origin=Origin(xyz=(0.0, sy, (col_top - 0.08) / 2.0 + 0.08)),
        material=mat["frame"],
        name="curb_mast", material_class_id="metal.paint_coated",
    )


# --------------------------------------------------------------------------- #
# Head (cassette) + roller + front bar
# --------------------------------------------------------------------------- #
def _build_head(head, r: ResolvedRetractablePatioAwningConfig, mat: dict) -> None:
    W = r.awning_width
    P = r.projection
    top = r.head_height
    cass_z = top - 0.13
    head.visual(
        Box((W, 0.32, 0.060)),
        origin=Origin(xyz=(0.0, 0.0, top)),
        material=mat["frame"],
        name="cassette_top", material_class_id="metal.paint_coated",
    )
    head.visual(
        Box((W, 0.060, 0.255)),
        origin=Origin(xyz=(0.0, -0.130, cass_z)),
        material=mat["frame"],
        name="cassette_back", material_class_id="metal.paint_coated",
    )
    head.visual(
        Box((W, 0.045, 0.135)),
        origin=Origin(xyz=(0.0, 0.148, cass_z + 0.010)),
        material=mat["frame"],
        name="cassette_lip", material_class_id="metal.paint_coated",
    )
    for index, x in enumerate((-W / 2.0 + 0.025, W / 2.0 - 0.025)):
        head.visual(
            Box((0.050, 0.32, 0.255)),
            origin=Origin(xyz=(x, 0.0, cass_z)),
            material=mat["frame"],
            name=f"end_cap_{index}", material_class_id="metal.paint_coated",
        )
    # Extended canopy (mesh) — lives on the grounded head, spans to the front bar.
    # The canopy plane sits well ABOVE the folding arms (arms run underneath it).
    cloth = mesh_from_geometry(
        _fabric_geometry(
            width=W - 0.08,
            rear_y=0.080,
            rear_z=top - 0.050,
            front_y=P,
            front_z=top - 0.340,
            valance_drop=0.245,
            scallop_depth=0.065,
            scallop_count=r.scallop_count,
        ),
        "awning_fabric",
    )
    head.visual(cloth, material=mat["fabric"], name="fabric_skin", material_class_id=("fabric.printed_pattern" if r.palette_style == "terracotta_stripe" else "fabric.canvas"))
    # Arm shoulder brackets on the head front, below the canopy plane.
    pivot_z = top - 0.22
    for index, x in enumerate(_arm_x_positions(r)):
        head.visual(
            Box((0.16, 0.16, 0.120)),
            origin=Origin(xyz=(x, 0.245, pivot_z)),
            material=mat["hardware"],
            name=f"pivot_bracket_{index}", material_class_id="metal.paint_coated",
        )
    # Drive housing at the +x end, BEYOND the roller (mirrors 001 source, whose
    # drive sits just past the cassette end so the crank clears the roller tube).
    drive_x = _drive_x(r)
    head.visual(
        Box((0.11, 0.18, 0.19)),
        origin=Origin(xyz=(drive_x, -0.005, cass_z + 0.02)),
        material=mat["accent"],
        name="drive_housing", material_class_id="metal.paint_coated",
    )
    if r.drive == "gearbox_crank":
        head.visual(
            Cylinder(radius=0.095, length=0.090),
            origin=Origin(xyz=(drive_x - 0.02, -0.005, cass_z + 0.02), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mat["frame"],
            name="gearbox_cover", material_class_id="metal.paint_coated",
        )
        head.visual(
            Cylinder(radius=0.030, length=0.070),
            origin=Origin(xyz=(drive_x + 0.05, -0.005, cass_z + 0.02), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mat["hardware"],
            name="gearbox_input_boss", material_class_id="metal.stainless_matte",
        )
    elif r.drive == "chain_loop_drive":
        head.visual(
            Box((0.13, 0.20, 0.24)),
            origin=Origin(xyz=(drive_x, -0.005, cass_z + 0.02)),
            material=mat["accent"],
            name="chain_drive_housing", material_class_id="metal.paint_coated",
        )
        head.visual(
            Cylinder(radius=0.055, length=0.050),
            origin=Origin(xyz=(drive_x + 0.05, -0.005, cass_z + 0.02), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mat["hardware"],
            name="chain_gearbox_boss", material_class_id="metal.stainless_matte",
        )
    elif r.drive == "spring_rewind_roller":
        head.visual(
            Cylinder(radius=0.036, length=0.090),
            origin=Origin(xyz=(-W / 2.0 + 0.045, 0.040, cass_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mat["hardware"],
            name="rewind_bearing", material_class_id="metal.stainless_matte",
        )


def _build_roller(roller, r: ResolvedRetractablePatioAwningConfig, mat: dict) -> None:
    W = r.awning_width
    roller.visual(
        Cylinder(radius=0.058, length=W - 0.20),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mat["metal"],
        name="roller_tube", material_class_id="metal.aluminum_bare",
    )
    roller.visual(
        Cylinder(radius=0.071, length=W - 0.32),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mat["fabric"],
        name="fabric_roll", material_class_id=("fabric.printed_pattern" if r.palette_style == "terracotta_stripe" else "fabric.canvas"),
    )
    roller.visual(
        Box((W - 0.53, 0.010, 0.012)),
        origin=Origin(xyz=(0.0, -0.071, 0.0)),
        material=mat["accent"],
        name="roller_seam", material_class_id="fabric.thread_yarn",
    )
    roller.visual(
        Cylinder(radius=0.018, length=W - 0.10),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mat["hardware"],
        name="roller_axle", material_class_id="metal.stainless_matte",
    )
    if r.drive == "spring_rewind_roller":
        roller.visual(
            Cylinder(radius=0.030, length=W - 0.40),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mat["hardware"],
            name="spring_mandrel", material_class_id="metal.stainless_matte",
        )
        roller.visual(
            Cylinder(radius=0.049, length=0.14),
            origin=Origin(xyz=(-W / 2.0 + 0.12, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mat["accent"],
            name="spring_cartridge", material_class_id="metal.paint_coated",
        )


def _build_front_bar(front_bar, r: ResolvedRetractablePatioAwningConfig, mat: dict) -> None:
    W = r.awning_width
    front_bar.visual(
        Box((W, 0.105, 0.105)),
        material=mat["frame"],
        name="front_bar_body", material_class_id="metal.paint_coated",
    )
    front_bar.visual(
        Box((W - 0.18, 0.035, 0.028)),
        origin=Origin(xyz=(0.0, 0.060, 0.015)),
        material=mat["accent"],
        name="front_bar_groove", material_class_id="metal.paint_coated",
    )
    for index, x in enumerate(_arm_x_positions(r)):
        front_bar.visual(
            Box((0.14, 0.13, 0.085)),
            origin=Origin(xyz=(x, -0.085, -0.005)),
            material=mat["hardware"],
            name=f"front_tab_{index}", material_class_id="metal.paint_coated",
        )


def _build_drive_part(drive_part, r: ResolvedRetractablePatioAwningConfig, mat: dict) -> None:
    if r.drive == "chain_loop_drive":
        drive_part.visual(
            Cylinder(radius=0.052, length=0.040),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mat["metal"],
            name="drive_sprocket", material_class_id="metal.stainless_matte",
        )
        drive_part.visual(
            Cylinder(radius=0.026, length=0.070),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mat["hardware"],
            name="sprocket_boss", material_class_id="metal.stainless_matte",
        )
        for strand_index, dz in enumerate((-0.052, 0.052)):
            drive_part.visual(
                Cylinder(radius=0.008, length=0.36),
                origin=Origin(xyz=(0.010, 0.0, dz)),
                material=mat["accent"],
                name=f"chain_strand_{strand_index}", material_class_id="metal.stainless_matte",
            )
        drive_part.visual(
            Box((0.020, 0.020, 0.10)),
            origin=Origin(xyz=(0.010, 0.0, -0.18)),
            material=mat["accent"],
            name="chain_return", material_class_id="metal.stainless_matte",
        )
        return
    # plain_crank / gearbox_crank / spring_rewind_roller (service key)
    drive_part.visual(
        Cylinder(radius=0.020, length=0.075),
        origin=Origin(xyz=(0.0375, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mat["metal"],
        name="crank_spindle", material_class_id="metal.stainless_matte",
    )
    if r.drive == "gearbox_crank":
        drive_part.visual(
            Cylinder(radius=0.045, length=0.040),
            origin=Origin(xyz=(0.020, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mat["hardware"],
            name="crank_hub", material_class_id="metal.stainless_matte",
        )
    drive_part.visual(
        Box((0.030, 0.030, 0.40)),
        origin=Origin(xyz=(0.075, 0.0, -0.20)),
        material=mat["accent"],
        name="crank_drop", material_class_id="metal.paint_coated",
    )
    drive_part.visual(
        Cylinder(radius=0.020, length=0.14),
        origin=Origin(xyz=(0.075, 0.070, -0.40), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mat["hardware"],
        name="crank_grip", material_class_id="rubber.smooth_plain",
    )


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_retractable_patio_awning(
    config: RetractablePatioAwningConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="retractable_patio_awning", assets=assets)

    mat = {}
    for token, rgba in PALETTES[r.palette_style].items():
        full = f"awn_{token}_{r.palette_style}"
        model.material(full, rgba=rgba)
        mat[token] = full

    W = r.awning_width
    P = r.projection
    top = r.head_height
    cass_z = top - 0.13
    front_z = top - 0.46
    pivot_z = top - 0.22
    arm_pitch = math.atan2(pivot_z - front_z, max(0.2, P - 0.245))

    head = model.part("head")
    _build_support(head, r, mat)
    _build_head(head, r, mat)

    roller = model.part("fabric_roller")
    _build_roller(roller, r, mat)

    front_bar = model.part("front_bar")
    _build_front_bar(front_bar, r, mat)

    # Arms (multiplicity).
    arm_xs = _arm_x_positions(r)
    upper_length = (P - 0.30) * 0.5
    fore_length = (P - 0.30) * 0.5
    prismatic_shoulder = r.extension_mechanism == "guided_side_rails"
    prismatic_elbow = r.extension_mechanism in ("guided_side_rails", "telescoping_arms")

    upper_parts = []
    fore_parts = []
    for index in range(r.arm_count):
        upper = model.part(f"upper_arm_{index}")
        _add_arm_segment(
            upper,
            upper_length,
            mat["accent"],
            mat["hardware"],
            distal_name="elbow_clevis",
            mechanism=r.extension_mechanism,
        )
        upper_parts.append(upper)
        fore = model.part(f"forearm_{index}")
        _add_arm_segment(
            fore,
            fore_length,
            mat["accent"],
            mat["hardware"],
            distal_name="front_pin",
            mechanism=r.extension_mechanism,
        )
        fore_parts.append(fore)

    drive_part = model.part("drive_part")
    _build_drive_part(drive_part, r, mat)

    # ---- Joints ---------------------------------------------------------- #
    # roller_rotation — shaft-in-bearing captured pivot (grandfathered).
    model.articulation(
        "roller_rotation",
        ArticulationType.REVOLUTE,
        parent=head,
        child=roller,
        origin=Origin(xyz=(0.0, 0.040, cass_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=45.0, velocity=2.0, lower=-8.0 * math.pi, upper=8.0 * math.pi
        ),
    )
    # front_bar_pitch — pivot on the bar centreline (grandfathered).
    model.articulation(
        "front_bar_pitch",
        ArticulationType.REVOLUTE,
        parent=head,
        child=front_bar,
        origin=Origin(xyz=(0.0, P, front_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.8, lower=-0.22, upper=0.22),
    )

    shoulder_type = ArticulationType.PRISMATIC if prismatic_shoulder else ArticulationType.REVOLUTE
    elbow_type = ArticulationType.PRISMATIC if prismatic_elbow else ArticulationType.REVOLUTE
    shoulder_axis = (0.0, 1.0, 0.0) if prismatic_shoulder else (1.0, 0.0, 0.0)
    elbow_axis = (0.0, 1.0, 0.0) if prismatic_elbow else (1.0, 0.0, 0.0)
    for index, x in enumerate(arm_xs):
        model.articulation(
            f"shoulder_hinge_{index}",
            shoulder_type,
            parent=head,
            child=upper_parts[index],
            origin=Origin(xyz=(x, 0.245, pivot_z), rpy=(-arm_pitch, 0.0, 0.0)),
            axis=shoulder_axis,
            motion_limits=MotionLimits(
                effort=220.0, velocity=0.7, lower=r.shoulder_lower, upper=r.shoulder_upper
            ),
        )
        model.articulation(
            f"elbow_hinge_{index}",
            elbow_type,
            parent=upper_parts[index],
            child=fore_parts[index],
            origin=Origin(xyz=(0.0, upper_length, 0.0)),
            axis=elbow_axis,
            motion_limits=MotionLimits(
                effort=160.0, velocity=0.9, lower=r.elbow_lower, upper=r.elbow_upper
            ),
        )

    # drive joint.
    drive_x = _drive_x(r)
    if r.drive == "chain_loop_drive":
        drive_limits = MotionLimits(effort=30.0, velocity=1.0, lower=-0.18, upper=0.18)
    elif r.drive == "spring_rewind_roller":
        drive_limits = MotionLimits(
            effort=18.0, velocity=4.0, lower=-1.25 * math.pi, upper=1.25 * math.pi
        )
    else:
        drive_limits = MotionLimits(
            effort=18.0, velocity=4.0, lower=-2.0 * math.pi, upper=2.0 * math.pi
        )
    model.articulation(
        "drive_rotation",
        ArticulationType.REVOLUTE,
        parent=head,
        child=drive_part,
        origin=Origin(xyz=(drive_x + 0.02, -0.005, cass_z + 0.02)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=drive_limits,
    )

    return model


def build_seeded_retractable_patio_awning(seed: int) -> ArticulatedObject:
    return build_retractable_patio_awning(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Author tests
# --------------------------------------------------------------------------- #
def _element_center(ctx, part, name):
    bounds = ctx.part_element_world_aabb(part, elem=name)
    if bounds is None:
        return None
    return tuple((bounds[0][a] + bounds[1][a]) / 2.0 for a in range(3))


def _distance(a, b):
    if a is None or b is None:
        return 0.0
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def run_retractable_patio_awning_tests(
    model: ArticulatedObject,
    config: RetractablePatioAwningConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    head = model.get_part("head")
    front_bar = model.get_part("front_bar")

    # Captured / intentional overlaps (element-scoped), mirroring 001 source.
    # MUST be declared BEFORE the overlap checks so they are honored.
    for index in range(r.arm_count):
        upper = model.get_part(f"upper_arm_{index}")
        fore = model.get_part(f"forearm_{index}")
        ctx.allow_overlap(
            head, upper, elem_a=f"pivot_bracket_{index}", elem_b="shoulder_pin",
            reason="Shoulder pin captured inside its head pivot bracket.",
        )
        ctx.allow_overlap(
            head, upper, elem_a=f"pivot_bracket_{index}", elem_b="arm_beam",
            reason="Arm root seats in the open shoulder bracket around the pivot.",
        )
        ctx.allow_overlap(
            head, upper, elem_a="cassette_lip", elem_b="arm_beam",
            reason="Arm root pivots at the cassette front-lip bracket line.",
        )
        ctx.allow_overlap(
            head, upper, elem_a="cassette_lip", elem_b="shoulder_pin",
            reason="Shoulder pin sits under the cassette front lip.",
        )
        if r.extension_mechanism == "guided_side_rails":
            for rail in ("rail_flange_0", "rail_flange_1"):
                ctx.allow_overlap(
                    head, upper, elem_a=f"pivot_bracket_{index}", elem_b=rail,
                    reason="Guide rail runs through the shoulder carriage bracket.",
                )
        if r.extension_mechanism == "scissor_arms":
            ctx.allow_overlap(
                head, upper, elem_a=f"pivot_bracket_{index}", elem_b="scissor_cross",
                reason="Scissor cross link pivots at the shoulder bracket.",
            )
        # Forearm structural members nest into / fold against the upper arm at
        # the elbow hinge (real telescoping sleeve / folding tongue).
        fore_nest = ["arm_beam", "elbow_pin", "tension_link", "link_bridge_0", "link_bridge_1"]
        upper_nest = ["arm_beam", "elbow_clevis", "tension_link", "link_bridge_0", "link_bridge_1"]
        if r.extension_mechanism == "guided_side_rails":
            fore_nest += ["rail_flange_0", "rail_flange_1"]
            upper_nest += ["rail_flange_0", "rail_flange_1"]
        for fe in fore_nest:
            for ue in upper_nest:
                ctx.allow_overlap(
                    fore, upper, elem_a=fe, elem_b=ue,
                    reason="Forearm members nest/fold against the upper arm at the elbow hinge.",
                )
        ctx.allow_overlap(
            fore, front_bar, elem_a="arm_beam", elem_b=f"front_tab_{index}",
            reason="Arm tip enters the underside front-bar socket.",
        )
        ctx.allow_overlap(
            fore, front_bar, elem_a="front_pin", elem_b=f"front_tab_{index}",
            reason="Front pin captured by the underside front-bar socket.",
        )
        ctx.allow_overlap(
            fore, front_bar, elem_a="front_pin", elem_b="front_bar_body",
            reason="Arm terminal front pin seats against the front-bar body.",
        )
        ctx.allow_overlap(
            fore, front_bar, elem_a="arm_beam", elem_b="front_bar_body",
            reason="Forearm tip enters the front-bar underside as it pushes it out.",
        )
        for tip_elem in ("front_pin", "arm_beam", "tension_link"):
            ctx.allow_overlap(
                fore, front_bar, elem_a=tip_elem, elem_b="front_bar_groove",
                reason="Arm terminal engages the front-bar retention groove.",
            )
        ctx.allow_overlap(
            fore, front_bar, elem_a="tension_link", elem_b="front_bar_body",
            reason="Arm tension link seats against the front-bar body at full extension.",
        )
        ctx.allow_overlap(
            head, front_bar, elem_a="fabric_skin", elem_b=f"front_tab_{index}",
            reason="Front tab hidden inside the sewn fabric / front-bar hem pocket.",
        )
    # Fabric hem terminates at / wraps the front bar (canopy on head, bar separate).
    ctx.allow_overlap(
        head, front_bar, elem_a="fabric_skin", elem_b="front_bar_body",
        reason="Taut canopy hem terminates at and wraps the front bar.",
    )
    # Drive spindle captured in the head drive housing.
    if r.drive == "chain_loop_drive":
        drive_part = model.get_part("drive_part")
        for de in ("drive_sprocket", "sprocket_boss", "chain_strand_0", "chain_strand_1", "chain_return"):
            for he in ("drive_housing", "chain_drive_housing", "chain_gearbox_boss"):
                ctx.allow_overlap(
                    head, drive_part, elem_a=he, elem_b=de,
                    reason="Pull-chain loop drive runs inside its end drive housing.",
                )
    else:
        drive_part = model.get_part("drive_part")
        ctx.allow_overlap(
            head, drive_part,
            elem_a="drive_housing", elem_b="crank_spindle",
            reason="Manual crank spindle seats in the end drive housing.",
        )
        if r.drive == "gearbox_crank":
            ctx.allow_overlap(
                head, drive_part, elem_a="gearbox_input_boss", elem_b="crank_spindle",
                reason="Crank spindle enters the gearbox input boss.",
            )
            ctx.allow_overlap(
                head, drive_part, elem_a="gearbox_input_boss", elem_b="crank_hub",
                reason="Crank hub seats on the gearbox input boss.",
            )
            ctx.allow_overlap(
                head, drive_part, elem_a="drive_housing", elem_b="crank_hub",
                reason="Crank hub seats against the reduction-gearbox housing.",
            )
            ctx.allow_overlap(
                head, drive_part, elem_a="gearbox_cover", elem_b="crank_hub",
                reason="Crank hub runs inside the enclosed gearbox cover.",
            )
            ctx.allow_overlap(
                head, drive_part, elem_a="gearbox_cover", elem_b="crank_spindle",
                reason="Crank spindle passes through the enclosed gearbox cover.",
            )
            ctx.allow_overlap(
                head, drive_part, elem_a="gearbox_input_boss", elem_b="crank_drop",
                reason="Crank drop clears the gearbox input boss as it turns.",
            )
    if r.drive == "spring_rewind_roller":
        roller = model.get_part("fabric_roller")
        ctx.allow_overlap(
            roller, roller,
            elem_a="spring_mandrel", elem_b="spring_cartridge",
            reason="Torsion spring mandrel runs inside the coaxial spring cartridge.",
        )
        for elem in ("roller_tube", "roller_axle", "spring_mandrel", "spring_cartridge"):
            ctx.allow_overlap(
                roller, head, elem_a=elem, elem_b="rewind_bearing",
                reason="Roller end is captured in the spring-rewind end bearing.",
            )

    # Category identity checks.
    fabric_aabb = ctx.part_element_world_aabb(head, elem="fabric_skin")
    ctx.check(
        "canopy spans a broad patio width",
        fabric_aabb is not None
        and (fabric_aabb[1][0] - fabric_aabb[0][0]) >= 3.0
        and (fabric_aabb[1][1] - fabric_aabb[0][1]) >= 1.8,
        details=f"fabric_aabb={fabric_aabb}",
    )
    ctx.check(
        "one coherent awning assembly",
        {p.name for p in model.parts}
        == {"head", "fabric_roller", "front_bar", "drive_part"}
        | {f"upper_arm_{i}" for i in range(r.arm_count)}
        | {f"forearm_{i}" for i in range(r.arm_count)},
        details=f"parts={sorted(p.name for p in model.parts)}",
    )

    # Joint type / axis expectations.
    roller_joint = model.get_articulation("roller_rotation")
    ctx.check(
        "roller is a revolute winder about x",
        roller_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(roller_joint.axis) == (1.0, 0.0, 0.0),
        details=f"type={roller_joint.articulation_type}, axis={roller_joint.axis}",
    )
    exp_shoulder = (
        ArticulationType.PRISMATIC
        if r.extension_mechanism == "guided_side_rails"
        else ArticulationType.REVOLUTE
    )
    exp_elbow = (
        ArticulationType.PRISMATIC
        if r.extension_mechanism in ("guided_side_rails", "telescoping_arms")
        else ArticulationType.REVOLUTE
    )
    for index in range(r.arm_count):
        sj = model.get_articulation(f"shoulder_hinge_{index}")
        ej = model.get_articulation(f"elbow_hinge_{index}")
        ctx.check(
            f"shoulder_hinge_{index} type matches extension mechanism",
            sj.articulation_type == exp_shoulder,
            details=f"got={sj.articulation_type}, want={exp_shoulder}",
        )
        ctx.check(
            f"elbow_hinge_{index} type matches extension mechanism",
            ej.articulation_type == exp_elbow,
            details=f"got={ej.articulation_type}, want={exp_elbow}",
        )

    # Targeted motion semantics (Rule 5) — one per key mechanism.
    roller_rest = _element_center(ctx, model.get_part("fabric_roller"), "roller_seam")
    with ctx.pose({roller_joint: 0.70}):
        roller_moved = _element_center(ctx, model.get_part("fabric_roller"), "roller_seam")
    ctx.check(
        "fabric roller visibly rotates",
        _distance(roller_rest, roller_moved) > 0.03,
        details=f"rest={roller_rest}, moved={roller_moved}",
    )

    front_joint = model.get_articulation("front_bar_pitch")
    bar_rest = ctx.part_world_aabb(front_bar)
    with ctx.pose({front_joint: 0.18}):
        bar_tilt = ctx.part_world_aabb(front_bar)
    ctx.check(
        "front bar pitch changes bar attitude",
        bar_rest is not None
        and bar_tilt is not None
        and abs((bar_rest[1][2]) - (bar_tilt[1][2])) > 0.006,
        details=f"rest={bar_rest}, tilt={bar_tilt}",
    )

    # At least the first arm folds/extends visibly.
    fore0 = model.get_part("forearm_0")
    sj0 = model.get_articulation("shoulder_hinge_0")
    ej0 = model.get_articulation("elbow_hinge_0")
    def _far_limit(joint):
        lo, hi = joint.motion_limits.lower, joint.motion_limits.upper
        return lo if abs(lo) >= abs(hi) else hi

    tip_rest = _element_center(ctx, fore0, "front_pin")
    with ctx.pose({sj0: _far_limit(sj0)}):
        tip_shoulder = _element_center(ctx, fore0, "front_pin")
    with ctx.pose({ej0: _far_limit(ej0)}):
        tip_elbow = _element_center(ctx, fore0, "front_pin")
    ctx.check(
        "support arm 0 moves at the shoulder",
        _distance(tip_rest, tip_shoulder) > 0.05,
        details=f"rest={tip_rest}, moved={tip_shoulder}",
    )
    ctx.check(
        "support arm 0 moves at the elbow",
        _distance(tip_rest, tip_elbow) > 0.05,
        details=f"rest={tip_rest}, moved={tip_elbow}",
    )

    drive_joint = model.get_articulation("drive_rotation")
    drive_grip = "chain_return" if r.drive == "chain_loop_drive" else "crank_grip"
    drive_rest = _element_center(ctx, model.get_part("drive_part"), drive_grip)
    with ctx.pose({drive_joint: min(0.60, drive_joint.motion_limits.upper)}):
        drive_moved = _element_center(ctx, model.get_part("drive_part"), drive_grip)
    ctx.check(
        "drive visibly rotates",
        _distance(drive_rest, drive_moved) > 0.01,
        details=f"rest={drive_rest}, moved={drive_moved}",
    )

    # Rule 5 sampled-pose collision sweep.
    joint_count = 3 + 2 * r.arm_count
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=min(128, max(32, 1 + 4 * joint_count)),
        ignore_fixed=True,
    )

    return ctx.report()


__all__ = [
    "SupportTopology",
    "ExtensionMechanism",
    "Drive",
    "PaletteStyle",
    "RetractablePatioAwningConfig",
    "ResolvedRetractablePatioAwningConfig",
    "config_from_seed",
    "resolve_config",
    "with_overrides",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_retractable_patio_awning",
    "build_seeded_retractable_patio_awning",
    "run_retractable_patio_awning_tests",
]
