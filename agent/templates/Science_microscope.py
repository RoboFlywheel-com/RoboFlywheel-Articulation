# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``microscope``.

Follows ``articraft_template_authoring/specs_modular_v1/Science_Science_microscope.md``.

A compound optical microscope: a rigid white-metal ``base`` casting (heavy foot
+ angled arm column + head housing on the optical axis at X=0), a ROTATING
NOSEPIECE TURRET carrying N objective lenses (CONTINUOUS about the vertical
optical axis — the category identity), a FOCUS/STAGE mechanism, an eyepiece
HEAD, and a sub-stage ILLUMINATION module.

Three parallel structural slots hang off the rigid base, plus one multiplicity
axis (objective_count over the single turret joint):

    head           : monocular_inclined / binocular_head / vertical_straight
    focus_stage    : side_coaxial / dual_coarse_fine / mechanical_xy
    illumination   : condenser_lamp / tilting_mirror / led_disc

Identity invariant every seed: ``head_to_nosepiece`` CONTINUOUS turret + a
focus joint (PRISMATIC stage for side/dual, or X/Y PRISMATIC carriages for the
mechanical_xy stage). ``tilting_mirror`` adds a REVOLUTE; ``mechanical_xy`` adds
2 PRISMATIC + 2 REVOLUTE; ``dual_coarse_fine`` adds a second CONTINUOUS knob.

Adopted sources (spec Module Source Index):
S1 parent 5f8b9008 — monocular_inclined + condenser_lamp + side_coaxial (turret N=3)
S2 var_binoc — binocular_head
S3 var_vtube — vertical_straight
S4 var_mirror — tilting_mirror (fork + REVOLUTE mirror)
S5 var_leddisc — led_disc
S6 var_dualknob — dual_coarse_fine_knob
S7 var_xystage — mechanical_xy_stage
S8/S9/S10 var_obj{2,4,6} — objective_count multiplicity
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
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
    mesh_from_cadquery,
)

# adopted: S1 5f8b9008 — monocular tube + condenser + side coaxial knob (parent, N=3)
# adopted: S2 var_binoc — binocular bridge head
# adopted: S3 var_vtube — vertical straight monocular tube
# adopted: S4 var_mirror — trunnion fork + REVOLUTE tilting mirror
# adopted: S5 var_leddisc — recessed LED diffuser puck
# adopted: S6 var_dualknob — coaxial coarse + fine CONTINUOUS knobs
# adopted: S7 var_xystage — FIXED stage + X/Y PRISMATIC carriages + drive knobs
# adopted: S8/S9/S10 var_obj{2,4,6} — turret objective multiplicity

__modular__ = True

HeadStyle = Literal["monocular_inclined", "binocular_head", "vertical_straight"]
IlluminationStyle = Literal["condenser_lamp", "tilting_mirror", "led_disc"]
FocusStageStyle = Literal["side_coaxial", "dual_coarse_fine", "mechanical_xy"]
PaletteStyle = Literal[
    "white_lab", "black_chrome", "graphite", "blue_student", "brushed_chrome_pro"
]

# ----------------------------------------------------------------------
# Shared layout constants (S1 parent verbatim; used by build + tests)
# ----------------------------------------------------------------------
ARM_FRONT_X = 0.048          # arm front face below the head (clears turret sweep)
ARM_HALF_WIDTH = 0.027       # arm half-width in Y
# Base-mounted joints are anchored onto the arm front face (x=ARM_FRONT_X) so
# the joint origin sits on real ``base`` geometry (within the 15 mm baseline
# tol). Child geometry is built/translated so its world placement is unchanged
# and the child link's geometry still contains the joint origin.
STAGE_MOUNT_X = ARM_FRONT_X  # stage / xy stack mount on the arm front
KNOB_MOUNT_X = 0.060         # focus axle bore mount on the arm (within arm solid)
TURRET_Z = 0.240             # turret joint height (world)
TURRET_DISC_R = 0.040        # turret disc radius
OBJ_ORBIT_R = 0.028          # objective mounting radius (off-axis)
OBJ_BARREL_R = 0.0090        # objective barrel top radius
STAGE_Z = 0.146              # stage joint height (plate mid-plane, world)
STAGE_TRAVEL = (-0.010, 0.006)  # prismatic focus travel (lower, upper)
KNOB_Z = 0.105               # focus axle height (world)
KNOB_X = 0.078               # focus axle X position (inside the arm column)
HEAD_R = 0.034               # head housing radius (cylindrical mono / vert)
HEAD_X_HALF = 0.034          # head housing X half-width (binocular block)
HEAD_Y_HALF = 0.048          # head housing Y half-width (binocular block, widened)
HEAD_Z0, HEAD_Z1 = 0.245, 0.298  # head housing bottom/top

# Tilting mirror layout (S4)
FORK_MOUNT_Z = 0.035         # fork part origin height (world), at foot top
FORK_GAP = 0.046             # clear gap between fork cheeks (along Y)
CHEEK_T = 0.004              # cheek thickness (along Y)
FORK_WIDTH_Y = FORK_GAP + 2 * CHEEK_T  # total fork width
FORK_DEPTH_X = 0.012         # fork depth (front-to-back, along X)
FORK_BASE_T = 0.008          # base plate thickness
FORK_CHEEK_H = 0.052         # cheek height above base plate
FORK_TRUNNION_Z_LOCAL = 0.042  # trunnion center height from fork base (local)
FORK_TRUNNION_D = 0.006      # trunnion bore diameter
MIRROR_R = 0.020             # mirror disc radius
MIRROR_THICK = 0.003         # mirror disc thickness
MIRROR_TILT = (-0.5, 0.5)    # mirror revolute limits (radians)
STUB_R = 0.0025              # trunnion stub radius
STUB_EMBED = 0.002           # stub embed depth into disc edge

# Mechanical XY stage layout (S7)
# X travel + frame depth are bounded so the frame rear edge never reaches the
# arm front face (ARM_FRONT_X=0.048) across the full +X travel:
#   rear_edge_max = X_FRAME_OUTER[0]/2 + X_TRAVEL[1] = 0.038 + 0.006 = 0.044 < 0.048
X_TRAVEL = (-0.006, 0.006)   # x_carriage prismatic travel (lower, upper)
Y_TRAVEL = (-0.012, 0.012)   # y_carriage prismatic travel (lower, upper)
X_FRAME_OUTER = (0.076, 0.088, 0.005)  # x_carriage frame outer dims
X_FRAME_INNER = (0.068, 0.058)         # x_carriage frame inner opening
Y_PLATE_SIZE = (0.065, 0.055, 0.004)   # y_carriage plate dims
N_DRIVE_KNOBS = 2
DRIVE_KNOB_R = 0.007
DRIVE_KNOB_LENGTH = 0.012

# Objective multiplicity (S8/S9/S10). 360/N equal spacing, #0 faces front (-X).
OBJ_MULTIPLICITY = (2, 3, 4, 6)
OBJ_LENGTH_BANK = (0.050, 0.045, 0.040, 0.036, 0.032, 0.028)  # 100x..4x, longest first

# Per-style named palettes (>= 3 named materials each → every visual).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "white_lab": {
        "body": (0.93, 0.93, 0.94, 1.0),
        "black": (0.09, 0.09, 0.10, 1.0),
        "dark": (0.16, 0.16, 0.18, 1.0),
        "chrome": (0.75, 0.76, 0.78, 1.0),
        "brass": (0.78, 0.74, 0.55, 1.0),
        "teal": (0.10, 0.45, 0.45, 1.0),
        "glass": (0.45, 0.60, 0.70, 0.9),
    },
    "black_chrome": {
        "body": (0.13, 0.13, 0.15, 1.0),
        "black": (0.05, 0.05, 0.06, 1.0),
        "dark": (0.22, 0.22, 0.24, 1.0),
        "chrome": (0.82, 0.83, 0.86, 1.0),
        "brass": (0.74, 0.70, 0.46, 1.0),
        "teal": (0.10, 0.42, 0.50, 1.0),
        "glass": (0.40, 0.55, 0.66, 0.9),
    },
    "graphite": {
        "body": (0.34, 0.35, 0.37, 1.0),
        "black": (0.07, 0.07, 0.08, 1.0),
        "dark": (0.18, 0.19, 0.20, 1.0),
        "chrome": (0.70, 0.72, 0.74, 1.0),
        "brass": (0.72, 0.66, 0.44, 1.0),
        "teal": (0.12, 0.40, 0.46, 1.0),
        "glass": (0.42, 0.56, 0.66, 0.9),
    },
    "blue_student": {
        "body": (0.20, 0.34, 0.58, 1.0),
        "black": (0.08, 0.09, 0.11, 1.0),
        "dark": (0.14, 0.18, 0.26, 1.0),
        "chrome": (0.76, 0.78, 0.82, 1.0),
        "brass": (0.80, 0.74, 0.52, 1.0),
        "teal": (0.10, 0.48, 0.52, 1.0),
        "glass": (0.46, 0.62, 0.74, 0.9),
    },
    "brushed_chrome_pro": {
        "body": (0.66, 0.67, 0.69, 1.0),
        "black": (0.10, 0.10, 0.11, 1.0),
        "dark": (0.30, 0.31, 0.33, 1.0),
        "chrome": (0.85, 0.86, 0.88, 1.0),
        "brass": (0.82, 0.76, 0.54, 1.0),
        "teal": (0.12, 0.46, 0.50, 1.0),
        "glass": (0.50, 0.64, 0.74, 0.9),
    },
}


@dataclass(frozen=True)
class MicroscopeConfig:
    """Public configuration (frozen public API)."""

    head: HeadStyle = "monocular_inclined"
    illumination: IlluminationStyle = "condenser_lamp"
    focus_stage: FocusStageStyle = "side_coaxial"
    palette_style: PaletteStyle = "white_lab"
    objective_count: int = 3
    foot_scale: float = 1.0
    objective_length_scale: float = 1.0
    name: str = "reference_microscope"


@dataclass(frozen=True)
class ResolvedMicroscopeConfig:
    head: HeadStyle
    illumination: IlluminationStyle
    focus_stage: FocusStageStyle
    palette_style: PaletteStyle
    objective_count: int
    foot_scale: float
    objective_length_scale: float
    palette: dict[str, tuple[float, float, float, float]]
    obj_lengths: tuple[float, ...]
    obj_angles_deg: tuple[float, ...]
    name: str


def _clamp_scale(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> MicroscopeConfig:
    """Deterministic procedural sampling. seed=0 is not special.

    Uniformly samples the three structural slots, the objective
    multiplicity, and two continuous size scales (foot footprint and
    objective barrel length). Multiplicity is weighted toward the parent
    N=3 / common N=4, but every value in {2,3,4,6} is reachable.
    """
    rng = random.Random(seed)
    head: HeadStyle = rng.choice(("monocular_inclined", "binocular_head", "vertical_straight"))
    illumination: IlluminationStyle = rng.choice(
        ("condenser_lamp", "tilting_mirror", "led_disc")
    )
    focus_stage: FocusStageStyle = rng.choice(
        ("side_coaxial", "dual_coarse_fine", "mechanical_xy")
    )
    palette_style: PaletteStyle = rng.choice(tuple(PALETTES))
    objective_count = rng.choices(OBJ_MULTIPLICITY, weights=(2, 3, 3, 2), k=1)[0]

    return MicroscopeConfig(
        head=head,
        illumination=illumination,
        focus_stage=focus_stage,
        palette_style=palette_style,
        objective_count=objective_count,
        foot_scale=round(rng.uniform(0.92, 1.15), 3),
        objective_length_scale=round(rng.uniform(0.85, 1.15), 3),
        name=f"seeded_microscope_{seed}",
    )


def resolve_config(config: MicroscopeConfig) -> ResolvedMicroscopeConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")
    if config.head not in ("monocular_inclined", "binocular_head", "vertical_straight"):
        raise ValueError(f"Unsupported head: {config.head}")
    if config.illumination not in ("condenser_lamp", "tilting_mirror", "led_disc"):
        raise ValueError(f"Unsupported illumination: {config.illumination}")
    if config.focus_stage not in ("side_coaxial", "dual_coarse_fine", "mechanical_xy"):
        raise ValueError(f"Unsupported focus_stage: {config.focus_stage}")

    # Clamp objective_count into the supported multiplicity set.
    n = int(config.objective_count)
    if n not in OBJ_MULTIPLICITY:
        n = min(OBJ_MULTIPLICITY, key=lambda v: abs(v - n))

    foot_scale = _clamp_scale(config.foot_scale, 0.92, 1.15)
    obj_scale = _clamp_scale(config.objective_length_scale, 0.85, 1.15)

    # Objective barrel lengths: take the longest N from the bank so #0 (front)
    # is the tallest, like the parent. Equal 360/N angular spacing, #0 at 180.
    obj_lengths = tuple(length * obj_scale for length in OBJ_LENGTH_BANK[:n])
    obj_angles_deg = tuple((180.0 + i * (360.0 / n)) % 360.0 for i in range(n))

    return ResolvedMicroscopeConfig(
        head=config.head,
        illumination=config.illumination,
        focus_stage=config.focus_stage,
        palette_style=config.palette_style,
        objective_count=n,
        foot_scale=foot_scale,
        objective_length_scale=obj_scale,
        palette=dict(PALETTES[config.palette_style]),
        obj_lengths=obj_lengths,
        obj_angles_deg=obj_angles_deg,
        name=config.name,
    )


# --------------------------------------------------------------------------- #
# Material registration (named palette → every visual)
# --------------------------------------------------------------------------- #
def _register_materials(model: ArticulatedObject, palette: dict) -> dict:
    return {
        "body": model.material("body_metal", rgba=palette["body"]),
        "black": model.material("black_plastic", rgba=palette["black"]),
        "dark": model.material("dark_metal", rgba=palette["dark"]),
        "chrome": model.material("chrome", rgba=palette["chrome"]),
        "brass": model.material("brass_lens", rgba=palette["brass"]),
        "teal": model.material("teal_glass", rgba=palette["teal"]),
        "glass": model.material("slide_glass", rgba=palette["glass"]),
    }


def _mc(geom, name, assets):
    return mesh_from_cadquery(geom, name, assets=assets)


# --------------------------------------------------------------------------- #
# BASE: foot + angled arm + head housing (one rigid casting). S1 verbatim,
# head shape selected by head style.
# --------------------------------------------------------------------------- #
def _build_base(model, r, mats, *, assets) -> object:
    base = model.part("base")

    foot = (
        cq.Workplane("XY")
        .center(0.015, 0.0)
        .rect(0.200 * r.foot_scale, 0.150 * r.foot_scale)
        .workplane(offset=0.035)
        .rect(0.185 * r.foot_scale, 0.135 * r.foot_scale)
        .loft(combine=True)
        .edges(">Z")
        .fillet(0.008)
    )
    base.visual(_mc(foot, "foot", assets), material=mats["body"], name="foot", material_class_id="metal.paint_coated")

    arm_profile = [
        (ARM_FRONT_X, 0.030),
        (ARM_FRONT_X, 0.245),
        (0.020, 0.245),
        (0.020, 0.296),
        (0.072, 0.296),
        (0.105, 0.160),
        (0.105, 0.030),
    ]
    arm = (
        cq.Workplane("XZ")
        .polyline(arm_profile)
        .close()
        .extrude(ARM_HALF_WIDTH, both=True)
    )
    base.visual(_mc(arm, "arm_limb", assets), material=mats["body"], name="arm_limb", material_class_id="metal.paint_coated")

    if r.head == "binocular_head":
        # Widened rounded rectangular block (S2): wider in Y for two tube exits.
        head = (
            cq.Workplane("XY")
            .workplane(offset=HEAD_Z0)
            .rect(2 * HEAD_X_HALF, 2 * HEAD_Y_HALF)
            .extrude(HEAD_Z1 - HEAD_Z0)
            .edges("|Z")
            .fillet(0.015)
        )
    else:
        # Cylindrical head housing on the optical axis (S1/S3).
        head = (
            cq.Workplane("XY")
            .workplane(offset=HEAD_Z0)
            .circle(HEAD_R)
            .extrude(HEAD_Z1 - HEAD_Z0)
            .edges(">Z")
            .fillet(0.010)
        )
    base.visual(_mc(head, "head_housing", assets), material=mats["body"], name="head_housing", material_class_id="metal.paint_coated")

    base.inertial = Inertial.from_geometry(
        Box((0.20, 0.15, 0.30)), mass=3.0, origin=Origin(xyz=(0.04, 0.0, 0.13))
    )
    return base


# --------------------------------------------------------------------------- #
# HEAD slot
# --------------------------------------------------------------------------- #
def _build_monocular_inclined(model, base, r, mats, *, assets) -> None:
    """S1: single 40-deg inclined monocular tube + dark ocular + teal lens."""
    eyepiece = model.part("eyepiece_tube")
    tube_body = cq.Workplane("XY").circle(0.015).extrude(0.075)
    eyepiece.visual(_mc(tube_body, "tube_body", assets), material=mats["body"], name="tube_body", material_class_id="metal.paint_coated")
    ocular = (
        cq.Workplane("XY")
        .workplane(offset=0.073)
        .circle(0.0135)
        .extrude(0.030)
        .faces(">Z")
        .workplane()
        .circle(0.0115)
        .extrude(0.010)
    )
    eyepiece.visual(
        _mc(ocular, "ocular_barrel", assets), material=mats["black"], name="ocular_barrel", material_class_id="plastic.opaque_glossy_molded"
    )
    eyepiece.visual(
        Cylinder(radius=0.0105, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, 0.112)),
        material=mats["teal"],
        name="ocular_lens", material_class_id="glass.smoked_tinted",
    )
    eyepiece.inertial = Inertial.from_geometry(
        Cylinder(radius=0.015, length=0.115), mass=0.12, origin=Origin(xyz=(0.0, 0.0, 0.055))
    )
    model.articulation(
        "head_to_eyepiece",
        ArticulationType.FIXED,
        parent=base,
        child=eyepiece,
        origin=Origin(xyz=(0.0, 0.0, 0.290), rpy=(0.0, math.radians(-40.0), 0.0)),
    )


def _build_vertical_straight(model, base, r, mats, *, assets) -> None:
    """S3: single monocular tube rising straight up (no tilt)."""
    eyepiece = model.part("eyepiece_tube")
    tube_body = cq.Workplane("XY").circle(0.015).extrude(0.075)
    eyepiece.visual(_mc(tube_body, "tube_body", assets), material=mats["body"], name="tube_body", material_class_id="metal.paint_coated")
    ocular = (
        cq.Workplane("XY")
        .workplane(offset=0.073)
        .circle(0.0135)
        .extrude(0.030)
        .faces(">Z")
        .workplane()
        .circle(0.0115)
        .extrude(0.010)
    )
    eyepiece.visual(
        _mc(ocular, "ocular_barrel", assets), material=mats["black"], name="ocular_barrel", material_class_id="plastic.opaque_glossy_molded"
    )
    eyepiece.visual(
        Cylinder(radius=0.0105, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, 0.112)),
        material=mats["teal"],
        name="ocular_lens", material_class_id="glass.smoked_tinted",
    )
    eyepiece.inertial = Inertial.from_geometry(
        Cylinder(radius=0.015, length=0.115), mass=0.12, origin=Origin(xyz=(0.0, 0.0, 0.055))
    )
    model.articulation(
        "head_to_eyepiece",
        ArticulationType.FIXED,
        parent=base,
        child=eyepiece,
        origin=Origin(xyz=(0.0, 0.0, 0.295)),
    )


def _binoc_eyepiece_tube(y_offset: float, bridge_top_z: float, tube_r: float, tube_length: float):
    """S2 shared helper: (tube_cq, ocular_cq, lens_z, lens_r)."""
    tube = (
        cq.Workplane("XY")
        .workplane(offset=bridge_top_z - 0.003)
        .center(0.0, y_offset)
        .circle(tube_r)
        .extrude(tube_length + 0.003)
    )
    ocular_base_z = bridge_top_z + tube_length - 0.002
    ocular = (
        cq.Workplane("XY")
        .workplane(offset=ocular_base_z)
        .center(0.0, y_offset)
        .circle(0.0125)
        .extrude(0.030)
        .faces(">Z")
        .workplane()
        .circle(0.0105)
        .extrude(0.010)
    )
    lens_z = ocular_base_z + 0.030 + 0.010 - 0.001
    lens_r = 0.0095
    return tube, ocular, lens_z, lens_r


def _build_binocular_head(model, base, r, mats, *, assets) -> None:
    """S2: bridge/splitter block + two parallel inclined tubes."""
    tube_y_offset = 0.022
    tube_r = 0.014
    tube_length = 0.075
    bridge_h = 0.020
    n_eyepieces = 2

    eyepiece = model.part("binocular_head")
    bridge_y_half = tube_y_offset + tube_r + 0.006
    bridge = (
        cq.Workplane("XY")
        .rect(0.052, 2 * bridge_y_half)
        .extrude(bridge_h)
        .edges("|Z")
        .fillet(0.010)
    )
    eyepiece.visual(_mc(bridge, "bridge_block", assets), material=mats["body"], name="bridge_block", material_class_id="metal.paint_coated")

    for i in range(n_eyepieces):
        y_off = (2 * i - 1) * tube_y_offset
        tube_cq, ocular_cq, lens_z, lens_r = _binoc_eyepiece_tube(
            y_off, bridge_h, tube_r, tube_length
        )
        eyepiece.visual(_mc(tube_cq, f"tube_{i}", assets), material=mats["body"], name=f"tube_{i}", material_class_id="metal.paint_coated")
        eyepiece.visual(
            _mc(ocular_cq, f"ocular_{i}", assets), material=mats["black"], name=f"ocular_{i}", material_class_id="plastic.opaque_glossy_molded"
        )
        eyepiece.visual(
            Cylinder(radius=lens_r, length=0.004),
            origin=Origin(xyz=(0.0, y_off, lens_z)),
            material=mats["teal"],
            name=f"lens_{i}", material_class_id="glass.smoked_tinted",
        )

    eyepiece.inertial = Inertial.from_geometry(
        Box((0.052, 2 * bridge_y_half, 0.134)), mass=0.22, origin=Origin(xyz=(0.0, 0.0, 0.067))
    )
    model.articulation(
        "head_to_eyepiece",
        ArticulationType.FIXED,
        parent=base,
        child=eyepiece,
        origin=Origin(xyz=(0.0, 0.0, 0.290), rpy=(0.0, math.radians(-40.0), 0.0)),
    )


# --------------------------------------------------------------------------- #
# NOSEPIECE TURRET (always): CONTINUOUS about the vertical optical axis,
# carrying N off-axis objectives at 360/N spacing (single turret joint). S1.
# --------------------------------------------------------------------------- #
def _build_nosepiece(model, base, r, mats, *, assets) -> None:
    nosepiece = model.part("nosepiece_turret")
    turret_plate = (
        cq.Workplane("XY").workplane(offset=-0.025).circle(TURRET_DISC_R).extrude(0.005)
    )
    turret_cone = (
        cq.Workplane("XY")
        .workplane(offset=-0.020)
        .circle(TURRET_DISC_R)
        .workplane(offset=0.016)
        .circle(0.024)
        .loft(combine=True)
    )
    turret_hub = cq.Workplane("XY").workplane(offset=-0.006).circle(0.013).extrude(0.016)
    turret_solid = turret_plate.union(turret_cone).union(turret_hub)
    nosepiece.visual(
        _mc(turret_solid, "turret_disc", assets), material=mats["dark"], name="turret_disc", material_class_id="metal.blackened_gunmetal"
    )

    ring_mats = (mats["brass"], mats["teal"], mats["dark"])
    for i, length in enumerate(r.obj_lengths):
        ang = math.radians(r.obj_angles_deg[i])
        ox = OBJ_ORBIT_R * math.cos(ang)
        oy = OBJ_ORBIT_R * math.sin(ang)
        barrel = (
            cq.Workplane("XY")
            .workplane(offset=-0.023)
            .circle(OBJ_BARREL_R)
            .workplane(offset=-length * 0.60)
            .circle(0.0082)
            .workplane(offset=-length * 0.40)
            .circle(0.0050)
            .loft(combine=True)
        )
        barrel = barrel.translate((ox, oy, 0.0))
        nosepiece.visual(
            _mc(barrel, f"objective_barrel_{i}", assets),
            material=mats["chrome"],
            name=f"objective_barrel_{i}", material_class_id="metal.chrome_polished",
        )
        ring = (
            cq.Workplane("XY")
            .workplane(offset=-0.023 - 0.55 * length)
            .circle(0.0090)
            .extrude(-0.005)
        )
        ring = ring.translate((ox, oy, 0.0))
        nosepiece.visual(
            _mc(ring, f"objective_ring_{i}", assets),
            material=ring_mats[i % len(ring_mats)],
            name=f"objective_ring_{i}", material_class_id="metal.paint_coated",
        )
    nosepiece.inertial = Inertial.from_geometry(
        Cylinder(radius=TURRET_DISC_R, length=0.09), mass=0.22, origin=Origin(xyz=(0.0, 0.0, -0.035))
    )
    model.articulation(
        "head_to_nosepiece",
        ArticulationType.CONTINUOUS,
        parent=base,
        child=nosepiece,
        origin=Origin(xyz=(0.0, 0.0, TURRET_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0),
    )


# --------------------------------------------------------------------------- #
# STAGE (always): black mechanical stage holding the slide. PRISMATIC focus
# travel for side/dual; FIXED for the mechanical_xy carriage stack. S1/S7.
# --------------------------------------------------------------------------- #
def _build_stage(model, base, r, mats, *, assets, prismatic: bool, carry_slide: bool = True) -> None:
    # Anchor the stage joint on the arm front face (x=STAGE_MOUNT_X). All stage
    # geometry is built shifted by -mx in X so its world placement is unchanged
    # while the joint origin lands on real arm geometry and the child link's
    # geometry still contains (0,0,0).
    mx = STAGE_MOUNT_X
    stage = model.part("stage")
    stage_plate = (
        cq.Workplane("XY")
        .center(-0.0075, 0.0)
        .rect(0.135, 0.120)
        .extrude(0.008)
        .edges("|Z")
        .fillet(0.006)
    )
    stage_plate = stage_plate.translate((-mx, 0.0, -0.004))
    stage_plate = (
        stage_plate.faces(">Z").workplane(origin=(-mx, 0.0, 0.0)).circle(0.011).cutThruAll()
    )
    stage.visual(_mc(stage_plate, "stage_plate", assets), material=mats["black"], name="stage_plate", material_class_id="plastic.opaque_glossy_molded")

    bracket = cq.Workplane("XY").center(0.053, 0.0).rect(0.026, 0.040).extrude(-0.027)
    bracket = bracket.translate((-mx, 0.0, -0.003))
    stage.visual(_mc(bracket, "stage_bracket", assets), material=mats["dark"], name="stage_bracket", material_class_id="metal.blackened_gunmetal")

    if carry_slide:
        # Mechanical XY carries the slide + clips on the moving y_carriage
        # instead, so it passes carry_slide=False and keeps the bare stage here.
        for sy, tag in ((-0.020, "n"), (0.020, "p")):
            clip = cq.Workplane("XY").center(0.022, sy).rect(0.030, 0.004).extrude(0.0015)
            clip = clip.translate((-mx, 0.0, 0.0037))
            stage.visual(_mc(clip, f"stage_clip_{tag}", assets), material=mats["chrome"], name=f"stage_clip_{tag}", material_class_id="metal.chrome_polished")
        stage.visual(
            Box((0.064, 0.024, 0.0012)),
            origin=Origin(xyz=(-mx, 0.0, 0.0044)),
            material=mats["glass"],
            name="specimen_slide", material_class_id="glass.clear_transparent",
        )

    stage.inertial = Inertial.from_geometry(
        Box((0.135, 0.120, 0.030)), mass=0.30, origin=Origin(xyz=(-mx, 0.0, -0.010))
    )
    if prismatic:
        model.articulation(
            "arm_to_stage",
            ArticulationType.PRISMATIC,
            parent=base,
            child=stage,
            origin=Origin(xyz=(mx, 0.0, STAGE_Z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=5.0, velocity=0.05, lower=STAGE_TRAVEL[0], upper=STAGE_TRAVEL[1]
            ),
        )
    else:
        model.articulation(
            "arm_to_stage",
            ArticulationType.FIXED,
            parent=base,
            child=stage,
            origin=Origin(xyz=(mx, 0.0, STAGE_Z)),
        )


# --------------------------------------------------------------------------- #
# FOCUS-STAGE slot
# --------------------------------------------------------------------------- #
def _add_focus_bearing_boss(base, mats, *, assets) -> None:
    """Add a focus-knob bearing boss to the base arm at the axle centerline.

    Real microscopes carry a raised bearing hub on the arm where the focus
    axle passes through. It also gives the CONTINUOUS knob joint origin real
    base geometry within the 15 mm origin tolerance (the bare arm centerline
    is ARM_HALF_WIDTH away from the nearest arm surface). Cylinder along Y.
    """
    # Bearing collar centered on the axle (y=0). It must protrude just past the
    # arm Y-faces (|y| = ARM_HALF_WIDTH) so its surface makes real contact with
    # the arm (otherwise a fully-buried hub reads as a disconnected island), and
    # it carries the focus joint origin onto real base geometry.
    boss_half = ARM_HALF_WIDTH + 0.002
    boss = (
        cq.Workplane("XZ")
        .workplane(offset=-boss_half)
        .center(KNOB_X, KNOB_Z)
        .circle(0.012)
        .extrude(2 * boss_half)
    )
    base.visual(_mc(boss, "focus_bearing_boss", assets), material=mats["dark"], name="focus_bearing_boss", material_class_id="metal.blackened_gunmetal")


def _build_side_coaxial(model, base, r, mats, *, assets) -> None:
    """S1: PRISMATIC stage + a single through-axle CONTINUOUS focus knob."""
    _build_stage(model, base, r, mats, assets=assets, prismatic=True)
    _add_focus_bearing_boss(base, mats, assets=assets)

    focus_knob = model.part("focus_knob")
    knob_axle = cq.Workplane("XY").workplane(offset=-0.046).circle(0.006).extrude(0.092)
    focus_knob.visual(_mc(knob_axle, "knob_axle", assets), material=mats["dark"], name="knob_axle", material_class_id="metal.blackened_gunmetal")
    for sz, tag in ((-1.0, "n"), (1.0, "p")):
        disc = (
            cq.Workplane("XY")
            .workplane(offset=sz * 0.028 if sz > 0 else sz * 0.040)
            .circle(0.018)
            .extrude(0.012)
        )
        hub = (
            cq.Workplane("XY")
            .workplane(offset=sz * 0.040 if sz > 0 else sz * 0.046)
            .circle(0.011)
            .extrude(0.006)
        )
        focus_knob.visual(
            _mc(disc.union(hub), f"knob_disc_{tag}", assets),
            material=mats["dark"],
            name=f"knob_disc_{tag}", material_class_id="metal.blackened_gunmetal",
        )
    for sz, tag in ((-1.0, "n"), (1.0, "p")):
        nub = (
            cq.Workplane("XY")
            .workplane(offset=sz * 0.0395 if sz > 0 else sz * 0.0445)
            .center(0.0140, 0.0)
            .rect(0.006, 0.003)
            .extrude(0.005)
        )
        focus_knob.visual(_mc(nub, f"knob_nub_{tag}", assets), material=mats["body"], name=f"knob_nub_{tag}", material_class_id="metal.paint_coated")
    focus_knob.inertial = Inertial.from_geometry(Cylinder(radius=0.018, length=0.092), mass=0.06)
    model.articulation(
        "arm_to_focus_knob",
        ArticulationType.CONTINUOUS,
        parent=base,
        child=focus_knob,
        origin=Origin(xyz=(KNOB_X, 0.0, KNOB_Z), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0),
    )


def _build_dual_coarse_fine(model, base, r, mats, *, assets) -> None:
    """S6: PRISMATIC stage + coaxial coarse + fine CONTINUOUS knobs."""
    _build_stage(model, base, r, mats, assets=assets, prismatic=True)
    _add_focus_bearing_boss(base, mats, assets=assets)

    coarse_disc_r = 0.022
    fine_disc_r = 0.014
    coarse_axle_r = 0.007
    fine_axle_r = 0.004

    knob_origin = Origin(xyz=(KNOB_X, 0.0, KNOB_Z), rpy=(-math.pi / 2.0, 0.0, 0.0))

    def _side_discs(part, prefix, disc_r, thickness, hub_r, disc_z_offset, hub_z_offset, mat):
        for i, sign in enumerate([-1.0, 1.0]):
            disc = (
                cq.Workplane("XY")
                .workplane(offset=sign * disc_z_offset)
                .circle(disc_r)
                .extrude(sign * thickness)
            )
            hub = (
                cq.Workplane("XY")
                .workplane(offset=sign * hub_z_offset)
                .circle(hub_r)
                .extrude(sign * 0.006)
            )
            part.visual(
                _mc(disc.union(hub), f"{prefix}_disc_{i}", assets),
                material=mat,
                name=f"{prefix}_disc_{i}", material_class_id="metal.generic_plain",
            )

    def _side_nubs(part, prefix, nub_r_offset, nub_z_offset, mat):
        for i, sign in enumerate([-1.0, 1.0]):
            nub = (
                cq.Workplane("XY")
                .workplane(offset=sign * nub_z_offset)
                .center(nub_r_offset, 0.0)
                .rect(0.006, 0.003)
                .extrude(sign * 0.004)
            )
            part.visual(_mc(nub, f"{prefix}_nub_{i}", assets), material=mat, name=f"{prefix}_nub_{i}", material_class_id="metal.generic_plain")

    # --- COARSE FOCUS ---
    coarse_focus = model.part("coarse_focus")
    coarse_axle = cq.Workplane("XY").workplane(offset=-0.046).circle(coarse_axle_r).extrude(0.092)
    coarse_focus.visual(_mc(coarse_axle, "coarse_axle", assets), material=mats["dark"], name="coarse_axle", material_class_id="metal.blackened_gunmetal")
    _side_discs(coarse_focus, "coarse", coarse_disc_r, 0.012, 0.013, 0.030, 0.042, mats["dark"])
    for i, sign in enumerate([-1.0, 1.0]):
        for k in range(8):
            ang = k * (2.0 * math.pi / 8)
            rx = (coarse_disc_r - 0.001) * math.cos(ang)
            ry = (coarse_disc_r - 0.001) * math.sin(ang)
            ridge = (
                cq.Workplane("XY")
                .workplane(offset=sign * 0.031)
                .center(rx, ry)
                .rect(0.003, 0.002)
                .extrude(sign * 0.010)
            )
            coarse_focus.visual(
                _mc(ridge, f"coarse_ridge_{i}_{k}", assets),
                material=mats["black"],
                name=f"coarse_ridge_{i}_{k}", material_class_id="plastic.patterned_textured",
            )
    _side_nubs(coarse_focus, "coarse", 0.016, 0.041, mats["body"])
    coarse_focus.inertial = Inertial.from_geometry(Cylinder(radius=coarse_disc_r, length=0.092), mass=0.05)
    model.articulation(
        "arm_to_coarse_focus",
        ArticulationType.CONTINUOUS,
        parent=base,
        child=coarse_focus,
        origin=knob_origin,
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=4.0),
    )

    # --- FINE FOCUS ---
    fine_focus = model.part("fine_focus")
    fine_axle = cq.Workplane("XY").workplane(offset=-0.050).circle(fine_axle_r).extrude(0.100)
    fine_focus.visual(_mc(fine_axle, "fine_axle", assets), material=mats["chrome"], name="fine_axle", material_class_id="metal.chrome_polished")
    _side_discs(fine_focus, "fine", fine_disc_r, 0.008, 0.007, 0.044, 0.052, mats["chrome"])
    for i, sign in enumerate([-1.0, 1.0]):
        for k in range(6):
            ang = k * (2.0 * math.pi / 6)
            rx = (fine_disc_r - 0.001) * math.cos(ang)
            ry = (fine_disc_r - 0.001) * math.sin(ang)
            ridge = (
                cq.Workplane("XY")
                .workplane(offset=sign * 0.045)
                .center(rx, ry)
                .rect(0.002, 0.0015)
                .extrude(sign * 0.006)
            )
            fine_focus.visual(
                _mc(ridge, f"fine_ridge_{i}_{k}", assets),
                material=mats["black"],
                name=f"fine_ridge_{i}_{k}", material_class_id="plastic.patterned_textured",
            )
    _side_nubs(fine_focus, "fine", 0.010, 0.051, mats["dark"])
    fine_focus.inertial = Inertial.from_geometry(Cylinder(radius=fine_disc_r, length=0.100), mass=0.03)
    model.articulation(
        "arm_to_fine_focus",
        ArticulationType.CONTINUOUS,
        parent=base,
        child=fine_focus,
        origin=knob_origin,
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.5, velocity=6.0),
    )


def _make_drive_knob(length: float, radius: float):
    """S7: cylindrical drive knob with mounting boss + grip ring along +Z."""
    boss = cq.Workplane("XY").workplane(offset=-0.003).circle(radius * 0.50).extrude(0.003)
    body = cq.Workplane("XY").circle(radius).extrude(length)
    ring = (
        cq.Workplane("XY")
        .workplane(offset=length * 0.60)
        .circle(radius * 1.12)
        .extrude(length * 0.18)
    )
    return boss.union(body).union(ring)


def _build_mechanical_xy(model, base, r, mats, *, assets) -> None:
    """S7: Z-PRISMATIC focus stage + X/Y PRISMATIC carriages + 2 REVOLUTE knobs.

    The whole XY carriage stack rides the vertical (Z) ``arm_to_stage`` focus
    prismatic like the other variants, so this remains a focusable microscope;
    the X/Y carriages add specimen positioning on top of that focus DOF.
    """
    _build_stage(model, base, r, mats, assets=assets, prismatic=True, carry_slide=False)
    stage = model.get_part("stage")
    # The stage child frame is now anchored at world x=STAGE_MOUNT_X (see
    # _build_stage). Children that parent to ``stage`` and are authored on the
    # optical axis must offset their joint origin x by -mx to land back at x=0;
    # those origins still fall on the (shifted) stage plate geometry.
    mx = STAGE_MOUNT_X

    # --- X carriage (PRISMATIC, X) ---
    x_carriage = model.part("x_carriage")
    x_frame = (
        cq.Workplane("XY")
        .rect(X_FRAME_OUTER[0], X_FRAME_OUTER[1])
        .extrude(X_FRAME_OUTER[2])
        .edges("|Z")
        .fillet(0.003)
    )
    x_frame = x_frame.faces(">Z").workplane().rect(X_FRAME_INNER[0], X_FRAME_INNER[1]).cutThruAll()
    for rx in (0.030, -0.030):
        y_rail = (
            cq.Workplane("XY")
            .workplane(offset=X_FRAME_OUTER[2])
            .center(rx, 0.0)
            .rect(0.006, 0.060)
            .extrude(0.002)
        )
        x_frame = x_frame.union(y_rail)
    # Twin lead-screw nut carriers spanning the X opening, flanking the optical
    # aperture in Y (inner edges at y=0.010) so they carry the carriage nut
    # material near the centerline WITHOUT occluding the transmitted-light path
    # through the stage/slide bore on the optical axis (y=0, r~0.010).
    for cby in (-0.014, 0.014):
        nut_bar = (
            cq.Workplane("XY")
            .center(0.0, cby)
            .rect(X_FRAME_INNER[0] + 0.006, 0.008)
            .extrude(X_FRAME_OUTER[2])
        )
        x_frame = x_frame.union(nut_bar)
    x_carriage.visual(_mc(x_frame, "x_carriage_frame", assets), material=mats["dark"], name="x_carriage_frame", material_class_id="metal.blackened_gunmetal")
    x_carriage.inertial = Inertial.from_geometry(
        Box((X_FRAME_OUTER[0], X_FRAME_OUTER[1], X_FRAME_OUTER[2] + 0.002)),
        mass=0.12,
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
    )
    model.articulation(
        "stage_to_x_carriage",
        ArticulationType.PRISMATIC,
        parent=stage,
        child=x_carriage,
        origin=Origin(xyz=(-mx, 0.0, 0.004)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=0.02, lower=X_TRAVEL[0], upper=X_TRAVEL[1]),
    )

    # --- Y carriage (PRISMATIC, Y) ---
    y_carriage = model.part("y_carriage")
    y_plate = (
        cq.Workplane("XY")
        .rect(Y_PLATE_SIZE[0], Y_PLATE_SIZE[1])
        .extrude(Y_PLATE_SIZE[2])
        .edges("|Z")
        .fillet(0.002)
    )
    y_plate = y_plate.faces(">Z").workplane().circle(0.010).cutThruAll()
    y_carriage.visual(_mc(y_plate, "y_carriage_plate", assets), material=mats["dark"], name="y_carriage_plate", material_class_id="metal.blackened_gunmetal")
    for cy, tag in ((-0.018, "0"), (0.018, "1")):
        clip = cq.Workplane("XY").center(0.015, cy).rect(0.028, 0.004).extrude(0.0015)
        clip = clip.translate((0.0, 0.0, 0.0037))
        y_carriage.visual(_mc(clip, f"stage_clip_{tag}", assets), material=mats["chrome"], name=f"stage_clip_{tag}", material_class_id="metal.chrome_polished")
    y_carriage.visual(
        Box((0.064, 0.024, 0.0012)),
        origin=Origin(xyz=(0.0, 0.0, 0.0044)),
        material=mats["glass"],
        name="specimen_slide", material_class_id="glass.clear_transparent",
    )
    y_carriage.inertial = Inertial.from_geometry(
        Box((Y_PLATE_SIZE[0], Y_PLATE_SIZE[1], Y_PLATE_SIZE[2] + 0.002)),
        mass=0.08,
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
    )
    model.articulation(
        "x_carriage_to_y_carriage",
        ArticulationType.PRISMATIC,
        parent=x_carriage,
        child=y_carriage,
        origin=Origin(xyz=(0.0, 0.0, 0.001)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=0.02, lower=Y_TRAVEL[0], upper=Y_TRAVEL[1]),
    )

    # --- drive knobs (REVOLUTE x2) ---
    # Mounts authored in the optical-axis frame, then offset by -mx so they
    # land on the shifted stage plate while keeping their world placement.
    knob_mounts = [
        Origin(xyz=(-0.075 - mx, 0.0, 0.0), rpy=(0.0, -math.pi / 2.0, 0.0)),
        Origin(xyz=(-0.0075 - mx, 0.060, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
    ]
    for i in range(N_DRIVE_KNOBS):
        knob = model.part(f"drive_knob_{i}")
        knob.visual(
            _mc(_make_drive_knob(DRIVE_KNOB_LENGTH, DRIVE_KNOB_R), f"knob_body_{i}", assets),
            material=mats["dark"],
            name=f"knob_body_{i}", material_class_id="metal.blackened_gunmetal",
        )
        knob.visual(
            Cylinder(radius=DRIVE_KNOB_R * 0.40, length=0.002),
            origin=Origin(xyz=(0.0, 0.0, DRIVE_KNOB_LENGTH + 0.001)),
            material=mats["chrome"],
            name=f"knob_cap_{i}", material_class_id="metal.chrome_polished",
        )
        knob.inertial = Inertial.from_geometry(
            Cylinder(radius=DRIVE_KNOB_R, length=DRIVE_KNOB_LENGTH),
            mass=0.015,
            origin=Origin(xyz=(0.0, 0.0, DRIVE_KNOB_LENGTH * 0.5)),
        )
        model.articulation(
            f"stage_to_drive_knob_{i}",
            ArticulationType.REVOLUTE,
            parent=stage,
            child=knob,
            origin=knob_mounts[i],
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=1.0, velocity=6.0, lower=-math.pi, upper=math.pi),
        )


# --------------------------------------------------------------------------- #
# ILLUMINATION slot
# --------------------------------------------------------------------------- #
def _build_condenser_lamp(model, base, r, mats, *, assets) -> None:
    """S1: black sub-stage condenser/illuminator stack standing on the foot."""
    # Anchor the FIXED joint on the foot top (world z=ANCHOR_Z) where the lamp
    # body stands. Original authoring placed the joint at world z=0.085 (mid
    # body); shift all geometry up by DZ and lower the joint to the foot top so
    # the world placement is unchanged, the origin lands on the foot, and the
    # child still contains (0,0,0).
    anchor_z = 0.035
    dz = 0.085 - anchor_z  # 0.050
    condenser = model.part("condenser")
    lamp = (
        cq.Workplane("XY")
        .workplane(offset=-0.053 + dz)
        .circle(0.026)
        .extrude(0.068)
        .edges(">Z")
        .fillet(0.004)
    )
    condenser.visual(_mc(lamp, "condenser_body", assets), material=mats["black"], name="condenser_body", material_class_id="plastic.opaque_glossy_molded")
    mount = cq.Workplane("XY").workplane(offset=0.013 + dz).circle(0.017).extrude(0.032)
    condenser.visual(_mc(mount, "condenser_mount", assets), material=mats["dark"], name="condenser_mount", material_class_id="metal.blackened_gunmetal")
    condenser.inertial = Inertial.from_geometry(
        Cylinder(radius=0.026, length=0.10), mass=0.18, origin=Origin(xyz=(0.0, 0.0, -0.005 + dz))
    )
    model.articulation(
        "base_to_condenser",
        ArticulationType.FIXED,
        parent=base,
        child=condenser,
        origin=Origin(xyz=(0.0, 0.0, anchor_z)),
    )


def _trunnion_stub(sign: int, disc_r: float, stub_r: float, stub_len: float):
    """S4 helper: horizontal trunnion stub cylinder along Y."""
    embed = 0.002
    y_inner = disc_r - embed
    if sign > 0:
        y_start = y_inner
    else:
        y_start = -(y_inner + stub_len)
    return (
        cq.Workplane("XZ")
        .workplane(offset=y_start)
        .center(0, 0)
        .circle(stub_r)
        .extrude(stub_len)
    )


def _build_tilting_mirror(model, base, r, mats, *, assets) -> None:
    """S4: trunnion fork (FIXED) + round reflector on a REVOLUTE Y tilt."""
    mirror_fork = model.part("mirror_fork")
    base_plate = cq.Workplane("XY").center(0.0, 0.0).rect(FORK_DEPTH_X, FORK_WIDTH_Y).extrude(FORK_BASE_T)
    mirror_fork.visual(_mc(base_plate, "fork_base", assets), material=mats["dark"], name="fork_base", material_class_id="metal.blackened_gunmetal")

    cheek_y = FORK_GAP / 2.0 + CHEEK_T / 2.0
    for sign, tag in ((-1, "n"), (1, "p")):
        cheek = (
            cq.Workplane("XY")
            .workplane(offset=FORK_BASE_T)
            .center(0.0, sign * cheek_y)
            .rect(FORK_DEPTH_X, CHEEK_T)
            .extrude(FORK_CHEEK_H)
        )
        bore = (
            cq.Workplane("XZ")
            .workplane(offset=sign * (cheek_y - CHEEK_T / 2.0))
            .center(0.0, FORK_TRUNNION_Z_LOCAL)
            .circle(FORK_TRUNNION_D / 2.0)
            .extrude(CHEEK_T)
        )
        cheek = cheek.cut(bore)
        mirror_fork.visual(_mc(cheek, f"fork_cheek_{tag}", assets), material=mats["dark"], name=f"fork_cheek_{tag}", material_class_id="metal.blackened_gunmetal")

    fork_stem = cq.Workplane("XY").workplane(offset=-0.003).circle(0.006).extrude(FORK_BASE_T + 0.003)
    mirror_fork.visual(_mc(fork_stem, "fork_stem", assets), material=mats["dark"], name="fork_stem", material_class_id="metal.blackened_gunmetal")
    mirror_fork.inertial = Inertial.from_geometry(
        Cylinder(radius=0.028, length=0.068), mass=0.10, origin=Origin(xyz=(0.0, 0.0, 0.030))
    )
    model.articulation(
        "base_to_mirror_fork",
        ArticulationType.FIXED,
        parent=base,
        child=mirror_fork,
        origin=Origin(xyz=(0.0, 0.0, FORK_MOUNT_Z)),
    )

    mirror = model.part("mirror")
    # Compensating shift (cf. stage -mx, condenser dz): the revolute origin sits
    # on the cheek trunnion (world y=cheek_y), so the child link frame is there
    # too. Build ALL mirror geometry at local y -= cheek_y so its WORLD placement
    # stays centered on the optical axis (y=0), between the two fork cheeks,
    # while the joint origin still lands on the cheek bore.
    my = cheek_y
    mirror_face = (
        cq.Workplane("XY").workplane(offset=-MIRROR_THICK / 2).circle(MIRROR_R).extrude(MIRROR_THICK)
        .translate((0.0, -my, 0.0))
    )
    mirror.visual(_mc(mirror_face, "mirror_face", assets), material=mats["chrome"], name="mirror_face", material_class_id="glass.mirror")
    rim_outer = (
        cq.Workplane("XY").workplane(offset=-MIRROR_THICK / 2 - 0.0005).circle(MIRROR_R + 0.001).extrude(MIRROR_THICK + 0.001)
    )
    rim_hole = (
        cq.Workplane("XY").workplane(offset=-MIRROR_THICK / 2 - 0.001).circle(MIRROR_R - 0.001).extrude(MIRROR_THICK + 0.002)
    )
    rim = rim_outer.cut(rim_hole).translate((0.0, -my, 0.0))
    mirror.visual(_mc(rim, "mirror_rim", assets), material=mats["dark"], name="mirror_rim", material_class_id="metal.blackened_gunmetal")

    stub_len = FORK_GAP / 2.0 - MIRROR_R + STUB_EMBED + 0.002
    for i in range(2):
        # Stub signs flipped relative to the un-shifted build so that after the
        # -my shift, stub_0 reaches the -Y cheek (fork_cheek_n) and stub_1 the
        # +Y cheek (fork_cheek_p), matching the trunnion overlap declarations.
        sign = 1 if i == 0 else -1
        stub = _trunnion_stub(sign, MIRROR_R, STUB_R, stub_len).translate((0.0, -my, 0.0))
        mirror.visual(_mc(stub, f"mirror_stub_{i}", assets), material=mats["dark"], name=f"mirror_stub_{i}", material_class_id="metal.blackened_gunmetal")
    mirror.inertial = Inertial.from_geometry(Cylinder(radius=MIRROR_R, length=MIRROR_THICK), mass=0.04)
    # Anchor the revolute origin on the cheek trunnion bore (y = cheek center):
    # the axis is Y, so the origin may sit anywhere along it. This puts the
    # origin inside the fork cheek (parent) and on the mirror stub (child)
    # rather than in the empty gap between the cheeks.
    cheek_y = FORK_GAP / 2.0 + CHEEK_T / 2.0
    model.articulation(
        "fork_to_mirror",
        ArticulationType.REVOLUTE,
        parent=mirror_fork,
        child=mirror,
        origin=Origin(xyz=(0.0, cheek_y, FORK_TRUNNION_Z_LOCAL)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=MIRROR_TILT[0], upper=MIRROR_TILT[1]),
    )


def _build_led_disc(model, base, r, mats, *, assets) -> None:
    """S5: flat LED diffuser puck recessed into the foot top."""
    illuminator = model.part("illuminator")
    puck_housing = cq.Workplane("XY").circle(0.022).extrude(0.009).edges(">Z").fillet(0.001)
    illuminator.visual(_mc(puck_housing, "puck_housing", assets), material=mats["black"], name="puck_housing", material_class_id="plastic.opaque_glossy_molded")
    diffuser = cq.Workplane("XY").workplane(offset=0.009).circle(0.018).extrude(0.0015)
    illuminator.visual(_mc(diffuser, "puck_diffuser", assets), material=mats["glass"], name="puck_diffuser", material_class_id="glass.frosted_smooth")
    bezel = cq.Workplane("XY").workplane(offset=0.0085).circle(0.021).circle(0.019).extrude(0.002)
    illuminator.visual(_mc(bezel, "puck_bezel", assets), material=mats["chrome"], name="puck_bezel", material_class_id="metal.chrome_polished")
    illuminator.inertial = Inertial.from_geometry(
        Cylinder(radius=0.022, length=0.011), mass=0.04, origin=Origin(xyz=(0.0, 0.0, 0.0055))
    )
    model.articulation(
        "base_to_illuminator",
        ArticulationType.FIXED,
        parent=base,
        child=illuminator,
        origin=Origin(xyz=(0.0, 0.0, 0.026)),
    )


# --------------------------------------------------------------------------- #
# Top-level build / dispatch
# --------------------------------------------------------------------------- #
_HEAD_FACTORIES = {
    "monocular_inclined": _build_monocular_inclined,
    "binocular_head": _build_binocular_head,
    "vertical_straight": _build_vertical_straight,
}
_FOCUS_FACTORIES = {
    "side_coaxial": _build_side_coaxial,
    "dual_coarse_fine": _build_dual_coarse_fine,
    "mechanical_xy": _build_mechanical_xy,
}
_ILLUM_FACTORIES = {
    "condenser_lamp": _build_condenser_lamp,
    "tilting_mirror": _build_tilting_mirror,
    "led_disc": _build_led_disc,
}


def build_microscope(
    config: MicroscopeConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or MicroscopeConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-microscope-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["adopted_source_ids"] = ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8")
    model.meta["slot_choices"] = slot_choices_for_config(r)

    mats = _register_materials(model, r.palette)

    base = _build_base(model, r, mats, assets=assets)
    _HEAD_FACTORIES[r.head](model, base, r, mats, assets=assets)
    _build_nosepiece(model, base, r, mats, assets=assets)
    _FOCUS_FACTORIES[r.focus_stage](model, base, r, mats, assets=assets)
    _ILLUM_FACTORIES[r.illumination](model, base, r, mats, assets=assets)
    return model


def build_seeded_microscope(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_microscope(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedMicroscopeConfig) -> list[tuple[str, str]]:
    return [
        ("head", r.head),
        ("illumination", r.illumination),
        ("focus_stage", r.focus_stage),
        ("objective_count", f"obj_{r.objective_count}"),
        ("palette_style", r.palette_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def run_microscope_tests(model: ArticulatedObject, config: MicroscopeConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    parts = {p.name for p in model.parts}

    nosepiece = model.get_part("nosepiece_turret")
    stage = model.get_part("stage")

    turret_joint = model.get_articulation("head_to_nosepiece")

    # --- IDENTITY: nosepiece turret CONTINUOUS about Z (every seed) ---
    ctx.check(
        "turret is continuous about Z",
        turret_joint.articulation_type == ArticulationType.CONTINUOUS
        and tuple(turret_joint.axis) == (0.0, 0.0, 1.0),
        details=f"type={turret_joint.articulation_type}, axis={turret_joint.axis}",
    )

    # --- IDENTITY: a real bounded VERTICAL (Z) focus prismatic is always
    # present. Every variant (including mechanical_xy) focuses via the
    # ``arm_to_stage`` Z prismatic; the X carriage is specimen positioning, NOT
    # focus, so it no longer satisfies this identity invariant on its own. ---
    stage_joint = model.get_articulation("arm_to_stage")
    ctx.check(
        "stage focus travel is a bounded vertical prismatic",
        stage_joint.articulation_type == ArticulationType.PRISMATIC
        and tuple(stage_joint.axis) == (0.0, 0.0, 1.0)
        and stage_joint.motion_limits is not None
        and stage_joint.motion_limits.lower == STAGE_TRAVEL[0]
        and stage_joint.motion_limits.upper == STAGE_TRAVEL[1],
        details=f"type={stage_joint.articulation_type}, limits={stage_joint.motion_limits}",
    )

    # --- Objective multiplicity assertion (updated for variable N) ---
    obj_barrels = [
        v for v in nosepiece.visuals if v.name and v.name.startswith("objective_barrel_")
    ]
    ctx.check(
        f"turret carries {r.objective_count} objective lenses",
        len(obj_barrels) == r.objective_count,
        details=f"objective barrels found: {len(obj_barrels)}, expected {r.objective_count}",
    )
    ctx.check(
        "objective count is a valid multiplicity",
        r.objective_count in OBJ_MULTIPLICITY,
        details=f"objective_count={r.objective_count}, allowed={OBJ_MULTIPLICITY}",
    )

    # --- Rests on the ground: global z-min ~ 0 ---
    zmin = None
    for part in model.parts:
        aabb = ctx.part_world_aabb(part)
        if aabb is not None:
            zmin = aabb[0][2] if zmin is None else min(zmin, aabb[0][2])
    ctx.check(
        "model rests on the ground (z-min ~ 0)",
        zmin is not None and abs(zmin) < 1.0e-4,
        details=f"global z-min={zmin}",
    )

    # --- Vertical optical stack ordering ---
    stage_aabb = ctx.part_world_aabb(stage)
    disc_aabb = ctx.part_element_world_aabb(nosepiece, elem="turret_disc")
    ctx.check(
        "turret disc hangs above the stage",
        disc_aabb is not None and stage_aabb is not None and disc_aabb[0][2] > stage_aabb[1][2],
        details=f"disc_min_z={disc_aabb[0][2] if disc_aabb else None}, "
        f"stage_max_z={stage_aabb[1][2] if stage_aabb else None}",
    )
    ctx.expect_within(
        nosepiece, stage, axes="xy", margin=0.005, name="turret stays over the stage footprint"
    )

    # --- FK sweep: every objective clears arm/head through a full turret sweep ---
    sweep_ok = True
    sweep_details = []
    min_radius = None
    max_radius = None
    n_angles = 12
    n = r.objective_count
    for k in range(n_angles):
        ang = k * (2.0 * math.pi / n_angles)
        with ctx.pose({turret_joint: ang}):
            for i in range(n):
                bb = ctx.part_element_world_aabb(nosepiece, elem=f"objective_barrel_{i}")
                if bb is None:
                    sweep_ok = False
                    sweep_details.append(f"missing barrel {i} @ {ang:.2f}")
                    continue
                cx = 0.5 * (bb[0][0] + bb[1][0])
                cy = 0.5 * (bb[0][1] + bb[1][1])
                rad = math.hypot(cx, cy)
                min_radius = rad if min_radius is None else min(min_radius, rad)
                max_radius = rad if max_radius is None else max(max_radius, rad)
                if bb[1][0] >= ARM_FRONT_X - 1.0e-4:
                    sweep_ok = False
                    sweep_details.append(f"barrel {i} @ {ang:.2f} hits arm: max_x={bb[1][0]:.4f}")
                if bb[1][2] >= HEAD_Z0 - 1.0e-4:
                    sweep_ok = False
                    sweep_details.append(f"barrel {i} @ {ang:.2f} hits head: max_z={bb[1][2]:.4f}")
    ctx.check(
        "objectives clear arm/head through a full turret sweep (12 angles)",
        sweep_ok,
        details="; ".join(sweep_details) if sweep_details else "all clear",
    )
    ctx.check(
        "objective centroids trace an off-axis circle (visible rotation)",
        min_radius is not None
        and max_radius is not None
        and min_radius > OBJ_BARREL_R
        and (max_radius - min_radius) < 0.004,
        details=f"centroid orbit radius range=[{min_radius}, {max_radius}], barrel r={OBJ_BARREL_R}",
    )

    # --- Decisive pose: a quarter turn swings objective 0 sideways ---
    rest_obj = ctx.part_element_world_aabb(nosepiece, elem="objective_barrel_0")
    with ctx.pose({turret_joint: math.pi / 2.0}):
        turned_obj = ctx.part_element_world_aabb(nosepiece, elem="objective_barrel_0")
    moved = 0.0
    if rest_obj is not None and turned_obj is not None:
        moved = math.hypot(
            0.5 * (turned_obj[0][0] + turned_obj[1][0]) - 0.5 * (rest_obj[0][0] + rest_obj[1][0]),
            0.5 * (turned_obj[0][1] + turned_obj[1][1]) - 0.5 * (rest_obj[0][1] + rest_obj[1][1]),
        )
    ctx.check(
        "rotating the turret visibly swings an objective",
        moved > 0.02,
        details=f"objective 0 center moved {moved:.4f} m under a quarter turn",
    )

    # --- Per-slot motion + overlap declarations ---
    _check_focus_stage(ctx, model, r, parts)
    _check_illumination(ctx, model, r, parts)
    _declare_base_overlaps(ctx, model, r, parts)

    return ctx.report()


def _check_focus_stage(ctx, model, r, parts) -> None:
    base = model.get_part("base")
    stage = model.get_part("stage")

    if r.focus_stage == "side_coaxial":
        focus_knob = model.get_part("focus_knob")
        focus_joint = model.get_articulation("arm_to_focus_knob")
        ctx.check(
            "focus knob is continuous",
            focus_joint.articulation_type == ArticulationType.CONTINUOUS,
            details=f"type={focus_joint.articulation_type}",
        )
        rest_ptr = ctx.part_element_world_aabb(focus_knob, elem="knob_nub_p")
        with ctx.pose({focus_joint: math.pi / 2.0}):
            turned_ptr = ctx.part_element_world_aabb(focus_knob, elem="knob_nub_p")
        d_knob = 0.0
        if rest_ptr is not None and turned_ptr is not None:
            d_knob = math.hypot(
                0.5 * (turned_ptr[0][0] + turned_ptr[1][0]) - 0.5 * (rest_ptr[0][0] + rest_ptr[1][0]),
                0.5 * (turned_ptr[0][2] + turned_ptr[1][2]) - 0.5 * (rest_ptr[0][2] + rest_ptr[1][2]),
            )
        ctx.check(
            "focus knob rotates about its axle (off-axis nub moves)",
            d_knob > 0.008,
            details=f"knob nub moved {d_knob:.4f} m under a quarter turn",
        )
        knob_aabb = ctx.part_world_aabb(focus_knob)
        ctx.check(
            "focus knobs project from both sides of the arm",
            knob_aabb is not None
            and knob_aabb[0][1] < -ARM_HALF_WIDTH - 0.005
            and knob_aabb[1][1] > ARM_HALF_WIDTH + 0.005,
            details=f"knob y-range=[{knob_aabb[0][1] if knob_aabb else None}, {knob_aabb[1][1] if knob_aabb else None}]",
        )
        ctx.allow_overlap(
            base, focus_knob, elem_a="arm_limb", elem_b="knob_axle",
            reason="The focus axle passes through the bearing bore in the arm column.",
        )
        ctx.allow_overlap(
            base, focus_knob, elem_a="focus_bearing_boss", elem_b="knob_axle",
            reason="The focus axle runs through the raised bearing boss on the arm.",
        )
        ctx.allow_overlap(
            base, base, elem_a="arm_limb", elem_b="focus_bearing_boss",
            reason="The focus bearing boss is cast onto the arm column.",
        )
        for tag in ("p", "n"):
            ctx.allow_overlap(
                base, focus_knob, elem_a="focus_bearing_boss", elem_b=f"knob_disc_{tag}",
                reason="The knob disc seats against the arm bearing collar.",
            )
        ctx.expect_contact(
            base, focus_knob, elem_a="arm_limb", elem_b="knob_axle",
            name="focus axle is captured in the arm",
        )
        for tag in ("p", "n"):
            ctx.allow_overlap(
                focus_knob, focus_knob, elem_a="knob_axle", elem_b=f"knob_disc_{tag}",
                reason="The knob disc is keyed onto the through-axle.",
            )
            ctx.allow_overlap(
                focus_knob, focus_knob, elem_a=f"knob_disc_{tag}", elem_b=f"knob_nub_{tag}",
                reason="Index nub is riveted 0.5 mm into the knob face.",
            )

    elif r.focus_stage == "dual_coarse_fine":
        coarse_focus = model.get_part("coarse_focus")
        fine_focus = model.get_part("fine_focus")
        coarse_joint = model.get_articulation("arm_to_coarse_focus")
        fine_joint = model.get_articulation("arm_to_fine_focus")
        ctx.check(
            "coarse + fine focus knobs are both continuous",
            coarse_joint.articulation_type == ArticulationType.CONTINUOUS
            and fine_joint.articulation_type == ArticulationType.CONTINUOUS,
            details=f"coarse={coarse_joint.articulation_type}, fine={fine_joint.articulation_type}",
        )
        rest_ptr = ctx.part_element_world_aabb(coarse_focus, elem="coarse_nub_1")
        with ctx.pose({coarse_joint: math.pi / 2.0}):
            turned_ptr = ctx.part_element_world_aabb(coarse_focus, elem="coarse_nub_1")
        d_knob = 0.0
        if rest_ptr is not None and turned_ptr is not None:
            d_knob = math.hypot(
                0.5 * (turned_ptr[0][0] + turned_ptr[1][0]) - 0.5 * (rest_ptr[0][0] + rest_ptr[1][0]),
                0.5 * (turned_ptr[0][2] + turned_ptr[1][2]) - 0.5 * (rest_ptr[0][2] + rest_ptr[1][2]),
            )
        ctx.check(
            "coarse focus knob rotates about its axle (off-axis nub moves)",
            d_knob > 0.005,
            details=f"coarse nub moved {d_knob:.4f} m under a quarter turn",
        )
        ctx.allow_overlap(
            base, coarse_focus, elem_a="arm_limb", elem_b="coarse_axle",
            reason="The coarse focus axle passes through the bearing bore in the arm column.",
        )
        ctx.allow_overlap(
            base, fine_focus, elem_a="arm_limb", elem_b="fine_axle",
            reason="The fine focus axle passes through the arm bearing bore.",
        )
        ctx.allow_overlap(
            base, base, elem_a="arm_limb", elem_b="focus_bearing_boss",
            reason="The focus bearing boss is cast onto the arm column.",
        )
        ctx.allow_overlap(
            base, coarse_focus, elem_a="focus_bearing_boss", elem_b="coarse_axle",
            reason="The coarse axle runs through the raised bearing boss on the arm.",
        )
        ctx.allow_overlap(
            base, fine_focus, elem_a="focus_bearing_boss", elem_b="fine_axle",
            reason="The fine axle runs through the raised bearing boss on the arm.",
        )
        ctx.allow_overlap(
            coarse_focus, fine_focus, elem_a="coarse_axle", elem_b="fine_axle",
            reason="The fine focus axle passes coaxially through the hollow coarse axle bore.",
        )
        for i in range(2):
            ctx.allow_overlap(
                coarse_focus, fine_focus, elem_a=f"coarse_disc_{i}", elem_b="fine_axle",
                reason="The fine axle passes through the coarse disc hub bore.",
            )
            ctx.allow_overlap(
                coarse_focus, coarse_focus, elem_a="coarse_axle", elem_b=f"coarse_disc_{i}",
                reason="The coarse disc is keyed onto the coarse axle.",
            )
            ctx.allow_overlap(
                coarse_focus, coarse_focus, elem_a=f"coarse_disc_{i}", elem_b=f"coarse_nub_{i}",
                reason="Index nub is riveted into the coarse disc face.",
            )
            for k in range(8):
                ctx.allow_overlap(
                    coarse_focus, coarse_focus, elem_a=f"coarse_disc_{i}", elem_b=f"coarse_ridge_{i}_{k}",
                    reason="Knurled grip ridge is embossed into the coarse disc perimeter.",
                )
            ctx.allow_overlap(
                fine_focus, fine_focus, elem_a="fine_axle", elem_b=f"fine_disc_{i}",
                reason="The fine disc is keyed onto the fine axle.",
            )
            ctx.allow_overlap(
                fine_focus, fine_focus, elem_a=f"fine_disc_{i}", elem_b=f"fine_nub_{i}",
                reason="Index nub is riveted into the fine disc face.",
            )
            for k in range(6):
                ctx.allow_overlap(
                    fine_focus, fine_focus, elem_a=f"fine_disc_{i}", elem_b=f"fine_ridge_{i}_{k}",
                    reason="Knurled grip ridge is embossed into the fine disc perimeter.",
                )
        # Coarse disc flanks the stage bracket in Y; XZ projection may overlap.
        ctx.allow_overlap(
            coarse_focus, stage, elem_a="coarse_disc_1", elem_b="stage_bracket",
            reason="The coarse disc flanks the stage bracket in Y with a gap; XZ overlap is projected proximity.",
        )

    elif r.focus_stage == "mechanical_xy":
        x_carriage = model.get_part("x_carriage")
        y_carriage = model.get_part("y_carriage")
        x_joint = model.get_articulation("stage_to_x_carriage")
        y_joint = model.get_articulation("x_carriage_to_y_carriage")
        ctx.check(
            "xy carriages are bounded prismatics (X then Y)",
            x_joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(x_joint.axis) == (1.0, 0.0, 0.0)
            and y_joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(y_joint.axis) == (0.0, 1.0, 0.0),
            details=f"x_axis={x_joint.axis}, y_axis={y_joint.axis}",
        )
        # X carriage translates.
        rest_x = ctx.part_world_aabb(x_carriage)
        with ctx.pose({x_joint: X_TRAVEL[1]}):
            moved_x = ctx.part_world_aabb(x_carriage)
        dx = None
        if rest_x is not None and moved_x is not None:
            dx = 0.5 * (moved_x[0][0] + moved_x[1][0]) - 0.5 * (rest_x[0][0] + rest_x[1][0])
        ctx.check(
            "x carriage translates along X",
            dx is not None and abs(dx - X_TRAVEL[1]) < 1.0e-4,
            details=f"x carriage moved {dx} m for upper travel {X_TRAVEL[1]}",
        )
        # Lock-in (fix #1): at the full +X travel the frame rear must stay in
        # front of the arm face so it never drives into the fixed arm column.
        with ctx.pose({x_joint: X_TRAVEL[1]}):
            xc_at_max = ctx.part_element_world_aabb(x_carriage, elem="x_carriage_frame")
        ctx.check(
            "x_carriage clears the arm front face across full +X travel",
            xc_at_max is not None and xc_at_max[1][0] < ARM_FRONT_X - 0.001,
            details=f"x_carriage_frame max_x at +travel="
            f"{xc_at_max[1][0] if xc_at_max else None}, arm_front={ARM_FRONT_X}",
        )
        # Drive knobs are revolute.
        for i in range(N_DRIVE_KNOBS):
            kj = model.get_articulation(f"stage_to_drive_knob_{i}")
            ctx.check(
                f"drive knob {i} is revolute",
                kj.articulation_type == ArticulationType.REVOLUTE,
                details=f"type={kj.articulation_type}",
            )
        ctx.expect_contact(
            stage, x_carriage, elem_a="stage_plate", elem_b="x_carriage_frame",
            name="x_carriage frame contacts the stage plate top",
        )
        ctx.expect_within(
            y_carriage, x_carriage, axes="xy",
            inner_elem="y_carriage_plate", outer_elem="x_carriage_frame", margin=0.001,
            name="y_carriage plate stays inside the x_carriage frame opening",
        )
        for tag in ("0", "1"):
            ctx.allow_overlap(
                y_carriage, y_carriage, elem_a="y_carriage_plate", elem_b=f"stage_clip_{tag}",
                reason="Spring clip foot is screwed 0.3 mm into the y_carriage plate top.",
            )
        ctx.allow_overlap(
            y_carriage, y_carriage, elem_a="y_carriage_plate", elem_b="specimen_slide",
            reason="The glass slide rests seated on the y_carriage plate over the aperture.",
        )
        for i in range(N_DRIVE_KNOBS):
            knob = model.get_part(f"drive_knob_{i}")
            ctx.allow_overlap(
                stage, knob, elem_a="stage_plate", elem_b=f"knob_body_{i}",
                reason=f"Drive knob {i} mounting boss enters the stage plate edge by 3 mm.",
            )
            ctx.allow_overlap(
                knob, knob, elem_a=f"knob_body_{i}", elem_b=f"knob_cap_{i}",
                reason=f"Drive knob {i} cap accent sits on the knob tip.",
            )

    # Shared stage overlaps (apply to all focus styles).
    ctx.allow_overlap(
        base, stage, elem_a="arm_limb", elem_b="stage_plate",
        reason="The stage plate rear slides in the dovetail ways on the arm front.",
    )
    ctx.allow_overlap(
        base, stage, elem_a="arm_limb", elem_b="stage_bracket",
        reason="The stage saddle bracket rides in the dovetail ways on the arm front.",
    )
    ctx.expect_contact(
        base, stage, elem_a="arm_limb", elem_b="stage_bracket",
        name="stage saddle engages the arm dovetail",
    )
    ctx.allow_overlap(
        stage, stage, elem_a="stage_plate", elem_b="stage_bracket",
        reason="The saddle bracket bolts 1 mm into the plate underside.",
    )
    if "specimen_slide" in {v.name for v in stage.visuals}:
        ctx.allow_overlap(
            stage, stage, elem_a="stage_plate", elem_b="specimen_slide",
            reason="The glass slide rests seated on the stage plate over the aperture.",
        )
        for tag in ("p", "n"):
            ctx.allow_overlap(
                stage, stage, elem_a="stage_plate", elem_b=f"stage_clip_{tag}",
                reason="Spring clip foot is screwed into the stage top plate.",
            )


def _check_illumination(ctx, model, r, parts) -> None:
    base = model.get_part("base")

    if r.illumination == "condenser_lamp":
        condenser = model.get_part("condenser")
        ctx.allow_overlap(
            base, condenser, elem_a="foot", elem_b="condenser_body",
            reason="The illuminator housing bolts 3 mm into the top of the foot.",
        )
        ctx.expect_contact(
            base, condenser, elem_a="foot", elem_b="condenser_body",
            name="illuminator stands on the base",
        )
        ctx.allow_overlap(
            condenser, condenser, elem_a="condenser_body", elem_b="condenser_mount",
            reason="The condenser mount is press-fit 2 mm into the lamp housing.",
        )

    elif r.illumination == "tilting_mirror":
        mirror_fork = model.get_part("mirror_fork")
        mirror = model.get_part("mirror")
        tilt_joint = model.get_articulation("fork_to_mirror")
        ctx.check(
            "mirror tilt is revolute about Y",
            tilt_joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(tilt_joint.axis) == (0.0, 1.0, 0.0),
            details=f"type={tilt_joint.articulation_type}, axis={tilt_joint.axis}",
        )
        rest_face = ctx.part_element_world_aabb(mirror, elem="mirror_stub_1")
        with ctx.pose({tilt_joint: MIRROR_TILT[1]}):
            tilted_face = ctx.part_element_world_aabb(mirror, elem="mirror_face")
        rest_face2 = ctx.part_element_world_aabb(mirror, elem="mirror_face")
        moved = 0.0
        if rest_face2 is not None and tilted_face is not None:
            moved = abs(
                0.5 * (tilted_face[0][0] + tilted_face[1][0])
                - 0.5 * (rest_face2[0][0] + rest_face2[1][0])
            ) + abs(tilted_face[1][2] - rest_face2[1][2])
        ctx.check(
            "tilting the mirror moves its reflective face",
            moved > 0.003,
            details=f"mirror face shifted {moved:.4f} m under full tilt; rest_stub={rest_face is not None}",
        )
        # Lock-in (fix #2): the reflector must sit centered on the optical axis
        # (y=0), not shifted onto/through a cheek, and each trunnion stub must
        # reach its own fork cheek bore.
        face_bb = ctx.part_element_world_aabb(mirror, elem="mirror_face")
        face_ycen = 0.5 * (face_bb[0][1] + face_bb[1][1]) if face_bb is not None else None
        ctx.check(
            "mirror reflector is centered on the optical axis (y=0)",
            face_ycen is not None and abs(face_ycen) < 0.003,
            details=f"mirror_face y-center={face_ycen}",
        )
        stub0_bb = ctx.part_element_world_aabb(mirror, elem="mirror_stub_0")
        stub1_bb = ctx.part_element_world_aabb(mirror, elem="mirror_stub_1")
        cheek_inner = FORK_GAP / 2.0
        ctx.check(
            "trunnion stubs reach into both fork cheek bores",
            stub0_bb is not None
            and stub1_bb is not None
            and stub0_bb[0][1] <= -cheek_inner + 1.0e-4
            and stub1_bb[1][1] >= cheek_inner - 1.0e-4,
            details=f"stub0 min_y={stub0_bb[0][1] if stub0_bb else None}, "
            f"stub1 max_y={stub1_bb[1][1] if stub1_bb else None}, cheek_inner={cheek_inner}",
        )
        ctx.allow_overlap(
            base, mirror_fork, elem_a="foot", elem_b="fork_stem",
            reason="The mirror fork stem plugs 3 mm into the top of the foot.",
        )
        ctx.expect_contact(
            base, mirror_fork, elem_a="foot", elem_b="fork_stem",
            name="mirror fork stem stands on the base foot",
        )
        ctx.allow_overlap(
            mirror_fork, mirror_fork, elem_a="fork_stem", elem_b="fork_base",
            reason="The fork stem extends into the fork base plate for structural continuity.",
        )
        for tag in ("p", "n"):
            ctx.allow_overlap(
                mirror_fork, mirror_fork, elem_a="fork_base", elem_b=f"fork_cheek_{tag}",
                reason="The fork cheek is welded to the fork base plate.",
            )
        ctx.allow_overlap(
            mirror, mirror, elem_a="mirror_face", elem_b="mirror_rim",
            reason="The bezel rim encircles the mirror disc edge.",
        )
        for i in range(2):
            ctx.allow_overlap(
                mirror, mirror, elem_a="mirror_face", elem_b=f"mirror_stub_{i}",
                reason=f"Trunnion stub {i} is embedded 2 mm into the mirror disc edge.",
            )
        ctx.allow_overlap(
            mirror_fork, mirror, elem_a="fork_cheek_n", elem_b="mirror_stub_0",
            reason="Mirror trunnion stub 0 enters the fork cheek bore as a pivot bearing.",
        )
        ctx.allow_overlap(
            mirror_fork, mirror, elem_a="fork_cheek_p", elem_b="mirror_stub_1",
            reason="Mirror trunnion stub 1 enters the fork cheek bore as a pivot bearing.",
        )

    elif r.illumination == "led_disc":
        illuminator = model.get_part("illuminator")
        ctx.allow_overlap(
            base, illuminator, elem_a="foot", elem_b="puck_housing",
            reason="The LED puck housing is recessed 3 mm into the foot top surface.",
        )
        ctx.expect_contact(
            base, illuminator, elem_a="foot", elem_b="puck_housing",
            name="illuminator puck is seated in the base recess",
        )
        ctx.allow_overlap(
            illuminator, illuminator, elem_a="puck_housing", elem_b="puck_diffuser",
            reason="The frosted diffuser lens sits on top of the puck housing.",
        )
        ctx.allow_overlap(
            illuminator, illuminator, elem_a="puck_housing", elem_b="puck_bezel",
            reason="The chrome bezel ring wraps around the diffuser on the puck housing.",
        )


def _declare_base_overlaps(ctx, model, r, parts) -> None:
    base = model.get_part("base")
    nosepiece = model.get_part("nosepiece_turret")

    # Base internal castings.
    ctx.allow_overlap(
        base, base, elem_a="foot", elem_b="arm_limb",
        reason="The arm column is cast into the top of the foot.",
    )
    ctx.allow_overlap(
        base, base, elem_a="arm_limb", elem_b="head_housing",
        reason="The head housing is cast onto the forward jut of the arm.",
    )

    # Head/eyepiece seating + ocular press-fits.
    if r.head == "binocular_head":
        eyepiece = model.get_part("binocular_head")
        ctx.allow_overlap(
            base, eyepiece, elem_a="head_housing", elem_b="bridge_block",
            reason="The binocular head bridge block plugs into the top of the widened head housing.",
        )
        ctx.expect_contact(
            base, eyepiece, elem_a="head_housing", elem_b="bridge_block",
            name="binocular bridge is seated in the head",
        )
        for i in range(2):
            ctx.allow_overlap(
                eyepiece, eyepiece, elem_a="bridge_block", elem_b=f"tube_{i}",
                reason=f"Tube {i} is cast 3 mm into the bridge block.",
            )
            ctx.allow_overlap(
                eyepiece, eyepiece, elem_a=f"tube_{i}", elem_b=f"ocular_{i}",
                reason=f"Ocular barrel {i} is press-fit 2 mm into tube {i}.",
            )
            ctx.allow_overlap(
                eyepiece, eyepiece, elem_a=f"ocular_{i}", elem_b=f"lens_{i}",
                reason=f"Teal lens {i} is seated 1 mm into ocular {i} top cap.",
            )
    else:
        eyepiece = model.get_part("eyepiece_tube")
        ctx.allow_overlap(
            base, eyepiece, elem_a="head_housing", elem_b="tube_body",
            reason="The monocular tube plugs into the top of the head housing.",
        )
        ctx.expect_contact(
            base, eyepiece, elem_a="head_housing", elem_b="tube_body",
            name="eyepiece tube is seated in the head",
        )
        ctx.allow_overlap(
            eyepiece, eyepiece, elem_a="tube_body", elem_b="ocular_barrel",
            reason="The ocular barrel is press-fit 2 mm into the tube top.",
        )
        ctx.allow_overlap(
            eyepiece, eyepiece, elem_a="ocular_barrel", elem_b="ocular_lens",
            reason="The ocular lens is seated 1 mm into the ocular top cap.",
        )

    # Turret spindle in the head bore; objectives thread into the disc.
    ctx.allow_overlap(
        base, nosepiece, elem_a="head_housing", elem_b="turret_disc",
        reason="The turret spindle hub rides in a bearing bore in the head underside.",
    )
    ctx.expect_contact(
        base, nosepiece, elem_a="head_housing", elem_b="turret_disc",
        name="turret spindle is captured in the head bore",
    )
    for i in range(r.objective_count):
        ctx.allow_overlap(
            nosepiece, nosepiece, elem_a="turret_disc", elem_b=f"objective_barrel_{i}",
            reason="Objective barrel threads 2 mm into the turret disc.",
        )
        ctx.allow_overlap(
            nosepiece, nosepiece, elem_a=f"objective_barrel_{i}", elem_b=f"objective_ring_{i}",
            reason="Colored magnification band wraps around the barrel.",
        )


__all__ = [
    "MicroscopeConfig",
    "ResolvedMicroscopeConfig",
    "config_from_seed",
    "resolve_config",
    "build_microscope",
    "build_seeded_microscope",
    "slot_choices_for_seed",
    "slot_choices_for_config",
    "run_microscope_tests",
    "__modular__",
]
