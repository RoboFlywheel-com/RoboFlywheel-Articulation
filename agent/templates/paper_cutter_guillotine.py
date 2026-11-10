# SPDX-License-Identifier: Apache-2.0

"""Paper cutter guillotine — modular procedural template.

A grounded ``base`` (Slot 1: cutting bed + printed grid/ruler + diagonal
angle guides + rear fence + cutting-strip anvil + rubber feet + rear-corner
hinge hardware, all baked as visuals) carrying a single REVOLUTE
``blade_arm`` (Slot 2) that swings about the rear-corner hinge line. The
blade runs along the LONG edge of the bed (≈ ``base_x``) like the 5-star
samples — hinged at the ``-x`` corner, handle protruding past the ``+x``
end, cutting edge riding just above the anvil strip when closed.

Slot 3 picks the pivot_mount topology: ``baked_clevis_in_base`` /
``baked_pin_in_base`` (2-part main trunk) vs ``separate_pivot_bracket``
(introduces a FIXED ``pivot_bracket`` part, making the blade_arm a
grandchild of the base). Slot 4 gates an optional second moving part
(hold_down bar PRISMATIC, finger_guard REVOLUTE, lock_handle REVOLUTE, or
side_gauge PRISMATIC); each bakes its own anchor hardware onto the base
only when selected.

Geometry fidelity (Rule 3): ``mesh_rrect_bed`` / ``cadquery_fillet_bed``
build real ``ExtrudeGeometry`` / cadquery boards; ``extrude_profile_arm`` /
``lofted_eyelet_arm`` build real ``ExtrudeGeometry`` / ``section_loft``
spines. The hinge axis is ``(0, -1, 0)`` (horizontal, perpendicular to the
blade) and travel is 0 → ``blade_upper`` rad.

Identity invariant: every seed has exactly one REVOLUTE joint joining the
blade_arm to base (or to pivot_bracket).

seed=0 anchor: prim_box_bed + prim_box_arm + baked_clevis_in_base + none.
"""

from __future__ import annotations

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
    ExtrudeGeometry,
    Inertial,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    section_loft,
)

__modular__ = True


BaseStyle = Literal[
    "prim_box_bed", "mesh_rrect_bed", "cadquery_fillet_bed", "plinth_plus_plate_bed"
]
ArmStyle = Literal[
    "prim_box_arm", "extrude_profile_arm", "cadquery_sloped_arm", "lofted_eyelet_arm"
]
PivotMount = Literal["baked_clevis_in_base", "baked_pin_in_base", "separate_pivot_bracket"]
SecondDof = Literal[
    "none",
    "hold_down_bar_prismatic",
    "finger_guard_revolute",
    "lock_handle_revolute",
    "side_gauge_prismatic",
]
PaletteTheme = Literal["natural_steel", "office_white", "industrial_black", "red_safety"]

BASE_MODULES: tuple[BaseStyle, ...] = (
    "prim_box_bed",
    "mesh_rrect_bed",
    "cadquery_fillet_bed",
    "plinth_plus_plate_bed",
)
ARM_MODULES: tuple[ArmStyle, ...] = (
    "prim_box_arm",
    "extrude_profile_arm",
    "cadquery_sloped_arm",
    "lofted_eyelet_arm",
)
PIVOT_MODULES: tuple[PivotMount, ...] = (
    "baked_clevis_in_base",
    "baked_pin_in_base",
    "separate_pivot_bracket",
)
DOF_MODULES: tuple[SecondDof, ...] = (
    "none",
    "hold_down_bar_prismatic",
    "finger_guard_revolute",
    "lock_handle_revolute",
    "side_gauge_prismatic",
)

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "natural_steel": {
        "board": (0.55, 0.40, 0.22, 1.0),
        "steel": (0.62, 0.64, 0.66, 1.0),
        "blade": (0.85, 0.86, 0.88, 1.0),
        "grip": (0.12, 0.13, 0.15, 1.0),
        "mat": (0.20, 0.30, 0.26, 1.0),
        "rule": (0.92, 0.91, 0.86, 1.0),
        "clear": (0.62, 0.78, 0.92, 0.35),
        "red": (0.78, 0.10, 0.10, 1.0),
        "dark": (0.10, 0.10, 0.11, 1.0),
    },
    "office_white": {
        "board": (0.90, 0.90, 0.88, 1.0),
        "steel": (0.55, 0.57, 0.60, 1.0),
        "blade": (0.78, 0.80, 0.82, 1.0),
        "grip": (0.10, 0.10, 0.12, 1.0),
        "mat": (0.22, 0.34, 0.30, 1.0),
        "rule": (0.20, 0.20, 0.22, 1.0),
        "clear": (0.65, 0.80, 0.92, 0.35),
        "red": (0.85, 0.18, 0.18, 1.0),
        "dark": (0.14, 0.14, 0.15, 1.0),
    },
    "industrial_black": {
        "board": (0.16, 0.16, 0.18, 1.0),
        "steel": (0.55, 0.57, 0.60, 1.0),
        "blade": (0.82, 0.84, 0.86, 1.0),
        "grip": (0.78, 0.10, 0.10, 1.0),
        "mat": (0.10, 0.11, 0.12, 1.0),
        "rule": (0.85, 0.85, 0.85, 1.0),
        "clear": (0.45, 0.62, 0.78, 0.35),
        "red": (0.85, 0.12, 0.12, 1.0),
        "dark": (0.05, 0.05, 0.05, 1.0),
    },
    "red_safety": {
        "board": (0.78, 0.10, 0.10, 1.0),
        "steel": (0.55, 0.57, 0.60, 1.0),
        "blade": (0.82, 0.84, 0.86, 1.0),
        "grip": (0.14, 0.14, 0.16, 1.0),
        "mat": (0.40, 0.10, 0.10, 1.0),
        "rule": (0.94, 0.94, 0.94, 1.0),
        "clear": (0.65, 0.80, 0.92, 0.35),
        "red": (0.95, 0.15, 0.15, 1.0),
        "dark": (0.10, 0.10, 0.12, 1.0),
    },
}


@dataclass(frozen=True)
class PaperCutterGuillotineConfig:
    base_style: BaseStyle | None = None
    arm_style: ArmStyle | None = None
    pivot_mount: PivotMount | None = None
    second_dof: SecondDof | None = None
    palette_theme: PaletteTheme = "natural_steel"
    base_x: float = 0.52
    base_y: float = 0.36
    base_thickness: float = 0.026
    arm_length: float = 0.52
    pivot_z: float = 0.095
    blade_upper: float = 1.45


@dataclass(frozen=True)
class ResolvedPaperCutterGuillotineConfig:
    base_style: BaseStyle
    arm_style: ArmStyle
    pivot_mount: PivotMount
    second_dof: SecondDof
    palette_theme: PaletteTheme
    base_x: float
    base_y: float
    base_thickness: float
    arm_length: float
    pivot_z: float
    blade_upper: float
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def config_from_seed(seed: int) -> PaperCutterGuillotineConfig:
    if seed == 0:
        return PaperCutterGuillotineConfig(
            base_style="prim_box_bed",
            arm_style="prim_box_arm",
            pivot_mount="baked_clevis_in_base",
            second_dof="none",
            palette_theme="natural_steel",
            base_x=0.52,
            base_y=0.36,
            base_thickness=0.026,
            arm_length=0.52,
            pivot_z=0.095,
            blade_upper=1.45,
        )
    rng = random.Random(seed)
    base_x = round(rng.uniform(0.42, 0.76), 4)
    # The blade runs the length of the bed; handle protrudes a little past +x.
    arm_length = round(base_x * rng.uniform(0.96, 1.08), 4)
    return PaperCutterGuillotineConfig(
        base_style=rng.choice(BASE_MODULES),  # type: ignore[arg-type]
        arm_style=rng.choice(ARM_MODULES),  # type: ignore[arg-type]
        pivot_mount=rng.choice(PIVOT_MODULES),  # type: ignore[arg-type]
        second_dof=rng.choice(DOF_MODULES),  # type: ignore[arg-type]
        palette_theme=rng.choice(tuple(PALETTES.keys())),  # type: ignore[arg-type]
        base_x=base_x,
        base_y=round(rng.uniform(0.28, 0.46), 4),
        base_thickness=round(rng.uniform(0.020, 0.040), 4),
        arm_length=arm_length,
        pivot_z=round(rng.uniform(0.078, 0.125), 4),
        blade_upper=round(rng.uniform(1.20, 1.55), 3),
    )


def resolve_config(config: PaperCutterGuillotineConfig) -> ResolvedPaperCutterGuillotineConfig:
    base = config.base_style or "prim_box_bed"
    arm = config.arm_style or "prim_box_arm"
    pivot = config.pivot_mount or "baked_clevis_in_base"
    dof = config.second_dof or "none"
    for value, pool, label in (
        (base, BASE_MODULES, "base_style"),
        (arm, ARM_MODULES, "arm_style"),
        (pivot, PIVOT_MODULES, "pivot_mount"),
        (dof, DOF_MODULES, "second_dof"),
    ):
        if value not in pool:
            raise ValueError(f"Unsupported {label}: {value!r}")
    if config.palette_theme not in PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme!r}")
    return ResolvedPaperCutterGuillotineConfig(
        base_style=base,
        arm_style=arm,
        pivot_mount=pivot,
        second_dof=dof,
        palette_theme=config.palette_theme,
        base_x=_clamp(config.base_x, 0.34, 0.90),
        base_y=_clamp(config.base_y, 0.24, 0.52),
        base_thickness=_clamp(config.base_thickness, 0.015, 0.055),
        arm_length=_clamp(config.arm_length, 0.30, 0.95),
        pivot_z=_clamp(config.pivot_z, 0.065, 0.150),
        blade_upper=_clamp(config.blade_upper, 1.10, 1.62),
        palette=dict(PALETTES[config.palette_theme]),
    )


# --------------------------------------------------------------------------- #
# Shared geometry constants (derived from a resolved config)
# --------------------------------------------------------------------------- #


HUB_RADIUS = 0.020
HUB_LENGTH = 0.052
CUT_INSET = 0.034  # cut line distance inboard from the front (-y) edge


def _pivot_x(r: ResolvedPaperCutterGuillotineConfig) -> float:
    return -r.base_x * 0.5 + max(0.058, r.base_x * 0.11)


def _cut_y(r: ResolvedPaperCutterGuillotineConfig) -> float:
    return -r.base_y * 0.5 + CUT_INSET


def _pivot_world_z(r: ResolvedPaperCutterGuillotineConfig) -> float:
    return r.base_thickness + r.pivot_z


# --------------------------------------------------------------------------- #
# Slot 1: base board (style-specific) + shared deck/hinge decorations
# --------------------------------------------------------------------------- #


def _rrect_board_mesh(x: float, y: float, t: float):
    profile = rounded_rect_profile(x, y, radius=min(0.024, 0.45 * min(x, y)), corner_segments=10)
    geom = ExtrudeGeometry.from_z0(profile, t)
    return mesh_from_geometry(geom, "paper_cutter_rrect_board")


def _cadquery_fillet_board_mesh(x: float, y: float, t: float):
    import cadquery as cq

    radius = min(0.020, 0.45 * min(x, y))
    solid = (
        cq.Workplane("XY").box(x, y, t).edges("|Z").fillet(radius).translate((0.0, 0.0, t / 2.0))
    )
    return mesh_from_cadquery(solid, "paper_cutter_fillet_board", tolerance=0.0012)


def _build_base_board(p, r: ResolvedPaperCutterGuillotineConfig) -> float:
    """Emit the style-specific board. Returns the bed-top z (= base_thickness)."""
    style = r.base_style
    X, Y, T = r.base_x, r.base_y, r.base_thickness

    if style == "prim_box_bed":
        p.visual(
            Box((X, Y, T)),
            origin=Origin(xyz=(0.0, 0.0, T * 0.5)),
            material="board",
            name="bed_board", material_class_id="wood.engineered_board",
        )
    elif style == "mesh_rrect_bed":
        p.visual(_rrect_board_mesh(X, Y, T), material="board", name="bed_board", material_class_id="wood.engineered_board")
    elif style == "cadquery_fillet_bed":
        p.visual(_cadquery_fillet_board_mesh(X, Y, T), material="board", name="bed_board", material_class_id="wood.engineered_board")
    else:  # plinth_plus_plate_bed
        plinth_h = T * 0.6
        plate_h = T * 0.5
        p.visual(
            Box((X * 0.94, Y * 0.94, plinth_h)),
            origin=Origin(xyz=(0.0, 0.0, plinth_h * 0.5)),
            material="dark",
            name="plinth", material_class_id="plastic.opaque_glossy_molded",
        )
        p.visual(
            Box((X, Y, plate_h)),
            origin=Origin(xyz=(0.0, 0.0, plinth_h + plate_h * 0.5 - 0.004)),
            material="board",
            name="bed_plate", material_class_id="wood.engineered_board",
        )
        return plinth_h + plate_h - 0.004
    return T


def _build_base_deck(p, r: ResolvedPaperCutterGuillotineConfig, top: float) -> None:
    """Shared printed deck: cutting mat, ruler, grid, angle guides, fences,
    anvil cutting strip, and rubber feet. Common to every base style."""
    X, Y = r.base_x, r.base_y
    cut_y = _cut_y(r)

    # Inset cutting mat covering the working area (behind the cut line).
    mat_w = X * 0.90
    mat_d = Y * 0.74
    mat_cy = cut_y + mat_d * 0.5 + 0.006
    p.visual(
        Box((mat_w, mat_d, 0.0010)),
        origin=Origin(xyz=(0.0, mat_cy, top + 0.0005)),
        material="mat",
        name="cutting_mat", material_class_id="rubber.smooth_plain",
    )

    # Rear fence (paper backstop) along the +y edge.
    fence_h = 0.030
    p.visual(
        Box((X * 0.98, 0.014, fence_h)),
        origin=Origin(xyz=(0.0, Y * 0.5 - 0.009, top + fence_h * 0.5)),
        material="dark",
        name="rear_fence", material_class_id="plastic.opaque_glossy_molded",
    )
    # Side fence / squaring rail along the -x edge.
    p.visual(
        Box((0.014, Y * 0.92, 0.022)),
        origin=Origin(xyz=(-X * 0.5 + 0.009, 0.0, top + 0.011)),
        material="steel",
        name="side_fence", material_class_id="metal.stainless_matte",
    )
    p.visual(
        Box((0.006, Y * 0.88, 0.0006)),
        origin=Origin(xyz=(-X * 0.5 + 0.020, 0.0, top + 0.0003)),
        material="rule",
        name="side_ruler", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )

    # Steel anvil / cutting strip running under the blade along the cut line.
    p.visual(
        Box((X * 0.94, 0.020, 0.003)),
        origin=Origin(xyz=(0.0, cut_y, top + 0.0015)),
        material="steel",
        name="cutting_strip", material_class_id="metal.stainless_matte",
    )
    p.visual(
        Box((X * 0.94, 0.0022, 0.0008)),
        origin=Origin(xyz=(0.0, cut_y + 0.012, top + 0.0004)),
        material="red",
        name="cut_line_indicator", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )

    # Printed measuring grid on the deck (behind the cut line).
    grid_y0 = cut_y + 0.020
    grid_y1 = Y * 0.5 - 0.022
    grid_depth = max(0.04, grid_y1 - grid_y0)
    grid_cy = (grid_y0 + grid_y1) * 0.5
    for i in range(7):
        gx = -X * 0.40 + (i / 6.0) * X * 0.80
        thick = 0.0022 if i % 2 == 0 else 0.0013
        p.visual(
            Box((thick, grid_depth, 0.0006)),
            origin=Origin(xyz=(gx, grid_cy, top + 0.0003)),
            material="rule",
            name=f"grid_x_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    for j in range(4):
        gy = grid_y0 + (j + 0.5) / 4.0 * grid_depth
        p.visual(
            Box((X * 0.78, 0.0013, 0.0006)),
            origin=Origin(xyz=(0.0, gy, top + 0.0003)),
            material="rule",
            name=f"grid_y_{j}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    # Rubber feet at the four corners, proud below the board.
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.visual(
                Cylinder(radius=0.020, length=0.012),
                origin=Origin(xyz=(sx * (X * 0.5 - 0.030), sy * (Y * 0.5 - 0.030), 0.002)),
                material="grip",
                name=f"foot_{'r' if sx > 0 else 'l'}_{'b' if sy > 0 else 'f'}", material_class_id="rubber.smooth_plain",
            )


def _build_clevis_hinge(p, r: ResolvedPaperCutterGuillotineConfig, top: float) -> None:
    """baked_clevis_in_base: bolted pad + twin cheeks + rear bridge + pin caps
    + a fat pivot pin (along y), all baked onto the base. The blade-arm hub
    closes over the pin (captured-pin overlap)."""
    px = _pivot_x(r)
    cy = _cut_y(r)
    pz = r.pivot_z
    half = HUB_LENGTH * 0.5
    p.visual(
        Box((0.085, HUB_LENGTH + 0.044, 0.014)),
        origin=Origin(xyz=(px, cy, top + 0.007)),
        material="dark",
        name="hinge_pad", material_class_id="metal.blackened_gunmetal",
    )
    for sgn, side in ((+1, "rear"), (-1, "front")):
        p.visual(
            Box((0.060, 0.012, pz + 0.012)),
            origin=Origin(xyz=(px, cy + sgn * (half + 0.010), top + (pz + 0.012) * 0.5)),
            material="dark",
            name=f"cheek_{side}", material_class_id="metal.blackened_gunmetal",
        )
    p.visual(
        Box((0.016, HUB_LENGTH + 0.040, pz)),
        origin=Origin(xyz=(px - 0.034, cy, top + pz * 0.5)),
        material="dark",
        name="bracket_bridge", material_class_id="metal.blackened_gunmetal",
    )
    for sgn, side in ((+1, "rear"), (-1, "front")):
        p.visual(
            Cylinder(radius=0.013, length=0.014),
            origin=Origin(
                xyz=(px, cy + sgn * (half + 0.012), top + pz),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material="steel",
            name=f"pin_cap_{side}", material_class_id="metal.stainless_matte",
        )
    p.visual(
        Cylinder(radius=0.008, length=HUB_LENGTH + 0.050),
        origin=Origin(xyz=(px, cy, top + pz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="steel",
        name="pivot_pin", material_class_id="metal.stainless_matte",
    )


def _build_pin_hinge(p, r: ResolvedPaperCutterGuillotineConfig, top: float) -> None:
    """baked_pin_in_base: a solid hinge block + a half-shell cap and an
    exposed pivot pin. 2-part trunk, distinct hardware silhouette."""
    px = _pivot_x(r)
    cy = _cut_y(r)
    pz = r.pivot_z
    p.visual(
        Box((0.066, HUB_LENGTH + 0.050, pz + 0.010)),
        origin=Origin(xyz=(px - 0.006, cy, top + (pz + 0.010) * 0.5)),
        material="dark",
        name="hinge_block", material_class_id="metal.blackened_gunmetal",
    )
    p.visual(
        Cylinder(radius=0.015, length=HUB_LENGTH + 0.026),
        origin=Origin(xyz=(px, cy, top + pz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="steel",
        name="hinge_cap", material_class_id="metal.stainless_matte",
    )
    p.visual(
        Cylinder(radius=0.008, length=HUB_LENGTH + 0.058),
        origin=Origin(xyz=(px, cy, top + pz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="steel",
        name="pivot_pin", material_class_id="metal.stainless_matte",
    )


def _build_bracket_mount_pad(p, r: ResolvedPaperCutterGuillotineConfig, top: float) -> None:
    """separate_pivot_bracket: only a bolted mount pad is baked on the base;
    the upright clevis lives on the independent ``pivot_bracket`` part."""
    px = _pivot_x(r)
    cy = _cut_y(r)
    p.visual(
        Box((0.080, HUB_LENGTH + 0.048, 0.012)),
        origin=Origin(xyz=(px, cy, top + 0.006)),
        material="dark",
        name="bracket_mount_pad", material_class_id="metal.blackened_gunmetal",
    )


def _build_base(model: ArticulatedObject, r: ResolvedPaperCutterGuillotineConfig) -> float:
    """Emit the cutting base. The blade hinge axis is along y at
    ``(_pivot_x, _cut_y, base_thickness + pivot_z)``; the blade swings up
    in +z. Returns the bed-top z used by the deck."""
    p = model.part("base")
    top = _build_base_board(p, r)
    _build_base_deck(p, r, top)

    if r.pivot_mount == "baked_clevis_in_base":
        _build_clevis_hinge(p, r, top)
    elif r.pivot_mount == "baked_pin_in_base":
        _build_pin_hinge(p, r, top)
    else:
        _build_bracket_mount_pad(p, r, top)

    p.inertial = Inertial.from_geometry(
        Box((r.base_x, r.base_y, r.base_thickness)),
        mass=2.6,
        origin=Origin(xyz=(0.0, 0.0, r.base_thickness * 0.5)),
    )
    return top


# --------------------------------------------------------------------------- #
# Slot 3 (separate variant): pivot_bracket
# --------------------------------------------------------------------------- #


def _build_pivot_bracket(model: ArticulatedObject, r: ResolvedPaperCutterGuillotineConfig) -> None:
    """Independent FIXED pivot_bracket. Part frame origin sits on the bed top
    (the mount-pad interface). A seat + backbone column rises to the
    bracket_axle (along y) at local z = pivot_z, where the blade_arm pins."""
    p = model.part("pivot_bracket")
    pz = r.pivot_z
    seat_h = 0.012
    half = HUB_LENGTH * 0.5
    p.visual(
        Box((0.062, HUB_LENGTH + 0.046, seat_h)),
        origin=Origin(xyz=(0.0, 0.0, seat_h * 0.5)),
        material="dark",
        name="bracket_seat", material_class_id="metal.blackened_gunmetal",
    )
    p.visual(
        Box((0.026, HUB_LENGTH + 0.040, pz)),
        origin=Origin(xyz=(-0.014, 0.0, pz * 0.5 + 0.002)),
        material="dark",
        name="bracket_backbone", material_class_id="metal.blackened_gunmetal",
    )
    for sgn, side in ((+1, "rear"), (-1, "front")):
        p.visual(
            Box((0.020, 0.012, 0.040)),
            origin=Origin(xyz=(0.0, sgn * (half + 0.010), pz)),
            material="dark",
            name=f"bracket_cheek_{side}", material_class_id="metal.blackened_gunmetal",
        )
    p.visual(
        Cylinder(radius=0.008, length=HUB_LENGTH + 0.030),
        origin=Origin(xyz=(0.0, 0.0, pz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="steel",
        name="bracket_axle", material_class_id="metal.stainless_matte",
    )
    p.inertial = Inertial.from_geometry(
        Box((0.062, HUB_LENGTH + 0.046, pz + 0.040)),
        mass=0.5,
        origin=Origin(xyz=(0.0, 0.0, (pz + 0.040) * 0.5)),
    )


# --------------------------------------------------------------------------- #
# Slot 2: blade_arm
# --------------------------------------------------------------------------- #


def _arm_beam_extrude_mesh(length: float, depth: float, height: float):
    """Tapered top spine — wider/taller near the hinge, narrowing to the tip.
    Profile lies in the x/y plane (planform), extruded in z (height)."""
    hd = depth * 0.5
    profile = [
        (0.0, -hd),
        (length * 0.18, -hd * 1.05),
        (length * 0.55, -hd * 0.82),
        (length * 0.86, -hd * 0.60),
        (length, -hd * 0.46),
        (length, hd * 0.46),
        (length * 0.86, hd * 0.60),
        (length * 0.55, hd * 0.82),
        (length * 0.18, hd * 1.05),
        (0.0, hd),
    ]
    geom = ExtrudeGeometry.centered(profile, height)
    return mesh_from_geometry(geom, "paper_cutter_arm_beam_extrude")


def _arm_beam_loft_mesh(length: float, depth: float, height: float):
    """Lofted 3D beam: rounded y/z cross-sections swept along x, tapering to
    the tip. Mirrors the section_loft arm spine of the 5-star bracket sample."""

    def _section(x_pos: float, w_y: float, h_z: float, cz: float):
        radius = min(w_y, h_z) * 0.32
        return [
            (x_pos, yy, zz + cz)
            for zz, yy in rounded_rect_profile(h_z, w_y, radius, corner_segments=6)
        ]

    spec = [
        _section(0.0, depth * 1.0, height * 1.0, 0.0),
        _section(length * 0.30, depth * 1.04, height * 0.96, -0.001),
        _section(length * 0.66, depth * 0.84, height * 0.80, -0.003),
        _section(length, depth * 0.58, height * 0.62, -0.005),
    ]
    return mesh_from_geometry(section_loft(spec), "paper_cutter_arm_beam_loft")


def _add_blade_and_handle(p, r: ResolvedPaperCutterGuillotineConfig, drop: float) -> None:
    """Shared blade plate + honed edge + handle (posts + long grip + end cap).
    The blade hangs ``drop`` below the hub so the honed edge rides just above
    the anvil strip when closed."""
    L = r.arm_length
    blade_top = 0.004
    plate_h = drop + blade_top
    plate_cz = (blade_top - drop) * 0.5
    p.visual(
        Box((L * 0.96, 0.012, plate_h)),
        origin=Origin(xyz=(L * 0.50, 0.0, plate_cz)),
        material="blade",
        name="blade_plate", material_class_id="metal.brushed_silver",
    )
    p.visual(
        Box((L * 0.93, 0.016, 0.006)),
        origin=Origin(xyz=(L * 0.50, 0.0, -drop + 0.003)),
        material="blade",
        name="sharp_edge", material_class_id="metal.brushed_silver",
    )
    # Handle: two posts lifting a long grip rail near the free (+x) end.
    for tag, hx in (("rear", L * 0.60), ("front", L * 0.92)):
        p.visual(
            Cylinder(radius=0.007, length=0.048),
            origin=Origin(xyz=(hx, 0.0, 0.030)),
            material="dark",
            name=f"handle_post_{tag}", material_class_id="metal.blackened_gunmetal",
        )
    p.visual(
        Cylinder(radius=0.016, length=L * 0.42),
        origin=Origin(xyz=(L * 0.76, 0.0, 0.052), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="grip",
        name="handle_grip", material_class_id="rubber.smooth_plain",
    )
    p.visual(
        Sphere(radius=0.018),
        origin=Origin(xyz=(L * 0.98, 0.0, 0.052)),
        material="grip",
        name="handle_end_cap", material_class_id="rubber.smooth_plain",
    )
    p.inertial = Inertial.from_geometry(
        Box((L, 0.05, drop + 0.06)),
        mass=0.6,
        origin=Origin(xyz=(L * 0.5, 0.0, -drop * 0.3)),
    )


def _build_blade_arm(model: ArticulatedObject, r: ResolvedPaperCutterGuillotineConfig) -> None:
    """Emit blade_arm. Part frame origin is at the hinge — the hub (a y-axis
    barrel) covers (0,0,0). The blade extends +x and hangs down toward the
    bed; the handle protrudes past the +x tip."""
    style = r.arm_style
    L = r.arm_length
    drop = max(0.045, r.pivot_z - 0.005)
    p = model.part("blade_arm")

    # Hinge hub (barrel along y) covers the part origin for every style.
    p.visual(
        Cylinder(radius=HUB_RADIUS, length=HUB_LENGTH),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="steel",
        name="hinge_hub", material_class_id="metal.stainless_matte",
    )

    if style == "prim_box_arm":
        p.visual(
            Box((L * 0.99, 0.026, 0.022)),
            origin=Origin(xyz=(L * 0.50, 0.0, 0.006)),
            material="steel",
            name="arm_spine", material_class_id="metal.stainless_matte",
        )
    elif style == "extrude_profile_arm":
        # Mesh profile runs 0..length along x, so place at the hub (x=0).
        p.visual(
            _arm_beam_extrude_mesh(L * 0.99, 0.030, 0.024),
            origin=Origin(xyz=(0.0, 0.0, 0.006)),
            material="steel",
            name="arm_spine", material_class_id="metal.stainless_matte",
        )
    elif style == "cadquery_sloped_arm":
        # A sloped/raked spine: lofted beam plus a red top fillet rail.
        p.visual(
            _arm_beam_loft_mesh(L * 0.99, 0.028, 0.024),
            origin=Origin(xyz=(0.0, 0.0, 0.006)),
            material="red",
            name="arm_spine", material_class_id="metal.paint_coated",
        )
        p.visual(
            Box((L * 0.70, 0.020, 0.008)),
            origin=Origin(xyz=(L * 0.55, 0.0, 0.018)),
            material="steel",
            name="spine_cap", material_class_id="metal.stainless_matte",
        )
    else:  # lofted_eyelet_arm
        # Eyelet sleeve over the hub + a lofted tapered beam.
        p.visual(
            Cylinder(radius=HUB_RADIUS + 0.008, length=0.030),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="steel",
            name="pivot_eyelet", material_class_id="metal.stainless_matte",
        )
        p.visual(
            _arm_beam_loft_mesh(L * 0.99, 0.030, 0.026),
            origin=Origin(xyz=(0.0, 0.0, 0.006)),
            material="steel",
            name="arm_spine", material_class_id="metal.stainless_matte",
        )

    _add_blade_and_handle(p, r, drop)


# --------------------------------------------------------------------------- #
# Slot 4: second DOF parts — each bakes its own anchor on the base
# --------------------------------------------------------------------------- #


def _build_hold_down(
    model: ArticulatedObject, r: ResolvedPaperCutterGuillotineConfig, base, top: float
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Vertical paper clamp: a bar on two guide posts that slides down to
    pinch paper against the bed. Anchored on baked guide posts."""
    X = r.base_x
    cut_y = _cut_y(r)
    span = X * 0.22
    hy = cut_y + 0.085
    post_h = 0.100
    # Baked guide posts on the base.
    for sgn, tag in ((-1, "l"), (+1, "r")):
        base.visual(
            Cylinder(radius=0.011, length=post_h),
            origin=Origin(xyz=(sgn * span, hy, top + post_h * 0.5)),
            material="steel",
            name=f"hold_down_post_{tag}", material_class_id="metal.stainless_matte",
        )
    # Moving clamp. Frame origin at the LEFT post top; +x toward the right post.
    p = model.part("hold_down")
    for lx, tag in ((0.0, "l"), (2 * span, "r")):
        p.visual(
            Cylinder(radius=0.016, length=0.030),
            origin=Origin(xyz=(lx, 0.0, 0.0)),
            material="steel",
            name=f"slider_sleeve_{tag}", material_class_id="metal.stainless_matte",
        )
    p.visual(
        Box((2 * span + 0.040, 0.030, 0.016)),
        origin=Origin(xyz=(span, 0.0, -0.022)),
        material="steel",
        name="clamp_bar", material_class_id="metal.stainless_matte",
    )
    p.visual(
        Box((2 * span + 0.010, 0.022, 0.005)),
        origin=Origin(xyz=(span, 0.0, -0.032)),
        material="grip",
        name="clamp_pad", material_class_id="rubber.smooth_plain",
    )
    p.visual(
        Cylinder(radius=0.012, length=0.052),
        origin=Origin(xyz=(span, -0.041, -0.010), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="grip",
        name="clamp_handle", material_class_id="rubber.smooth_plain",
    )
    p.inertial = Inertial.from_geometry(
        Box((2 * span + 0.05, 0.06, 0.060)),
        mass=0.12,
        origin=Origin(xyz=(span, 0.0, -0.018)),
    )
    return (-span, hy, top + post_h), (0.0, 0.0, 1.0)


def _build_finger_guard(
    model: ArticulatedObject, r: ResolvedPaperCutterGuillotineConfig, base, top: float
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Transparent finger guard that flips up about the cut-line axis (x).
    Anchored on a baked hinge rod carried by two stands."""
    X = r.base_x
    cut_y = _cut_y(r)
    rod_y = cut_y - 0.008
    rod_z = top + 0.024
    panel_w = X * 0.66
    # Baked hinge rod + stands.
    for sgn, tag in ((-1, "l"), (+1, "r")):
        base.visual(
            Box((0.012, 0.012, 0.024)),
            origin=Origin(xyz=(sgn * X * 0.28, rod_y, top + 0.012)),
            material="steel",
            name=f"guard_stand_{tag}", material_class_id="metal.stainless_matte",
        )
    base.visual(
        Cylinder(radius=0.007, length=panel_w + 0.02),
        origin=Origin(xyz=(0.0, rod_y, rod_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="steel",
        name="guard_hinge_rod", material_class_id="metal.stainless_matte",
    )
    # Moving guard. Frame origin at the rod; panel rises in +z.
    p = model.part("finger_guard")
    panel_h = 0.085
    p.visual(
        Cylinder(radius=0.010, length=panel_w + 0.010),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material="steel",
        name="guard_knuckle", material_class_id="metal.stainless_matte",
    )
    p.visual(
        Box((panel_w, 0.004, panel_h)),
        origin=Origin(xyz=(0.0, 0.0, panel_h * 0.5)),
        material="clear",
        name="clear_panel", material_class_id="plastic.clear_rigid",
    )
    for k, frac in enumerate((0.2, 0.5, 0.8)):
        p.visual(
            Box((panel_w * 0.04, 0.010, 0.030)),
            origin=Origin(xyz=(-panel_w * 0.5 + frac * panel_w, 0.0, 0.020)),
            material="steel",
            name=f"clip_loop_{k}", material_class_id="metal.stainless_matte",
        )
    p.inertial = Inertial.from_geometry(
        Box((panel_w, 0.020, panel_h)),
        mass=0.05,
        origin=Origin(xyz=(0.0, 0.0, panel_h * 0.5)),
    )
    return (0.0, rod_y, rod_z), (1.0, 0.0, 0.0)


def _build_lock_handle(
    model: ArticulatedObject, r: ResolvedPaperCutterGuillotineConfig, base, top: float
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Rotary safety lock near the hinge end. Anchored on a baked lock boss."""
    px = _pivot_x(r)
    cut_y = _cut_y(r)
    bx = px + 0.075
    by = cut_y + 0.055
    base.visual(
        Box((0.038, 0.038, 0.026)),
        origin=Origin(xyz=(bx, by, top + 0.013)),
        material="steel",
        name="lock_boss", material_class_id="metal.stainless_matte",
    )
    p = model.part("lock_handle")
    p.visual(
        Cylinder(radius=0.009, length=0.028),
        origin=Origin(xyz=(0.0, 0.0, 0.010)),
        material="steel",
        name="lock_shaft", material_class_id="metal.stainless_matte",
    )
    p.visual(
        Cylinder(radius=0.022, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, 0.028)),
        material="grip",
        name="round_handle", material_class_id="rubber.smooth_plain",
    )
    p.visual(
        Box((0.044, 0.010, 0.008)),
        origin=Origin(xyz=(0.022, 0.0, 0.033)),
        material="red",
        name="lock_pointer", material_class_id="plastic.opaque_glossy_molded",
    )
    p.inertial = Inertial.from_geometry(
        Cylinder(radius=0.024, length=0.040), mass=0.04, origin=Origin(xyz=(0.0, 0.0, 0.02))
    )
    return (bx, by, top + 0.026), (0.0, 0.0, 1.0)


def _build_side_gauge(
    model: ArticulatedObject, r: ResolvedPaperCutterGuillotineConfig, base, top: float
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Sliding paper side-gauge riding a baked rail near the rear edge."""
    X, Y = r.base_x, r.base_y
    rail_y = Y * 0.5 - 0.046
    rail_z = top + 0.0086
    base.visual(
        Box((X * 0.86, 0.024, 0.016)),
        origin=Origin(xyz=(0.0, rail_y, rail_z)),
        material="steel",
        name="gauge_rail", material_class_id="metal.stainless_matte",
    )
    p = model.part("side_gauge")
    p.visual(
        Box((0.044, 0.034, 0.026)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="steel",
        name="saddle", material_class_id="metal.stainless_matte",
    )
    p.visual(
        Box((0.006, 0.060, 0.046)),
        origin=Origin(xyz=(0.0, -0.040, 0.026)),
        material="steel",
        name="gauge_fence", material_class_id="metal.stainless_matte",
    )
    p.visual(
        Cylinder(radius=0.009, length=0.024),
        origin=Origin(xyz=(0.026, 0.0, 0.006), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="grip",
        name="thumb_knob", material_class_id="rubber.smooth_plain",
    )
    p.inertial = Inertial.from_geometry(
        Box((0.044, 0.080, 0.060)),
        mass=0.05,
        origin=Origin(xyz=(0.0, -0.020, 0.026)),
    )
    return (0.0, rail_y, rail_z), (1.0, 0.0, 0.0)


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #


def build_paper_cutter_guillotine(
    config: PaperCutterGuillotineConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="paper_cutter_guillotine", assets=assets)
    for material, rgba in r.palette.items():
        model.material(material, rgba=rgba)

    top = _build_base(model, r)
    base = model.get_part("base")

    px = _pivot_x(r)
    cy = _cut_y(r)
    pivot_world_z = top + r.pivot_z
    arm_axis = (0.0, -1.0, 0.0)  # horizontal hinge, perpendicular to the blade

    if r.pivot_mount == "separate_pivot_bracket":
        _build_pivot_bracket(model, r)
        bracket = model.get_part("pivot_bracket")
        model.articulation(
            "base_to_pivot_bracket",
            ArticulationType.FIXED,
            parent=base,
            child=bracket,
            origin=Origin(xyz=(px, cy, top)),
        )
        _build_blade_arm(model, r)
        model.articulation(
            "pivot_bracket_to_blade_arm",
            ArticulationType.REVOLUTE,
            parent=bracket,
            child=model.get_part("blade_arm"),
            origin=Origin(xyz=(0.0, 0.0, r.pivot_z)),
            axis=arm_axis,
            motion_limits=MotionLimits(effort=18.0, velocity=2.4, lower=0.0, upper=r.blade_upper),
        )
    else:
        _build_blade_arm(model, r)
        model.articulation(
            "base_to_blade_arm",
            ArticulationType.REVOLUTE,
            parent=base,
            child=model.get_part("blade_arm"),
            origin=Origin(xyz=(px, cy, pivot_world_z)),
            axis=arm_axis,
            motion_limits=MotionLimits(effort=18.0, velocity=2.4, lower=0.0, upper=r.blade_upper),
        )

    # Slot 4
    if r.second_dof == "hold_down_bar_prismatic":
        origin, axis = _build_hold_down(model, r, base, top)
        model.articulation(
            "base_to_hold_down",
            ArticulationType.PRISMATIC,
            parent=base,
            child=model.get_part("hold_down"),
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=MotionLimits(effort=6.0, velocity=0.20, lower=-0.035, upper=0.000),
        )
    elif r.second_dof == "finger_guard_revolute":
        origin, axis = _build_finger_guard(model, r, base, top)
        model.articulation(
            "base_to_finger_guard",
            ArticulationType.REVOLUTE,
            parent=base,
            child=model.get_part("finger_guard"),
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=MotionLimits(effort=0.5, velocity=3.0, lower=0.0, upper=1.55),
        )
    elif r.second_dof == "lock_handle_revolute":
        origin, axis = _build_lock_handle(model, r, base, top)
        model.articulation(
            "base_to_lock_handle",
            ArticulationType.REVOLUTE,
            parent=base,
            child=model.get_part("lock_handle"),
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=MotionLimits(effort=0.5, velocity=3.0, lower=0.0, upper=math.pi / 2.0),
        )
    elif r.second_dof == "side_gauge_prismatic":
        origin, axis = _build_side_gauge(model, r, base, top)
        model.articulation(
            "base_to_side_gauge",
            ArticulationType.PRISMATIC,
            parent=base,
            child=model.get_part("side_gauge"),
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=MotionLimits(
                effort=1.0, velocity=0.15, lower=-r.base_x * 0.32, upper=r.base_x * 0.32
            ),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_paper_cutter_guillotine(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_paper_cutter_guillotine(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedPaperCutterGuillotineConfig) -> list[tuple[str, str]]:
    return [
        ("base", r.base_style),
        ("arm", r.arm_style),
        ("pivot_mount", r.pivot_mount),
        ("second_dof", r.second_dof),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    name_set = {p.name for p in model.parts}
    # Blade_arm hub captures the pivot pin / clevis geometry baked on base.
    if "blade_arm" in name_set and "base" in name_set:
        ctx.allow_overlap(
            model.get_part("base"),
            model.get_part("blade_arm"),
            reason="blade_arm hub captures the pivot pin / clevis cheeks baked on base",
        )
    if "blade_arm" in name_set and "pivot_bracket" in name_set:
        ctx.allow_overlap(
            model.get_part("pivot_bracket"),
            model.get_part("blade_arm"),
            reason="blade_arm hub captures the bracket_axle (press-fit pivot)",
        )
    if "pivot_bracket" in name_set and "base" in name_set:
        ctx.allow_overlap(
            model.get_part("base"),
            model.get_part("pivot_bracket"),
            reason="pivot_bracket seat sits on the base mount pad",
        )
    # Second-DOF parts ride the base hardware (guide posts / rod / rail / boss).
    for child in ("hold_down", "finger_guard", "lock_handle", "side_gauge"):
        if child in name_set:
            ctx.allow_overlap(
                model.get_part("base"),
                model.get_part(child),
                reason=f"{child} rides on the base hardware along its joint axis",
            )
    # Blade arm + secondary part may co-occupy the work envelope.
    for child in ("hold_down", "finger_guard", "lock_handle", "side_gauge"):
        if child in name_set and "blade_arm" in name_set:
            ctx.allow_overlap(
                model.get_part("blade_arm"),
                model.get_part(child),
                reason=f"{child} shares the work envelope with the blade_arm",
            )


def run_paper_cutter_guillotine_tests(
    object_model: ArticulatedObject, config: PaperCutterGuillotineConfig
) -> TestReport:
    ctx = TestContext(object_model)
    _declare_overlaps(ctx, object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()
    parts = {p.name for p in object_model.parts}
    ctx.check("base_present", "base" in parts)
    ctx.check("blade_arm_present", "blade_arm" in parts)
    revolutes = [
        j for j in object_model.articulations if j.articulation_type == ArticulationType.REVOLUTE
    ]
    ctx.check("at_least_one_revolute", len(revolutes) >= 1)
    return ctx.report()


__all__ = [
    "ArmStyle",
    "BaseStyle",
    "PaletteTheme",
    "PaperCutterGuillotineConfig",
    "PivotMount",
    "ResolvedPaperCutterGuillotineConfig",
    "SecondDof",
    "__modular__",
    "build_paper_cutter_guillotine",
    "build_seeded_paper_cutter_guillotine",
    "config_from_seed",
    "resolve_config",
    "run_paper_cutter_guillotine_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
