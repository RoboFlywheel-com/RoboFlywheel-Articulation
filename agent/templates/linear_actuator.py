# SPDX-License-Identifier: Apache-2.0

"""Linear actuator procedural template (modular, enum-slot driven).

__modular__ = True. Structure derives from nine 5-star sources under
Robotics / Linear actuator (two picture origins + seven verified forks). Every
module below traces to a real source model.py (see the per-form docstrings and
the spec `specs_modular_v1/linear_actuator.md`).

Slot graph (parallel-children around a fixed `frame` root):

    frame --[PRISMATIC axis x]--> carriage(s)         (the linear output stroke)
    frame --[REVOLUTE  axis x/z]--> drive             (screw / pulley; absent for
                                                       direct_piston)

Three reported structural slots + two multiplicity axes:

  body_form (③ Primary Form Family):
    - extruded_rail      Planar Boundary Form   (origins A/B)
    - barrel_tube        Volumetric Envelope    (fork form_rod_cylinder / probe_pneumatic)
    - telescoping_column Macro Surface / stages (fork skeleton_telescoping)
  drive_mechanism (②), gated by body_form:
    - lead_screw   (origins A/B; all forms)
    - belt_pulley  (fork mechanism_belt; extruded_rail only)
    - direct_piston(fork probe_pneumatic; no rotary drive)
  motor_layout (①), extruded_rail only:
    - inline          (origins A/B)
    - parallel_offset (fork skeleton_parallel_motor)
  multiplicity:
    - carriage_count  {1,2}   (fork n_carriage2)      extruded_rail only
    - guide_rod_count {1,2}   (fork n_guiderod1)       extruded_rail only

Geometry is intentionally Box/Cylinder-only: picture-origin B and forks
n_carriage2 / n_guiderod1 / skeleton_telescoping build the identical structural
cell purely from Box/Cylinder and pass, so this is category-faithful primitive
usage (not a downgrade of a sophisticated primitive under Rule 3). The helical
lead-screw thread is rendered as a loop of thin ring Cylinders exactly as
picture-origin B does (`thread_crest_{i}`), keeping compile cheap.

Rule 1: every non-articulating detail (grooves, slots, screw heads, feet, thread
crests, belt spans, motor cap) is a `part.visual(...)` on the part it moves with,
never a FIXED-joint part. Rule 5: `run_..._tests` samples every joint pose and
adds targeted `ctx.pose(...)` motion checks; intentional captured/nested overlaps
(guide rod in bushing, rod in barrel, nested tubes, belt on pulley) are declared
element-scoped `ctx.allow_overlap(...)`.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

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
)

__modular__ = True

BodyForm = Literal["extruded_rail", "barrel_tube", "telescoping_column"]
DriveMechanism = Literal["lead_screw", "belt_pulley", "direct_piston"]
MotorLayout = Literal["inline", "parallel_offset"]
PaletteTheme = Literal[
    "brushed_aluminum",
    "black_industrial",
    "blue_barrel",
    "steel_gray",
]

_HALF_PI = math.pi / 2.0

# --------------------------------------------------------------------------- #
# Palette presets (⑥ material / finish). Keys are the material tokens every
# form uses; each theme covers metal + painted + dark accent families.
# --------------------------------------------------------------------------- #
LA_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "brushed_aluminum": {
        "body": (0.72, 0.74, 0.72, 1.0),
        "dark": (0.05, 0.05, 0.055, 1.0),
        "steel": (0.82, 0.83, 0.80, 1.0),
        "screw": (0.64, 0.66, 0.64, 1.0),
        "belt": (0.045, 0.045, 0.040, 1.0),
        "brass": (0.78, 0.54, 0.24, 1.0),
        "shadow": (0.0, 0.0, 0.0, 1.0),
        "rod": (0.90, 0.92, 0.88, 1.0),
        "barrel": (0.66, 0.68, 0.66, 1.0),
    },
    "black_industrial": {
        "body": (0.12, 0.12, 0.13, 1.0),
        "dark": (0.02, 0.02, 0.025, 1.0),
        "steel": (0.78, 0.80, 0.80, 1.0),
        "screw": (0.60, 0.62, 0.62, 1.0),
        "belt": (0.03, 0.03, 0.03, 1.0),
        "brass": (0.72, 0.50, 0.22, 1.0),
        "shadow": (0.0, 0.0, 0.0, 1.0),
        "rod": (0.86, 0.88, 0.86, 1.0),
        "barrel": (0.09, 0.09, 0.10, 1.0),
    },
    "blue_barrel": {
        "body": (0.60, 0.63, 0.66, 1.0),
        "dark": (0.06, 0.06, 0.07, 1.0),
        "steel": (0.80, 0.82, 0.80, 1.0),
        "screw": (0.62, 0.64, 0.64, 1.0),
        "belt": (0.04, 0.04, 0.04, 1.0),
        "brass": (0.78, 0.60, 0.20, 1.0),
        "shadow": (0.0, 0.0, 0.0, 1.0),
        "rod": (0.88, 0.90, 0.88, 1.0),
        "barrel": (0.18, 0.28, 0.52, 1.0),
    },
    "steel_gray": {
        "body": (0.55, 0.57, 0.58, 1.0),
        "dark": (0.08, 0.08, 0.09, 1.0),
        "steel": (0.83, 0.85, 0.84, 1.0),
        "screw": (0.66, 0.68, 0.66, 1.0),
        "belt": (0.05, 0.05, 0.045, 1.0),
        "brass": (0.75, 0.55, 0.26, 1.0),
        "shadow": (0.0, 0.0, 0.0, 1.0),
        "rod": (0.90, 0.91, 0.90, 1.0),
        "barrel": (0.42, 0.44, 0.46, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class LinearActuatorConfig:
    body_form: BodyForm = "extruded_rail"
    drive_mechanism: DriveMechanism = "lead_screw"
    motor_layout: MotorLayout = "inline"
    carriage_count: int = 1
    guide_rod_count: int = 2
    palette_theme: PaletteTheme = "brushed_aluminum"

    # ⑤ continuous dimensions / travel (independent unless noted).
    rail_length: float = 0.700
    carriage_travel: float = 0.170
    screw_radius: float = 0.0055
    barrel_length: float = 0.420
    barrel_radius: float = 0.038
    stroke: float = 0.260


@dataclass(frozen=True)
class ResolvedLinearActuatorConfig:
    body_form: BodyForm
    drive_mechanism: DriveMechanism
    motor_layout: MotorLayout
    carriage_count: int
    guide_rod_count: int
    palette_theme: PaletteTheme
    rail_length: float
    carriage_travel: float
    screw_radius: float
    barrel_length: float
    barrel_radius: float
    stroke: float
    palette: dict[str, tuple[float, float, float, float]]


# --------------------------------------------------------------------------- #
# Deterministic procedural sampling (seed 0 is NOT special-cased).
# body_form is the master choice; drive/motor/counts are sampled from the
# compatible set for that form (compatibility gating, spec §9).
# --------------------------------------------------------------------------- #
def _compatible_drives(body_form: str) -> tuple[str, ...]:
    if body_form == "extruded_rail":
        return ("lead_screw", "belt_pulley", "direct_piston")
    # barrel_tube / telescoping_column: round bodies, no external toothed belt
    return ("lead_screw", "direct_piston")


def config_from_seed(seed: int) -> LinearActuatorConfig:
    rng = random.Random(seed)

    body_form: BodyForm = rng.choice(
        ("extruded_rail", "extruded_rail", "barrel_tube", "telescoping_column")
    )  # extruded_rail weighted (dominant real archetype)
    drive_mechanism: DriveMechanism = rng.choice(_compatible_drives(body_form))  # type: ignore[assignment]

    if body_form == "extruded_rail":
        motor_layout: MotorLayout = rng.choice(("inline", "parallel_offset"))
        carriage_count = rng.choice((1, 1, 2))  # single dominant, dual real but rarer
        guide_rod_count = rng.choice((2, 2, 1))
    else:
        motor_layout = "inline"
        carriage_count = 1
        guide_rod_count = 2  # unused by round forms; reported constant

    palette_theme: PaletteTheme = rng.choice(tuple(LA_PALETTE_PRESETS.keys()))

    rail_length = round(rng.uniform(0.58, 0.84), 4)
    carriage_travel = round(rng.uniform(0.12, 0.22), 4)
    screw_radius = round(rng.uniform(0.0050, 0.0075), 5)
    barrel_length = round(rng.uniform(0.36, 0.48), 4)
    barrel_radius = round(rng.uniform(0.032, 0.046), 4)
    stroke = round(rng.uniform(0.20, 0.30), 4)

    return LinearActuatorConfig(
        body_form=body_form,
        drive_mechanism=drive_mechanism,
        motor_layout=motor_layout,
        carriage_count=carriage_count,
        guide_rod_count=guide_rod_count,
        palette_theme=palette_theme,
        rail_length=rail_length,
        carriage_travel=carriage_travel,
        screw_radius=screw_radius,
        barrel_length=barrel_length,
        barrel_radius=barrel_radius,
        stroke=stroke,
    )


def resolve_config(config: LinearActuatorConfig) -> ResolvedLinearActuatorConfig:
    if str(config.body_form) not in {"extruded_rail", "barrel_tube", "telescoping_column"}:
        raise ValueError(f"Unsupported body_form: {config.body_form}")
    if str(config.palette_theme) not in LA_PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    body_form = config.body_form

    # Gate drive/motor/counts to the legal set for this form (keeps corner
    # seeds — which perturb numeric fields only — consistent by construction).
    drive = str(config.drive_mechanism)
    if drive not in _compatible_drives(body_form):
        drive = "lead_screw"

    if body_form == "extruded_rail":
        motor_layout = str(config.motor_layout)
        if motor_layout not in {"inline", "parallel_offset"}:
            motor_layout = "inline"
        carriage_count = 2 if int(config.carriage_count) >= 2 else 1
        guide_rod_count = 1 if int(config.guide_rod_count) <= 1 else 2
    else:
        motor_layout = "inline"
        carriage_count = 1
        guide_rod_count = 2

    rail_length = max(0.55, min(float(config.rail_length), 0.86))
    screw_radius = max(0.0045, min(float(config.screw_radius), 0.0080))
    barrel_length = max(0.34, min(float(config.barrel_length), 0.50))
    barrel_radius = max(0.030, min(float(config.barrel_radius), 0.048))

    # ⑤ travel is bounded (inequality) so the carriage(s) never run off the
    # rail or into the end plates / each other. Usable span = rail_length minus
    # end margins; for 2 carriages the span is shared, each block ~0.11 long.
    usable = rail_length - 0.16
    if carriage_count == 2:
        # Two carriages sit at fixed x = ±0.100 (spacing 0.200), each block
        # 0.110 long. travel must keep the rear carriage's extended right edge
        # clear of the front carriage's rest left edge:
        #   0.100 - 0.055 >= (-0.100 + travel + 0.055)  ->  travel <= 0.090.
        travel_cap = 0.060  # 0.090 minus a 0.030 safety margin
    else:
        travel_cap = max(0.06, usable - 0.14)
    carriage_travel = max(0.06, min(float(config.carriage_travel), travel_cap))

    stroke_cap = barrel_length * 0.72
    stroke = max(0.12, min(float(config.stroke), stroke_cap))

    palette = dict(LA_PALETTE_PRESETS[str(config.palette_theme)])

    return ResolvedLinearActuatorConfig(
        body_form=body_form,  # type: ignore[arg-type]
        drive_mechanism=drive,  # type: ignore[arg-type]
        motor_layout=motor_layout,  # type: ignore[arg-type]
        carriage_count=carriage_count,
        guide_rod_count=guide_rod_count,
        palette_theme=config.palette_theme,
        rail_length=rail_length,
        carriage_travel=carriage_travel,
        screw_radius=screw_radius,
        barrel_length=barrel_length,
        barrel_radius=barrel_radius,
        stroke=stroke,
        palette=palette,
    )


def slot_choices_for_config(r: ResolvedLinearActuatorConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("body_form", str(r.body_form)),
        ("drive_mechanism", str(r.drive_mechanism)),
        ("motor_layout", str(r.motor_layout)),
        ("carriage_count", str(r.carriage_count)),
        ("guide_rod_count", str(r.guide_rod_count)),
        ("palette_theme", str(r.palette_theme)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Shared geometric quantities (Contract 3c — single-sourced).
# --------------------------------------------------------------------------- #
_RAIL_H = 0.045          # rail extrusion height (top at _RAIL_TOP)
_RAIL_TOP = 0.0575       # world z of rail top surface
_SCREW_Z = 0.090         # world z of lead-screw / belt-drive axis (clear of rail + carriage)
_CARRIAGE_JOINT_Z = 0.123  # world z of the carriage prismatic joint origin
_BEARING_SHOE_HALF_H = 0.0075
_BELT_Z = _SCREW_Z


def _end_plate_x(rail_length: float) -> float:
    """Half-distance to the end-plate centres (just outside the rail ends)."""
    return rail_length * 0.5 + 0.020


_GUIDE_ROD_Z = 0.077
_GUIDE_ROD_R = 0.0065
_CARRIAGE_BLOCK_BOTTOM_Z = _CARRIAGE_JOINT_Z - 0.021  # block half-height 0.021


def _guide_rod_layout(guide_rod_count: int) -> list[tuple[float, float]]:
    """(y, z) of each guide rod. 2 rods flank the central screw; 1 rod is
    offset to +y beside the central screw (source n_guiderod1 keeps the
    extrusion body for anti-rotation). Both cases keep the rod out of the
    central screw's yz footprint so the carriage shoe can never hit the screw."""
    if guide_rod_count == 1:
        return [(0.030, _GUIDE_ROD_Z)]
    return [(0.032, _GUIDE_ROD_Z), (-0.032, _GUIDE_ROD_Z)]


# --------------------------------------------------------------------------- #
# EXTRUDED RAIL form. Adapted from picture-origin B
# (rec_...__001, model.py:L32-L219) plus forks n_carriage2 / n_guiderod1 /
# skeleton_parallel_motor / mechanism_belt. All Box/Cylinder.
# --------------------------------------------------------------------------- #
def _build_rail_frame(frame, r: ResolvedLinearActuatorConfig) -> None:
    L = r.rail_length
    epx = _end_plate_x(L)

    # Rail extrusion + T-slot decoration (Rule 1: all parent visuals).
    frame.visual(
        Box((L, 0.085, _RAIL_H)),
        origin=Origin(xyz=(0.0, 0.0, 0.035)),
        material="body",
        name="rail_extrusion", material_class_id=("metal.aluminum_bare" if r.palette_theme in {"brushed_aluminum", "blue_barrel", "steel_gray"} else "metal.blackened_gunmetal"),
    )
    frame.visual(
        Box((L * 0.97, 0.112, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.0065)),
        material="dark",
        name="bottom_foot", material_class_id="metal.blackened_gunmetal",
    )
    for y, name in ((0.044, "side_slot_0"), (-0.044, "side_slot_1")):
        frame.visual(
            Box((L * 0.88, 0.004, 0.012)),
            origin=Origin(xyz=(0.0, y, 0.041)),
            material="shadow",
            name=name, material_class_id="metal.blackened_gunmetal",
        )
    for y, name in ((0.023, "top_slot_0"), (-0.023, "top_slot_1")):
        frame.visual(
            Box((L * 0.87, 0.008, 0.004)),
            origin=Origin(xyz=(0.0, y, 0.059)),
            material="shadow",
            name=name, material_class_id="metal.blackened_gunmetal",
        )

    # End plates.
    for x, name in ((-epx, "end_plate_0"), (epx, "end_plate_1")):
        frame.visual(
            Box((0.050, 0.118, 0.090)),
            origin=Origin(xyz=(x, 0.0, 0.045)),
            material="dark",
            name=name, material_class_id="metal.blackened_gunmetal",
        )

    # Motor housing: inline (coaxial behind left plate) or parallel_offset
    # (beside the rail in -Y with a reduction-belt pair). Fork
    # skeleton_parallel_motor (rec_..._parallel_motor:L273-L319).
    if r.motor_layout == "parallel_offset":
        # Folded drivetrain: motor sits beside the rail in -Y, coupled to the
        # screw axis by a reduction belt. All visuals form one connected cluster
        # anchored to end_plate_0 (fork skeleton_parallel_motor).
        frame.visual(
            Box((0.008, 0.150, 0.120)),
            origin=Origin(xyz=(-epx + 0.018, -0.050, _SCREW_Z - 0.010)),
            material="steel",
            name="motor_bracket", material_class_id="metal.steel_bare",
        )
        frame.visual(
            Box((0.084, 0.070, 0.070)),
            origin=Origin(xyz=(-epx + 0.012, -0.100, _SCREW_Z - 0.010)),
            material="dark",
            name="motor_block", material_class_id="metal.blackened_gunmetal",
        )
        frame.visual(
            Cylinder(radius=0.014, length=0.014),
            origin=Origin(xyz=(-epx + 0.030, -0.100, _SCREW_Z - 0.010), rpy=(0.0, _HALF_PI, 0.0)),
            material="steel",
            name="motor_pulley", material_class_id="metal.steel_bare",
        )
        # Single reduction belt box bridging the motor pulley (y=-0.100) up to
        # the screw axis (y=0) at the drive end.
        frame.visual(
            Box((0.006, 0.110, 0.010)),
            origin=Origin(xyz=(-epx + 0.030, -0.050, _SCREW_Z - 0.010)),
            material="belt",
            name="reduction_belt", material_class_id="rubber.smooth_plain",
        )
        frame.visual(
            Box((0.004, 0.140, 0.090)),
            origin=Origin(xyz=(-epx + 0.024, -0.050, _SCREW_Z - 0.005)),
            material="dark",
            name="drive_cover", material_class_id="metal.blackened_gunmetal",
        )
    else:
        frame.visual(
            Box((0.084, 0.128, 0.095)),
            origin=Origin(xyz=(-epx - 0.042, 0.0, 0.061)),
            material="dark",
            name="motor_block", material_class_id="metal.blackened_gunmetal",
        )
        frame.visual(
            Box((0.090, 0.106, 0.040)),
            origin=Origin(xyz=(-epx - 0.055, 0.0, 0.118)),
            material="dark",
            name="motor_cap", material_class_id="metal.blackened_gunmetal",
        )

    # Guide rods (FIXED to frame, run through the carriage bushings).
    rod_len = L + 0.035
    for index, (y, z) in enumerate(_guide_rod_layout(r.guide_rod_count)):
        frame.visual(
            Cylinder(radius=0.0065, length=rod_len),
            origin=Origin(xyz=(0.0, y, z), rpy=(0.0, _HALF_PI, 0.0)),
            material="steel",
            name=f"guide_rod_{index}", material_class_id="metal.steel_bare",
        )

    # Top mounting-hole decoration (Rule 1 parent visuals).
    n_holes = max(3, int(L / 0.12))
    for index in range(n_holes):
        x = -L * 0.42 + index * (L * 0.84 / max(1, n_holes - 1))
        frame.visual(
            Cylinder(radius=0.0065, length=0.006),
            origin=Origin(xyz=(x, 0.0, 0.054)),
            material="shadow",
            name=f"rail_hole_{index}", material_class_id="metal.blackened_gunmetal",
        )

    frame.inertial = Inertial.from_geometry(
        Box((L, 0.118, 0.13)),
        mass=3.0,
        origin=Origin(xyz=(0.0, 0.0, 0.055)),
    )


def _build_rail_carriage(carriage, r: ResolvedLinearActuatorConfig, *, index: int) -> None:
    """One carriage block + bearing shoes. Adapted from origin B carriage
    (model.py:L129-L176) and fork n_carriage2 (indexed visuals)."""
    block_len = 0.110 if r.carriage_count == 2 else 0.130
    carriage.visual(
        Box((block_len, 0.090, 0.042)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="body",
        name=f"carriage_block_{index}", material_class_id=("metal.aluminum_bare" if r.palette_theme in {"brushed_aluminum", "blue_barrel", "steel_gray"} else "metal.blackened_gunmetal"),
    )
    # Bearing shoes: one per guide rod. Each shoe spans from ~2mm into the
    # block underside down to ~2mm past the guide-rod top, so it connects the
    # block to the rod (island-free within the part) AND rides the rod (a small
    # cross-part overlap declared as a linear bushing in run_tests).
    for j, (y, z) in enumerate(_guide_rod_layout(r.guide_rod_count)):
        rod_top = z + _GUIDE_ROD_R
        shoe_top_world = _CARRIAGE_BLOCK_BOTTOM_Z + 0.002
        shoe_bottom_world = rod_top - 0.002
        shoe_h = shoe_top_world - shoe_bottom_world
        shoe_center_local = 0.5 * (shoe_top_world + shoe_bottom_world) - _CARRIAGE_JOINT_Z
        carriage.visual(
            Box((block_len * 0.82, 0.020, shoe_h)),
            origin=Origin(xyz=(0.0, y, shoe_center_local)),
            material="steel",
            name=f"bearing_shoe_{index}_{j}", material_class_id="metal.steel_bare",
        )
    # Raised mounting boss + hole decoration.
    carriage.visual(
        Box((block_len * 0.55, 0.030, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, 0.026)),
        material="body",
        name=f"mount_boss_{index}", material_class_id=("metal.aluminum_bare" if r.palette_theme in {"brushed_aluminum", "blue_barrel", "steel_gray"} else "metal.blackened_gunmetal"),
    )
    for hx in (-0.030, 0.0, 0.030):
        for hy in (-0.022, 0.022):
            carriage.visual(
                Cylinder(radius=0.0050, length=0.004),
                origin=Origin(xyz=(hx, hy, 0.023)),
                material="shadow",
                name=f"top_hole_{index}_{int((hx + 0.05) * 1000)}_{int((hy + 0.03) * 1000)}", material_class_id="metal.blackened_gunmetal",
            )

    carriage.inertial = Inertial.from_geometry(
        Box((block_len, 0.090, 0.06)),
        mass=0.30,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )


def _build_lead_screw_rail(part, r: ResolvedLinearActuatorConfig) -> None:
    """Central rotating lead screw for the rail form. Thread rendered as a loop
    of ring Cylinders (origin B `thread_crest_{i}`, model.py:L186-L193)."""
    L = r.rail_length
    core_len = L * 0.86
    part.visual(
        Cylinder(radius=r.screw_radius, length=core_len),
        origin=Origin(rpy=(0.0, _HALF_PI, 0.0)),
        material="screw",
        name="screw_core", material_class_id="metal.steel_bare",
    )
    crest_r = r.screw_radius + 0.0020
    n_crest = max(6, min(int(core_len / 0.032), 22))
    span = core_len - 0.06
    for i in range(n_crest):
        x = -span * 0.5 + i * (span / max(1, n_crest - 1))
        part.visual(
            Cylinder(radius=crest_r, length=0.0032),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
            material="screw",
            name=f"thread_crest_{i:02d}", material_class_id="metal.steel_bare",
        )
    for i, x in enumerate((-core_len * 0.5 - 0.011, core_len * 0.5 + 0.011)):
        part.visual(
            Cylinder(radius=r.screw_radius + 0.007, length=0.022),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
            material="steel",
            name=f"coupler_{i}", material_class_id="metal.steel_bare",
        )
    # Bearing journals bridge from the screw core out to the end-plate bearing
    # bores: each is one cylinder overlapping the core (within-part connection)
    # and the end plate (frame anchoring — allow_overlap in run_tests).
    epx = _end_plate_x(L)
    core_end = core_len * 0.5
    j_inner = core_end - 0.010
    j_outer = epx + 0.005
    j_len = j_outer - j_inner
    j_center = 0.5 * (j_inner + j_outer)
    for i, sign in enumerate((-1.0, 1.0)):
        part.visual(
            Cylinder(radius=r.screw_radius + 0.006, length=j_len),
            origin=Origin(xyz=(sign * j_center, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
            material="steel",
            name=f"bearing_journal_{i}", material_class_id="metal.steel_bare",
        )
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=r.screw_radius + 0.007, length=core_len),
        mass=0.12,
        origin=Origin(rpy=(0.0, _HALF_PI, 0.0)),
    )


def _build_drive_pulley(part, r: ResolvedLinearActuatorConfig) -> None:
    """Belt drive pulley (rotates about z). Fork mechanism_belt
    (rec_..._belt:L419-L431)."""
    part.visual(
        Cylinder(radius=0.020, length=0.016),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="dark",
        name="pulley_body", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.024, length=0.002),
        origin=Origin(xyz=(0.0, 0.0, 0.009)),
        material="dark",
        name="pulley_flange_top", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.024, length=0.002),
        origin=Origin(xyz=(0.0, 0.0, -0.009)),
        material="dark",
        name="pulley_flange_bottom", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.005, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, -0.022)),
        material="steel",
        name="drive_coupler", material_class_id="metal.steel_bare",
    )
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=0.024, length=0.02),
        mass=0.05,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )


def _add_belt_frame_visuals(frame, r: ResolvedLinearActuatorConfig) -> tuple[float, float]:
    """Idler pulley + belt loop spans + drive boss on the frame. Returns the
    (drive_x, idler_x) pulley centres. Belt is FIXED decoration."""
    L = r.rail_length
    drive_x = -L * 0.5 + 0.055
    idler_x = L * 0.5 - 0.055
    belt_r = 0.020
    frame.visual(
        Cylinder(radius=belt_r, length=0.016),
        origin=Origin(xyz=(idler_x, 0.0, _BELT_Z)),
        material="dark",
        name="idler_pulley", material_class_id="metal.blackened_gunmetal",
    )
    # Support bosses running from the rail top up to belt height so the idler
    # (and, via allow_overlap, the drive pulley) connect to the frame body.
    boss_h = _BELT_Z - _RAIL_TOP + 0.010
    boss_z = _RAIL_TOP + boss_h * 0.5 - 0.005
    frame.visual(
        Cylinder(radius=0.006, length=boss_h),
        origin=Origin(xyz=(idler_x, 0.0, boss_z)),
        material="steel",
        name="idler_boss", material_class_id="metal.steel_bare",
    )
    frame.visual(
        Cylinder(radius=0.006, length=boss_h),
        origin=Origin(xyz=(drive_x, 0.0, boss_z)),
        material="steel",
        name="pulley_boss", material_class_id="metal.steel_bare",
    )
    # Belt spans overlap the idler pulley (y just inside its radius) so the
    # idler+belt cluster is one connected sub-tree.
    span_len = idler_x - drive_x
    for sgn, name in ((+1.0, "belt_span_front"), (-1.0, "belt_span_back")):
        frame.visual(
            Box((span_len, 0.005, 0.012)),
            origin=Origin(xyz=(0.5 * (drive_x + idler_x), sgn * (belt_r - 0.002), _BELT_Z)),
            material="belt",
            name=name, material_class_id="rubber.smooth_plain",
        )
    return drive_x, idler_x


# --------------------------------------------------------------------------- #
# BARREL form. Adapted from fork form_rod_cylinder (rec_..._form_rod_cylinder)
# and probe_pneumatic (rec_..._probe_pneumatic). Round tube + coaxial rod.
# --------------------------------------------------------------------------- #
def _build_barrel_frame(frame, r: ResolvedLinearActuatorConfig) -> None:
    bl = r.barrel_length
    br = r.barrel_radius
    half = bl * 0.5
    # Barrel body (solid cylinder reads as the round barrel envelope).
    frame.visual(
        Cylinder(radius=br, length=bl),
        origin=Origin(rpy=(0.0, _HALF_PI, 0.0)),
        material="barrel",
        name="barrel_tube", material_class_id=("metal.aluminum_bare" if r.palette_theme in {"brushed_aluminum", "blue_barrel", "steel_gray"} else "metal.blackened_gunmetal"),
    )
    cap_r = br + 0.008
    # Caps embed 2mm into the barrel ends (island-free connection).
    frame.visual(
        Cylinder(radius=cap_r, length=0.018),
        origin=Origin(xyz=(-half - 0.007, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
        material="dark",
        name="rear_cap", material_class_id="metal.blackened_gunmetal",
    )
    frame.visual(
        Cylinder(radius=cap_r, length=0.018),
        origin=Origin(xyz=(half + 0.007, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
        material="dark",
        name="front_cap", material_class_id="metal.blackened_gunmetal",
    )
    # Rod gland ring on the front cap outer face (overlaps the cap).
    frame.visual(
        Cylinder(radius=0.016, length=0.012),
        origin=Origin(xyz=(half + 0.018, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
        material="steel",
        name="gland_ring", material_class_id="metal.steel_bare",
    )
    # Rear motor housing (only when a rotary drive exists); overlaps rear cap.
    if r.drive_mechanism == "lead_screw":
        frame.visual(
            Cylinder(radius=br * 0.9, length=0.090),
            origin=Origin(xyz=(-half - 0.058, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
            material="dark",
            name="motor_block", material_class_id="metal.blackened_gunmetal",
        )
    else:
        # Pneumatic: rear port bosses instead of a motor (probe_pneumatic).
        for i, xp in enumerate((-half * 0.5, half * 0.5)):
            frame.visual(
                Cylinder(radius=0.009, length=0.016),
                origin=Origin(xyz=(xp, 0.0, br + 0.006)),
                material="brass",
                name=f"port_boss_{i}", material_class_id="metal.brass_polished",
            )
    # Barrel band + mounting feet.
    frame.visual(
        Cylinder(radius=br + 0.003, length=0.010),
        origin=Origin(rpy=(0.0, _HALF_PI, 0.0)),
        material="steel",
        name="barrel_band", material_class_id="metal.steel_bare",
    )
    foot_z = -(br + 0.006)
    for i, xp in enumerate((-bl * 0.25, bl * 0.25)):
        frame.visual(
            Box((0.055, 0.050, 0.016)),
            origin=Origin(xyz=(xp, 0.0, foot_z)),
            material="dark",
            name=f"mount_foot_{i}", material_class_id="metal.blackened_gunmetal",
        )
    frame.inertial = Inertial.from_geometry(
        Cylinder(radius=cap_r, length=bl + 0.14),
        mass=1.4,
        origin=Origin(rpy=(0.0, _HALF_PI, 0.0)),
    )


def _barrel_rod_center_at_rest(r: ResolvedLinearActuatorConfig) -> float:
    """X of the carriage joint origin so the rod protrudes past the front cap
    yet keeps engagement inside the barrel."""
    half = r.barrel_length * 0.5
    return half + 0.030  # gland face is at half+0.018; joint just past it


def _build_barrel_rod(carriage, r: ResolvedLinearActuatorConfig) -> None:
    # Rod sized so at rest the piston sits near the rear inside the barrel and
    # the tip protrudes past the front cap; stays engaged at full stroke.
    rod_len = r.barrel_length - 0.02
    # Rod extends backward (-x) into the barrel from the joint origin.
    carriage.visual(
        Cylinder(radius=0.011, length=rod_len),
        origin=Origin(xyz=(-rod_len * 0.5, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
        material="rod",
        name="carriage_block_0", material_class_id="metal.chrome_polished",
    )
    carriage.visual(
        Cylinder(radius=0.016, length=0.012),
        origin=Origin(xyz=(0.006, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
        material="steel",
        name="rod_end_disk", material_class_id="metal.steel_bare",
    )
    # Piston disk near the rod base (rides the bore — sealed piston).
    piston_x = -rod_len + 0.028
    carriage.visual(
        Cylinder(radius=r.barrel_radius - 0.004, length=0.014),
        origin=Origin(xyz=(piston_x, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
        material="dark",
        name="piston_disk", material_class_id="metal.blackened_gunmetal",
    )
    carriage.inertial = Inertial.from_geometry(
        Cylinder(radius=0.016, length=rod_len),
        mass=0.20,
        origin=Origin(xyz=(-rod_len * 0.5, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
    )


def _build_lead_screw_barrel(part, r: ResolvedLinearActuatorConfig) -> None:
    screw_len = r.barrel_length - 0.05
    part.visual(
        Cylinder(radius=r.screw_radius, length=screw_len),
        origin=Origin(rpy=(0.0, _HALF_PI, 0.0)),
        material="screw",
        name="screw_core", material_class_id="metal.steel_bare",
    )
    crest_r = r.screw_radius + 0.0022
    n_crest = max(6, min(int(screw_len / 0.030), 18))
    span = screw_len - 0.05
    for i in range(n_crest):
        x = -span * 0.5 + i * (span / max(1, n_crest - 1))
        part.visual(
            Cylinder(radius=crest_r, length=0.0032),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
            material="screw",
            name=f"thread_crest_{i:02d}", material_class_id="metal.steel_bare",
        )
    part.visual(
        Cylinder(radius=r.screw_radius + 0.006, length=0.028),
        origin=Origin(xyz=(-screw_len * 0.5 - 0.014, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
        material="brass",
        name="drive_coupler", material_class_id="metal.brass_polished",
    )
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=crest_r, length=screw_len),
        mass=0.10,
        origin=Origin(rpy=(0.0, _HALF_PI, 0.0)),
    )


# --------------------------------------------------------------------------- #
# TELESCOPING form. Adapted from fork skeleton_telescoping
# (rec_..._skeleton_telescoping, model.py:L17-L157). Nested prismatic tubes.
# --------------------------------------------------------------------------- #
_TELESCOPE_STAGES = 3


def _telescope_params(r: ResolvedLinearActuatorConfig) -> list[dict]:
    base_r = r.barrel_radius
    base_len = r.barrel_length + 0.08
    out: list[dict] = []
    for i in range(_TELESCOPE_STAGES):
        out.append(
            {
                "radius": base_r - i * 0.008,
                "length": base_len - i * 0.08,
                "upper": 0.0 if i == 0 else min(0.15, r.stroke * 0.55),
            }
        )
    return out


def _add_tube_visuals(part, *, radius, length, base_name, is_base) -> None:
    tube_name = "rail_extrusion" if is_base else f"{base_name}_tube"
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=(length / 2.0, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
        material="body",
        name=tube_name, material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Cylinder(radius=radius * 1.08, length=0.018),
        origin=Origin(xyz=(0.009, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
        material="dark",
        name=f"{base_name}_base_flange", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=radius * 1.02, length=0.012),
        origin=Origin(xyz=(length - 0.006, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
        material="dark",
        name=f"{base_name}_tip_ring", material_class_id="metal.blackened_gunmetal",
    )


# --------------------------------------------------------------------------- #
# Top-level build
# --------------------------------------------------------------------------- #
def build_linear_actuator(
    config: LinearActuatorConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name="linear_actuator",
        assets=assets,
        meta={"category": "Robotics / Linear actuator"},
    )
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    if r.body_form == "extruded_rail":
        _build_rail(model, r)
    elif r.body_form == "barrel_tube":
        _build_barrel(model, r)
    else:
        _build_telescoping(model, r)

    model.meta["template_slug"] = "linear_actuator"
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]
    return model


def _build_rail(model: ArticulatedObject, r: ResolvedLinearActuatorConfig) -> None:
    frame = model.part("frame")
    _build_rail_frame(frame, r)

    # Belt drive adds idler/belt/boss visuals to the frame.
    drive_x = -r.rail_length * 0.5 + 0.055
    if r.drive_mechanism == "belt_pulley":
        drive_x, _idler_x = _add_belt_frame_visuals(frame, r)

    # Carriages (parallel prismatic children of frame).
    if r.carriage_count == 2:
        offsets = (-0.100, 0.100)
    else:
        offsets = (0.0,)
    for i, x_off in enumerate(offsets):
        carriage = model.part(f"carriage_{i}")
        _build_rail_carriage(carriage, r, index=i)
        model.articulation(
            f"frame_to_carriage_{i}",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=carriage,
            origin=Origin(xyz=(x_off, 0.0, _CARRIAGE_JOINT_Z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=160.0, velocity=0.35, lower=0.0, upper=r.carriage_travel
            ),
        )

    # Drive part.
    if r.drive_mechanism == "lead_screw":
        screw = model.part("lead_screw")
        _build_lead_screw_rail(screw, r)
        model.articulation(
            "screw_spin",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=screw,
            origin=Origin(xyz=(0.0, 0.0, _SCREW_Z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=20.0, lower=-math.pi, upper=math.pi),
        )
    elif r.drive_mechanism == "belt_pulley":
        pulley = model.part("drive_pulley")
        _build_drive_pulley(pulley, r)
        model.articulation(
            "drive_pulley_spin",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=pulley,
            origin=Origin(xyz=(drive_x, 0.0, _BELT_Z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=8.0, velocity=20.0, lower=-math.pi, upper=math.pi),
        )
    # direct_piston: no rotary drive part.


def _build_barrel(model: ArticulatedObject, r: ResolvedLinearActuatorConfig) -> None:
    frame = model.part("frame")
    _build_barrel_frame(frame, r)

    carriage = model.part("carriage_0")
    _build_barrel_rod(carriage, r)
    model.articulation(
        "frame_to_carriage_0",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=carriage,
        origin=Origin(xyz=(_barrel_rod_center_at_rest(r), 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=800.0, velocity=0.4, lower=0.0, upper=r.stroke),
    )

    if r.drive_mechanism == "lead_screw":
        screw = model.part("lead_screw")
        _build_lead_screw_barrel(screw, r)
        model.articulation(
            "screw_spin",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=screw,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=20.0, lower=-math.pi, upper=math.pi),
        )


def _build_telescoping(model: ArticulatedObject, r: ResolvedLinearActuatorConfig) -> None:
    frame = model.part("frame")
    params = _telescope_params(r)

    # Motor at the base.
    frame.visual(
        Box((0.084, 0.128, 0.095)),
        origin=Origin(xyz=(-0.062, 0.0, 0.0)),
        material="dark",
        name="motor_block", material_class_id="metal.blackened_gunmetal",
    )
    frame.visual(
        Box((0.055, 0.100, 0.096)),
        origin=Origin(xyz=(-0.013, 0.0, 0.0)),
        material="dark",
        name="motor_bracket", material_class_id="metal.blackened_gunmetal",
    )
    _add_tube_visuals(
        frame, radius=params[0]["radius"], length=params[0]["length"], base_name="stage_0", is_base=True
    )
    frame.inertial = Inertial.from_geometry(
        Box((params[0]["length"], params[0]["radius"] * 2.2, params[0]["radius"] * 2.2)),
        mass=1.4,
        origin=Origin(xyz=(params[0]["length"] * 0.5, 0.0, 0.0)),
    )

    parents = [frame]
    for i in range(1, _TELESCOPE_STAGES):
        stage = model.part(f"stage_{i}")
        _add_tube_visuals(
            stage, radius=params[i]["radius"], length=params[i]["length"], base_name=f"stage_{i}", is_base=False
        )
        stage.inertial = Inertial.from_geometry(
            Box((params[i]["length"], params[i]["radius"] * 2.2, params[i]["radius"] * 2.2)),
            mass=0.5,
            origin=Origin(xyz=(params[i]["length"] * 0.5, 0.0, 0.0)),
        )
        model.articulation(
            f"stage_slide_{i}",
            ArticulationType.PRISMATIC,
            parent=parents[i - 1],
            child=stage,
            origin=Origin(xyz=(0.05, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=160.0, velocity=0.35, lower=0.0, upper=params[i]["upper"]
            ),
        )
        parents.append(stage)

    if r.drive_mechanism == "lead_screw":
        screw = model.part("lead_screw")
        screw_len = params[0]["length"] + 0.08
        screw.visual(
            Cylinder(radius=r.screw_radius, length=screw_len),
            origin=Origin(xyz=(screw_len * 0.5, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
            material="screw",
            name="screw_core", material_class_id="metal.steel_bare",
        )
        crest_r = r.screw_radius + 0.0022
        n_crest = max(6, min(int(screw_len / 0.030), 20))
        for i in range(n_crest):
            x = 0.02 + i * (screw_len - 0.06) / max(1, n_crest - 1)
            screw.visual(
                Cylinder(radius=crest_r, length=0.004),
                origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
                material="screw",
                name=f"thread_crest_{i:02d}", material_class_id="metal.steel_bare",
            )
        screw.inertial = Inertial.from_geometry(
            Cylinder(radius=crest_r, length=screw_len),
            mass=0.10,
            origin=Origin(xyz=(screw_len * 0.5, 0.0, 0.0), rpy=(0.0, _HALF_PI, 0.0)),
        )
        model.articulation(
            "screw_spin",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=screw,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=20.0, lower=-math.pi, upper=math.pi),
        )


def build_seeded_linear_actuator(seed: int) -> ArticulatedObject:
    return build_linear_actuator(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Tests / QC
# --------------------------------------------------------------------------- #
def _declare_rail_overlaps(ctx: TestContext, model: ArticulatedObject, r) -> None:
    frame = model.get_part("frame")
    n_car = r.carriage_count
    rod_names = [f"guide_rod_{j}" for j in range(len(_guide_rod_layout(r.guide_rod_count)))]
    for i in range(n_car):
        carriage = model.get_part(f"carriage_{i}")
        # Bushing fit: bearing shoe slides on the guide rod (small overlap).
        for j in range(len(rod_names)):
            ctx.allow_overlap(
                carriage,
                frame,
                elem_a=f"bearing_shoe_{i}_{j}",
                elem_b=rod_names[j],
                reason="Linear bushing: the carriage bearing shoe rides on the guide rod.",
            )
    if r.drive_mechanism == "lead_screw":
        screw = model.get_part("lead_screw")
        for i in range(2):
            ctx.allow_overlap(
                frame,
                screw,
                elem_a=f"end_plate_{i}",
                elem_b=f"bearing_journal_{i}",
                reason="The rotating screw journal is seated in the end-plate bearing bore.",
            )
        # Inline motor sits just behind the left end plate; the screw's drive
        # journal enters the motor coupling.
        ctx.allow_overlap(
            frame,
            screw,
            elem_a="motor_block",
            elem_b="bearing_journal_0",
            reason="The screw's drive-end journal enters the motor coupling.",
        )
        if r.motor_layout == "parallel_offset":
            # In the folded layout the screw's drive journal passes through the
            # motor bracket / drive-cover bearing bore at the drive end.
            for elem in ("motor_bracket", "drive_cover", "reduction_belt"):
                ctx.allow_overlap(
                    frame,
                    screw,
                    elem_a=elem,
                    elem_b="bearing_journal_0",
                    reason="The screw drive journal passes through the drive-end bracket / belt bearing bore.",
                )
    if r.drive_mechanism == "belt_pulley":
        pulley = model.get_part("drive_pulley")
        for boss_elem, pulley_elem in (
            ("pulley_boss", "drive_coupler"),
            ("pulley_boss", "pulley_body"),
        ):
            ctx.allow_overlap(
                frame,
                pulley,
                elem_a=boss_elem,
                elem_b=pulley_elem,
                reason="The drive-pulley body/shaft is journalled on the frame bearing boss.",
            )
        for span in ("belt_span_front", "belt_span_back"):
            ctx.allow_overlap(
                frame,
                pulley,
                elem_a=span,
                elem_b="pulley_body",
                reason="The timing belt wraps around the drive pulley.",
            )


def _declare_barrel_overlaps(ctx: TestContext, model: ArticulatedObject, r) -> None:
    frame = model.get_part("frame")
    carriage = model.get_part("carriage_0")
    frame_elems = ["barrel_tube", "front_cap", "rear_cap", "gland_ring", "barrel_band"]
    if r.drive_mechanism == "lead_screw":
        frame_elems.append("motor_block")
    rod_elems = ["carriage_block_0", "piston_disk"]
    for fe in frame_elems:
        for re_ in rod_elems:
            ctx.allow_overlap(
                frame,
                carriage,
                elem_a=fe,
                elem_b=re_,
                reason="Piston rod / disk is captured inside and passes through the barrel bore and caps.",
            )
    if r.drive_mechanism == "lead_screw":
        screw = model.get_part("lead_screw")
        for elem in ("barrel_tube", "rear_cap", "front_cap", "motor_block", "barrel_band"):
            for se in ("screw_core", "drive_coupler"):
                ctx.allow_overlap(
                    frame,
                    screw,
                    elem_a=elem,
                    elem_b=se,
                    reason="Lead screw / coupler runs coaxially inside the barrel bore.",
                )
        for re_ in rod_elems:
            ctx.allow_overlap(
                carriage,
                screw,
                elem_a=re_,
                elem_b="screw_core",
                reason="Lead screw is nested inside the hollow rod / drives the lead-nut at the rod base.",
            )
        ctx.allow_overlap(
            carriage,
            screw,
            elem_a="carriage_block_0",
            elem_b="drive_coupler",
            reason="Lead-screw drive coupler is nested inside the barrel behind the rod.",
        )


def _declare_telescope_overlaps(ctx: TestContext, model: ArticulatedObject, r) -> None:
    frame = model.get_part("frame")
    stage_parts = {0: frame}
    for i in range(1, _TELESCOPE_STAGES):
        stage_parts[i] = model.get_part(f"stage_{i}")
    stage_elems = {
        0: ["rail_extrusion", "stage_0_base_flange", "stage_0_tip_ring", "motor_bracket"],
    }
    for i in range(1, _TELESCOPE_STAGES):
        stage_elems[i] = [f"stage_{i}_tube", f"stage_{i}_base_flange", f"stage_{i}_tip_ring"]
    # Every inner stage nests inside every outer stage — allow all element pairs.
    for outer in range(_TELESCOPE_STAGES):
        for inner in range(outer + 1, _TELESCOPE_STAGES):
            for ea in stage_elems[outer]:
                for eb in stage_elems[inner]:
                    ctx.allow_overlap(
                        stage_parts[outer],
                        stage_parts[inner],
                        elem_a=ea,
                        elem_b=eb,
                        reason="Telescoping nested-tube sliding fit.",
                    )
    if r.drive_mechanism == "lead_screw":
        screw = model.get_part("lead_screw")
        for i in range(_TELESCOPE_STAGES):
            for ea in stage_elems[i]:
                ctx.allow_overlap(
                    stage_parts[i],
                    screw,
                    elem_a=ea,
                    elem_b="screw_core",
                    reason="Central lead screw runs through the nested telescoping tubes.",
                )


def run_linear_actuator_tests(
    model: ArticulatedObject,
    config: LinearActuatorConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    # Declare intentional captured/nested overlaps BEFORE the overlap gates.
    if r.body_form == "extruded_rail":
        _declare_rail_overlaps(ctx, model, r)
    elif r.body_form == "barrel_tube":
        _declare_barrel_overlaps(ctx, model, r)
    else:
        _declare_telescope_overlaps(ctx, model, r)

    # Baseline-equivalent checks.
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    # Category identity: at least one prismatic linear-output joint on axis x.
    prismatics = [
        a for a in model.articulations if a.articulation_type == ArticulationType.PRISMATIC
    ]
    ctx.check(
        "has_prismatic_linear_output",
        len(prismatics) >= 1,
        f"Expected >=1 PRISMATIC joint, found {len(prismatics)}",
    )
    for a in prismatics:
        ctx.check(
            f"{a.name}_axis_is_x",
            tuple(a.axis) == (1.0, 0.0, 0.0),
            f"Expected prismatic axis (1,0,0), got {tuple(a.axis)}",
        )

    if r.drive_mechanism == "lead_screw":
        spin = model.get_articulation("screw_spin")
        ctx.check(
            "screw_spin_is_revolute",
            spin is not None and spin.articulation_type == ArticulationType.REVOLUTE,
            "Lead-screw drive must expose a REVOLUTE screw_spin joint.",
        )
    elif r.drive_mechanism == "belt_pulley":
        spin = model.get_articulation("drive_pulley_spin")
        ctx.check(
            "drive_pulley_is_revolute_z",
            spin is not None
            and spin.articulation_type == ArticulationType.REVOLUTE
            and tuple(spin.axis) == (0.0, 0.0, 1.0),
            "Belt drive must expose a REVOLUTE drive_pulley_spin about z.",
        )

    # Rule 5: sampled-pose collision sweep across every joint + a targeted
    # motion check proving the primary stroke actually extends the carriage.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    _expect_primary_stroke_extends(ctx, model, r)

    return ctx.report()


def _expect_primary_stroke_extends(ctx: TestContext, model: ArticulatedObject, r) -> None:
    """The primary prismatic joint must move its child measurably along +x."""
    if r.body_form == "telescoping_column":
        joint = model.get_articulation("stage_slide_1")
        child = model.get_part("stage_1")
    else:
        joint = model.get_articulation("frame_to_carriage_0")
        child = model.get_part("carriage_0")
    if joint is None or joint.motion_limits is None:
        return
    upper = joint.motion_limits.upper
    lower = joint.motion_limits.lower or 0.0
    rest = ctx.part_world_position(child)
    with ctx.pose({joint: upper}):
        moved = ctx.part_world_position(child)
    if rest is None or moved is None:
        return
    ctx.check(
        "primary_stroke_extends_along_x",
        moved[0] > rest[0] + (upper - lower) * 0.6,
        f"Carriage should advance ~{upper - lower:.3f}m along +x; rest={rest}, moved={moved}",
    )


__all__ = [
    "BodyForm",
    "DriveMechanism",
    "MotorLayout",
    "PaletteTheme",
    "LinearActuatorConfig",
    "ResolvedLinearActuatorConfig",
    "build_linear_actuator",
    "build_seeded_linear_actuator",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_linear_actuator_tests",
]
