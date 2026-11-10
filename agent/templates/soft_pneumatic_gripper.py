# SPDX-License-Identifier: Apache-2.0

"""Soft pneumatic gripper — modular procedural template.

An end-effector whose grasping members are soft, air-pressurised silicone
bellows fingers mounted to a rigid pneumatic manifold; the fingers bend inward
under pressure to enclose fragile / irregular objects. Structure is
parallel-children off a grounded ``manifold`` chassis (spec
``specs_modular_v1/soft_pneumatic_gripper.md``):

  * ``base_manifold`` builds the grounded ``manifold`` part (mount structure +
    central stack + per-station yoke / hinge-pin / elbow / air-tube hardware)
    and publishes ``model.meta["spg"]`` (station table, arrangement, hinge-pin
    names, support ref).
  * ``finger_form`` reads that meta and emits N static ``finger_{idx}`` parts
    (actuator_base + soft_neck + ``bellow`` mesh in the chosen ③ form family,
    plus a ``finger_{idx}_tip`` when the mechanism is multi-segment) — NO joints.
  * ``actuation_mechanism`` emits every articulation + the mechanism-specific
    parts (per-finger REVOLUTE bend, hose-swivel connector, serial knuckle for
    multi-segment, or a PRISMATIC span carriage for the 2-jaw span mechanism).

The last two slots declare NO ``upstream`` interface (so the assembler emits no
auto chain joint) and re-export the body interface — the parallel-children
pattern used by ``water_filter_pump``.

Sources (data/records/<id>/revisions/rev_000001/model.py):
  S1 origin_radial   = rec_robotics__soft_pneumatic_gripper__001  (crossed-rail radial, corrugated-oval bellows)
  S2 origin_opposing = rec_robotics__soft_pneumatic_gripper__002  (clevis frame, ribbed-fin PneuNet bellows)
  S3 = rec_soft_pneumatic_gripper_var_base_wrist_flange           (round ISO-9409 wrist flange)
  S4 = rec_soft_pneumatic_gripper_var_skeleton_inline             (inline single-rail bank)
  S5 = rec_soft_pneumatic_gripper_var_form_fiber_cylinder         (smooth fiber-reinforced cylinder)
  S5m= rec_soft_pneumatic_gripper_var_mechanism_multisegment      (serial 2-segment progressive curl)
  S6 = rec_soft_pneumatic_gripper_var_mechanism_span_prismatic    (PRISMATIC span-adjust carriage)
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

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
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    ExtrudeWithHolesGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    SphereGeometry,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

BaseArrangement = Literal[
    "crossed_rail_radial", "clevis_frame_opposing", "wrist_flange_radial", "inline_beam"
]
FingerForm = Literal["corrugated_oval", "ribbed_fin_pneunet", "fiber_cylinder"]
ActuationMechanism = Literal["single_swivel", "multi_segment", "span_carriage"]
PaletteStyle = Literal[
    "cyan_silicone", "matte_black", "food_white", "safety_orange", "blue_silicone"
]

# Common world-frame geometry shared by every base so the finger geometry is
# base-independent (only the joint origin differs per station).
BEND_Z = 0.130            # world z of every finger bend-joint origin / hinge axis
SUPPORT_Z = 0.141         # world z of the yoke-bridge support surface top-ish
RADIAL_R = 0.101          # nominal radial finger-circle radius (S1)
OPPOSING_R = 0.052        # opposing 2-jaw half-spacing (S2)
INLINE_PITCH = 0.065      # inline station pitch along +x (S4)


# --------------------------------------------------------------------------- #
# Palette presets — ⑥ colorway. Every .visual(material=...) reads a mats name.
# --------------------------------------------------------------------------- #
PALETTE_STYLES: tuple[str, ...] = (
    "cyan_silicone",
    "matte_black",
    "food_white",
    "safety_orange",
    "blue_silicone",
)

_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "cyan_silicone": {
        "aluminum": (0.72, 0.75, 0.78, 1.0),
        "dark_slot": (0.02, 0.025, 0.03, 1.0),
        "silicone": (0.04, 0.55, 0.70, 1.0),
        "silicone_shadow": (0.02, 0.34, 0.46, 1.0),
        "nylon": (0.88, 0.84, 0.75, 1.0),
        "rubber": (0.01, 0.012, 0.012, 1.0),
        "steel": (0.45, 0.47, 0.50, 1.0),
        "fiber": (0.12, 0.13, 0.16, 1.0),
    },
    "matte_black": {
        "aluminum": (0.78, 0.80, 0.80, 1.0),
        "dark_slot": (0.02, 0.02, 0.022, 1.0),
        "silicone": (0.02, 0.021, 0.023, 1.0),
        "silicone_shadow": (0.06, 0.06, 0.065, 1.0),
        "nylon": (0.86, 0.88, 0.84, 1.0),
        "rubber": (0.01, 0.011, 0.012, 1.0),
        "steel": (0.62, 0.64, 0.65, 1.0),
        "fiber": (0.30, 0.31, 0.33, 1.0),
    },
    "food_white": {
        "aluminum": (0.80, 0.82, 0.84, 1.0),
        "dark_slot": (0.20, 0.21, 0.22, 1.0),
        "silicone": (0.92, 0.92, 0.90, 1.0),
        "silicone_shadow": (0.70, 0.70, 0.68, 1.0),
        "nylon": (0.78, 0.80, 0.82, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
        "steel": (0.55, 0.57, 0.60, 1.0),
        "fiber": (0.55, 0.56, 0.58, 1.0),
    },
    "safety_orange": {
        "aluminum": (0.74, 0.76, 0.78, 1.0),
        "dark_slot": (0.10, 0.09, 0.08, 1.0),
        "silicone": (0.90, 0.42, 0.10, 1.0),
        "silicone_shadow": (0.62, 0.26, 0.06, 1.0),
        "nylon": (0.86, 0.84, 0.78, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
        "steel": (0.50, 0.52, 0.54, 1.0),
        "fiber": (0.20, 0.18, 0.16, 1.0),
    },
    "blue_silicone": {
        "aluminum": (0.72, 0.74, 0.77, 1.0),
        "dark_slot": (0.05, 0.06, 0.09, 1.0),
        "silicone": (0.14, 0.30, 0.72, 1.0),
        "silicone_shadow": (0.08, 0.18, 0.46, 1.0),
        "nylon": (0.86, 0.88, 0.90, 1.0),
        "rubber": (0.02, 0.02, 0.03, 1.0),
        "steel": (0.55, 0.57, 0.62, 1.0),
        "fiber": (0.20, 0.22, 0.30, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SoftPneumaticGripperConfig:
    base_arrangement: BaseArrangement = "crossed_rail_radial"
    finger_form: FingerForm = "corrugated_oval"
    actuation_mechanism: ActuationMechanism = "single_swivel"
    palette_style: PaletteStyle = "cyan_silicone"
    finger_count: int = 4
    finger_radius_scale: float = 1.0
    finger_length_scale: float = 1.0
    swivel_range: float = 0.30
    knuckle_upper: float = 0.50
    span_travel: float = 0.030


@dataclass(frozen=True)
class ResolvedSoftPneumaticGripperConfig:
    base_arrangement: BaseArrangement
    finger_form: FingerForm
    actuation_mechanism: ActuationMechanism
    palette_style: PaletteStyle
    finger_count: int
    finger_radius_scale: float
    finger_length_scale: float
    bend_upper: float
    swivel_range: float
    knuckle_upper: float
    span_travel: float
    palette: dict[str, tuple[float, float, float, float]]


def _n_range_for_base(base: str) -> list[int]:
    """Weighted N domain per base (small N common, large N rare)."""
    if base == "clevis_frame_opposing":
        return [2]
    if base == "wrist_flange_radial":
        return [3, 3, 4, 4, 5, 6]
    if base == "inline_beam":
        return [2, 3, 3, 4, 4, 5]
    # crossed_rail_radial
    return [2, 3, 3, 4, 4, 4, 6]


def _bend_upper_for_n(n: int) -> float:
    """Derived (equation): inward bend upper shrinks with N so radial fingers
    never converge on the centre (self-collision) — Contract 3e clearance."""
    if n <= 3:
        return 0.62
    if n == 4:
        return 0.55
    return 0.46


def config_from_seed(seed: int) -> SoftPneumaticGripperConfig:
    rng = random.Random(seed)
    base = rng.choice(
        ["crossed_rail_radial", "clevis_frame_opposing", "wrist_flange_radial", "inline_beam"]
    )
    form = rng.choice(["corrugated_oval", "ribbed_fin_pneunet", "fiber_cylinder"])
    mechanism = rng.choice(["single_swivel", "multi_segment", "span_carriage"])
    palette = rng.choice(list(PALETTE_STYLES))
    n = rng.choice(_n_range_for_base(base))

    return SoftPneumaticGripperConfig(
        base_arrangement=base,
        finger_form=form,
        actuation_mechanism=mechanism,
        palette_style=palette,
        finger_count=n,
        finger_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        finger_length_scale=round(rng.uniform(0.88, 1.12), 4),
        swivel_range=round(rng.uniform(0.24, 0.34), 4),
        knuckle_upper=round(rng.uniform(0.42, 0.52), 4),
        span_travel=round(rng.uniform(0.024, 0.032), 5),
    )


def resolve_config(config: SoftPneumaticGripperConfig) -> ResolvedSoftPneumaticGripperConfig:
    base = str(config.base_arrangement)
    if base not in {"crossed_rail_radial", "clevis_frame_opposing", "wrist_flange_radial", "inline_beam"}:
        raise ValueError(f"Unsupported base_arrangement: {base}")
    form = str(config.finger_form)
    if form not in {"corrugated_oval", "ribbed_fin_pneunet", "fiber_cylinder"}:
        raise ValueError(f"Unsupported finger_form: {form}")
    mechanism = str(config.actuation_mechanism)
    if mechanism not in {"single_swivel", "multi_segment", "span_carriage"}:
        raise ValueError(f"Unsupported actuation_mechanism: {mechanism}")
    palette_style = str(config.palette_style)
    if palette_style not in _PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_style: {palette_style}")

    # Clamp N into the base's legal domain.
    domain = sorted(set(_n_range_for_base(base)))
    n = int(config.finger_count)
    n = max(domain[0], min(n, domain[-1]))

    # Compatibility gating (Contract 2b analogue): keep clearance-safe combos.
    #  * span_carriage is a 2-jaw span adjuster — only meaningful at N == 2.
    #  * multi_segment adds finger length; restrict to N <= 4 so inward-curling
    #    radial banks stay clear.
    if mechanism == "span_carriage" and n != 2:
        mechanism = "single_swivel"
    if mechanism == "multi_segment" and n > 4:
        mechanism = "single_swivel"
    #  * multi_segment doubles the inward reach; on a dense radial bank (N>=3)
    #    both curled segments converge on the centre and neighbouring fingertips
    #    self-collide. Keep it to 2-jaw (facing) banks and to inline rows whose
    #    fingers curl in clear parallel planes.
    if mechanism == "multi_segment" and base in {"crossed_rail_radial", "wrist_flange_radial"} and n > 2:
        mechanism = "single_swivel"

    rs = max(0.90, min(float(config.finger_radius_scale), 1.12))
    ls = max(0.88, min(float(config.finger_length_scale), 1.12))
    return ResolvedSoftPneumaticGripperConfig(
        base_arrangement=base,  # type: ignore[arg-type]
        finger_form=form,  # type: ignore[arg-type]
        actuation_mechanism=mechanism,  # type: ignore[arg-type]
        palette_style=palette_style,  # type: ignore[arg-type]
        finger_count=n,
        finger_radius_scale=rs,
        finger_length_scale=ls,
        bend_upper=_bend_upper_for_n(n),
        swivel_range=max(0.24, min(float(config.swivel_range), 0.34)),
        knuckle_upper=max(0.42, min(float(config.knuckle_upper), 0.52)),
        span_travel=max(0.024, min(float(config.span_travel), 0.032)),
        palette=dict(_PALETTE_PRESETS[palette_style]),
    )


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #
def _rot_xy(r: float, yaw: float) -> tuple[float, float]:
    return (r * math.cos(yaw), r * math.sin(yaw))


def _circle_profile(radius: float, *, segments: int = 24, center: tuple[float, float] = (0.0, 0.0)):
    cx, cy = center
    return [
        (cx + radius * math.cos(2.0 * math.pi * i / segments),
         cy + radius * math.sin(2.0 * math.pi * i / segments))
        for i in range(segments)
    ]


def _cq_box(size: tuple[float, float, float], center: tuple[float, float, float], *, fillet: float = 0.0):
    shape = cq.Workplane("XY").box(*size).translate(center)
    if fillet > 0.0:
        shape = shape.edges("|Z").fillet(fillet)
    return shape


def _stations(base: str, n: int, radius_scale: float) -> list[dict]:
    """Per-finger station table in the shared world frame."""
    stations: list[dict] = []
    if base == "inline_beam":
        # Fingers reach +y off the bar and curl about the bar axis (yaw=pi/2),
        # so neighbouring fingers move in the y-z plane and never sweep into
        # each other along the x row.
        x0 = -((n - 1) / 2.0) * INLINE_PITCH
        for idx in range(n):
            stations.append({
                "idx": idx, "x": x0 + idx * INLINE_PITCH, "y": 0.0,
                "yaw": math.pi / 2.0, "radial": False,
            })
        return stations
    r = (OPPOSING_R if base == "clevis_frame_opposing" else RADIAL_R * radius_scale)
    for idx in range(n):
        yaw = 2.0 * math.pi * idx / n
        x, y = _rot_xy(r, yaw)
        stations.append({"idx": idx, "x": x, "y": y, "yaw": yaw, "radial": True})
    return stations


def _emit_station_hardware(body, st: dict, *, radial: bool, inner_r: float) -> None:
    """Yoke cheeks + bridge + hinge pin + pneumatic elbow + air tube at one
    station; a radial bridge arm ties the station back to the central stack so
    the manifold stays a single connected solid (Rule / Contract 3)."""
    idx, x, y, yaw = st["idx"], st["x"], st["y"], st["yaw"]
    if radial:
        # Radial support arm from the central block out to the yoke station.
        mid_r = math.hypot(x, y)
        arm_len = mid_r - inner_r
        mx, my = _rot_xy((inner_r + mid_r) / 2.0, yaw)
        body.visual(
            Box((arm_len, 0.018, 0.013)),
            origin=Origin(xyz=(mx, my, SUPPORT_Z - 0.003), rpy=(0.0, 0.0, yaw)),
            material="aluminum", name=f"support_arm_{idx}", material_class_id="metal.aluminum_bare",
        )
    # Fork cheeks straddle the moving actuator block.
    for side in (-1.0, 1.0):
        ly = side * 0.0235
        wx = x + ly * math.cos(yaw + math.pi / 2.0)
        wy = y + ly * math.sin(yaw + math.pi / 2.0)
        body.visual(
            Box((0.026, 0.006, 0.040)),
            origin=Origin(xyz=(wx, wy, 0.123), rpy=(0.0, 0.0, yaw)),
            material="aluminum", name=f"yoke_cheek_{idx}_{0 if side < 0 else 1}", material_class_id="metal.aluminum_bare",
        )
    body.visual(
        Box((0.028, 0.054, 0.006)),
        origin=Origin(xyz=(x, y, SUPPORT_Z), rpy=(0.0, 0.0, yaw)),
        material="aluminum", name=f"yoke_bridge_{idx}", material_class_id="metal.aluminum_bare",
    )
    body.visual(
        Cylinder(radius=0.0042, length=0.055),
        origin=Origin(xyz=(x, y, BEND_Z), rpy=(math.pi / 2.0, 0.0, yaw)),
        material="aluminum", name=f"hinge_pin_{idx}", material_class_id="metal.aluminum_bare",
    )
    fx, fy = _rot_xy(math.hypot(x, y) * 0.82 if radial else 0.0, yaw)
    if not radial:
        fx, fy = x, 0.020
    body.visual(
        Cylinder(radius=0.0065, length=0.020),
        origin=Origin(xyz=(fx, fy, 0.136), rpy=(math.pi / 2.0, 0.0, yaw)),
        material="nylon", name=f"fixed_elbow_{idx}", material_class_id="plastic.opaque_generic",
    )
    # Flexible air tube arcing from the centre toward the station (decoration).
    if radial:
        sx, sy = _rot_xy(0.020, yaw)
        mx2, my2 = _rot_xy(0.060, yaw)
        ex, ey = _rot_xy(max(0.062, math.hypot(x, y) * 0.85), yaw)
    else:
        sx, sy = 0.0, 0.0
        mx2, my2 = x * 0.5, 0.0
        ex, ey = x, 0.0
    tube = tube_from_spline_points(
        [(sx, sy, 0.160), (mx2, my2, 0.166), (ex, ey, 0.146)],
        radius=0.0026, samples_per_segment=10, radial_segments=12, cap_ends=True,
    )
    body.visual(mesh_from_geometry(tube, f"air_tube_{idx}"), material="rubber", name=f"air_tube_{idx}", material_class_id="rubber.smooth_plain")


def _emit_central_stack(body, *, high: bool = False) -> None:
    """Central boss + pneumatic distribution block, shared by every base. For
    the inline bank the finger row runs through the centre, so the block is
    raised clear of the actuators (`high=True`)."""
    if high:
        body.visual(Cylinder(radius=0.024, length=0.050),
                    origin=Origin(xyz=(0.0, 0.0, 0.160)), material="aluminum", name="central_boss", material_class_id="metal.aluminum_bare")
        body.visual(Box((0.050, 0.036, 0.020)),
                    origin=Origin(xyz=(0.0, 0.0, 0.162)), material="aluminum", name="air_manifold_block", material_class_id="metal.aluminum_bare")
    else:
        body.visual(Cylinder(radius=0.024, length=0.044),
                    origin=Origin(xyz=(0.0, 0.0, 0.150)), material="aluminum", name="central_boss", material_class_id="metal.aluminum_bare")
        # Narrow footprint so a close-in opposing / span jaw clears the central
        # distribution block through its full bend + slide envelope.
        body.visual(Box((0.034, 0.044, 0.026)),
                    origin=Origin(xyz=(0.0, 0.0, 0.128)), material="aluminum", name="air_manifold_block", material_class_id="metal.aluminum_bare")


def _body_iface() -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="body", part_name="manifold",
        visual_name="air_manifold_block", face_side="positive_z",
        anchor_local=(0.0, 0.0, 0.0),
    )


# --------------------------------------------------------------------------- #
# base_manifold modules — build grounded `manifold` + publish meta["spg"]
# --------------------------------------------------------------------------- #
def _publish_stations(ctx: ModuleBuildContext, base: str, radial: bool) -> None:
    r: ResolvedSoftPneumaticGripperConfig = ctx.config  # type: ignore[assignment]
    stations = _stations(base, r.finger_count, r.finger_radius_scale)
    for st in stations:
        _emit_station_hardware(ctx.model.get_part("manifold"), st, radial=radial, inner_r=0.024)
    ctx.model.meta["spg"] = {
        "stations": stations,
        "n_fingers": r.finger_count,
        "arrangement": ("radial" if radial else "inline")
        if base != "clevis_frame_opposing" else "opposing",
        "base": base,
    }


def _build_crossed_rail_radial(ctx: ModuleBuildContext) -> ModuleBuild:
    m = ctx.model
    body = m.part("manifold")
    plate_holes = [_circle_profile(0.004)]
    for hx, hy in ((0.024, 0.018), (-0.024, 0.018), (0.024, -0.018), (-0.024, -0.018), (0.0, 0.028), (0.0, -0.028)):
        plate_holes.append(_circle_profile(0.0032, center=(hx, hy)))
    plate = mesh_from_geometry(
        ExtrudeWithHolesGeometry(
            rounded_rect_profile(0.098, 0.074, 0.013, corner_segments=6), plate_holes, 0.008, center=True),
        "perforated_top_plate")
    body.visual(plate, origin=Origin(xyz=(0.0, 0.0, 0.176)), material="aluminum", name="mounting_plate", material_class_id="metal.aluminum_bare")
    _emit_central_stack(body)
    body.visual(Box((0.230, 0.021, 0.008)), origin=Origin(xyz=(0.0, 0.0, 0.144)), material="aluminum", name="rail_x", material_class_id="metal.aluminum_bare")
    body.visual(Box((0.021, 0.230, 0.008)), origin=Origin(xyz=(0.0, 0.0, 0.144)), material="aluminum", name="rail_y", material_class_id="metal.aluminum_bare")
    body.visual(Box((0.205, 0.006, 0.0022)), origin=Origin(xyz=(0.0, 0.0, 0.1491)), material="dark_slot", name="slot_x", material_class_id="metal.blackened_gunmetal")
    body.visual(Box((0.006, 0.205, 0.0022)), origin=Origin(xyz=(0.0, 0.0, 0.1491)), material="dark_slot", name="slot_y", material_class_id="metal.blackened_gunmetal")
    for i, (sx, sy) in enumerate(((0.030, 0.020), (-0.030, 0.020), (0.030, -0.020), (-0.030, -0.020))):
        body.visual(Cylinder(radius=0.004, length=0.012), origin=Origin(xyz=(sx, sy, 0.186)), material="aluminum", name=f"standoff_{i}", material_class_id="metal.aluminum_bare")
        body.visual(Cylinder(radius=0.006, length=0.003), origin=Origin(xyz=(sx, sy, 0.1935)), material="aluminum", name=f"cap_screw_{i}", material_class_id="metal.aluminum_bare")
    _publish_stations(ctx, "crossed_rail_radial", radial=True)
    return ModuleBuild(module_name="crossed_rail_radial", parts_emitted=["manifold"],
                       interfaces={"downstream": _body_iface()})


def _clevis_frame_shape():
    """Single connected machined-aluminum frame (cadquery), lifted into the
    shared coordinate frame (hinge line at BEND_Z). Adapted from S2
    `_metal_manifold_shape` (L30-L52): top plate + standoffs + two actuator
    blocks + clevis cheeks + central manifold body."""
    z0 = 0.176
    shape = _cq_box((0.130, 0.036, 0.010), (0.0, 0.0, z0), fillet=0.003)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            shape = shape.union(_cq_box((0.030, 0.026, 0.010), (sx * 0.048, sy * 0.014, z0), fillet=0.004))
    # Central manifold body + side bridge spanning to each actuator block.
    shape = shape.union(_cq_box((0.040, 0.038, 0.052), (0.0, 0.0, 0.150), fillet=0.003))
    shape = shape.union(_cq_box((0.110, 0.020, 0.018), (0.0, 0.0, 0.150), fillet=0.002))
    for sx in (-1.0, 1.0):
        # Actuator block raised so its underside (z~0.138) sits above the
        # outboard hose-swivel port (top ~0.132) — the close-in 2-jaw connector
        # then clears the frame through its full bend + swivel + slide envelope.
        shape = shape.union(_cq_box((0.048, 0.052, 0.038), (sx * 0.052, 0.0, 0.157), fillet=0.006))
        # Clevis-style cheeks flanking each hinge station.
        for sy in (-1.0, 1.0):
            shape = shape.union(_cq_box((0.028, 0.006, 0.028), (sx * 0.052, sy * 0.026, 0.132), fillet=0.0015))
    return shape


def _build_clevis_frame_opposing(ctx: ModuleBuildContext) -> ModuleBuild:
    m = ctx.model
    body = m.part("manifold")
    body.visual(mesh_from_cadquery(_clevis_frame_shape(), "machined_manifold"),
                material="aluminum", name="machined_manifold", material_class_id="metal.aluminum_bare")
    # Distribution block tucked UP into the frame body (z above the opposing
    # jaws' bend-swing plane, which tops out near BEND_Z=0.130) and narrow, so
    # the close-in 2-jaw actuator roots never clip it. Embedded in the machined
    # central body, so it stays part of the single connected manifold solid.
    body.visual(Cylinder(radius=0.020, length=0.030),
                origin=Origin(xyz=(0.0, 0.0, 0.156)), material="aluminum", name="central_boss", material_class_id="metal.aluminum_bare")
    body.visual(Box((0.030, 0.034, 0.028)),
                origin=Origin(xyz=(0.0, 0.0, 0.156)), material="aluminum", name="air_manifold_block", material_class_id="metal.aluminum_bare")
    # Visible port / fastener detail on the plate (Rule 1: host visuals).
    for idx, (x, y) in enumerate([(-0.048, -0.014), (-0.048, 0.014), (0.048, -0.014), (0.048, 0.014)]):
        body.visual(Cylinder(radius=0.0042, length=0.003), origin=Origin(xyz=(x, y, 0.182)), material="steel", name=f"screw_{idx}", material_class_id="metal.steel_bare")
        body.visual(Cylinder(radius=0.0020, length=0.0034), origin=Origin(xyz=(x, y, 0.1835)), material="dark_slot", name=f"hex_socket_{idx}", material_class_id="metal.blackened_gunmetal")
    for idx, x in enumerate((-0.036, 0.036)):
        body.visual(Cylinder(radius=0.0040, length=0.010), origin=Origin(xyz=(x, 0.009, 0.184)), material="nylon", name=f"barb_fitting_{idx}", material_class_id="plastic.opaque_generic")
    fixed_tube = tube_from_spline_points(
        [(-0.036, 0.009, 0.188), (-0.028, 0.030, 0.168), (0.0, 0.037, 0.150), (0.028, 0.030, 0.168), (0.036, 0.009, 0.188)],
        radius=0.0024, samples_per_segment=12, radial_segments=14, cap_ends=True)
    body.visual(mesh_from_geometry(fixed_tube, "fixed_air_tube"), material="nylon", name="fixed_air_tube", material_class_id="plastic.opaque_generic")
    _publish_stations(ctx, "clevis_frame_opposing", radial=True)
    return ModuleBuild(module_name="clevis_frame_opposing", parts_emitted=["manifold"],
                       interfaces={"downstream": _body_iface()})


def _build_wrist_flange_radial(ctx: ModuleBuildContext) -> ModuleBuild:
    m = ctx.model
    body = m.part("manifold")
    flange_r, flange_t, flange_z, n_bolts, bc_r = 0.055, 0.012, 0.178, 6, 0.038
    holes = [_circle_profile(0.012)]
    for i in range(n_bolts):
        bx, by = _rot_xy(bc_r, 2.0 * math.pi * i / n_bolts)
        holes.append(_circle_profile(0.003, center=(bx, by)))
    flange = mesh_from_geometry(
        ExtrudeWithHolesGeometry(_circle_profile(flange_r), holes, flange_t, center=True), "wrist_flange")
    body.visual(flange, origin=Origin(xyz=(0.0, 0.0, flange_z)), material="aluminum", name="wrist_flange", material_class_id="metal.aluminum_bare")
    for i in range(n_bolts):
        bx, by = _rot_xy(bc_r, 2.0 * math.pi * i / n_bolts)
        body.visual(Cylinder(radius=0.005, length=0.004),
                    origin=Origin(xyz=(bx, by, flange_z + flange_t / 2.0 + 0.002)), material="steel", name=f"flange_bolt_{i}", material_class_id="metal.steel_bare")
    _emit_central_stack(body)
    _publish_stations(ctx, "wrist_flange_radial", radial=True)
    return ModuleBuild(module_name="wrist_flange_radial", parts_emitted=["manifold"],
                       interfaces={"downstream": _body_iface()})


def _build_inline_beam(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedSoftPneumaticGripperConfig = ctx.config  # type: ignore[assignment]
    m = ctx.model
    body = m.part("manifold")
    n = r.finger_count
    span = max(0.16, (n - 1) * INLINE_PITCH + 0.11)
    plate_holes = [_circle_profile(0.004)]
    for hx in (span * 0.42, -span * 0.42, 0.0):
        for hy in (0.022, -0.022):
            plate_holes.append(_circle_profile(0.0032, center=(hx, hy)))
    plate = mesh_from_geometry(
        ExtrudeWithHolesGeometry(rounded_rect_profile(span, 0.060, 0.012, corner_segments=6), plate_holes, 0.008, center=True),
        "perforated_top_plate")
    body.visual(plate, origin=Origin(xyz=(0.0, 0.0, 0.176)), material="aluminum", name="mounting_plate", material_class_id="metal.aluminum_bare")
    _emit_central_stack(body, high=True)
    body.visual(Box((span, 0.024, 0.010)), origin=Origin(xyz=(0.0, 0.0, 0.144)), material="aluminum", name="beam", material_class_id="metal.aluminum_bare")
    body.visual(Box((span - 0.02, 0.006, 0.0022)), origin=Origin(xyz=(0.0, 0.0, 0.1496)), material="dark_slot", name="beam_slot", material_class_id="metal.blackened_gunmetal")
    for i, sx in enumerate((span * 0.42, -span * 0.42)):
        body.visual(Cylinder(radius=0.004, length=0.012), origin=Origin(xyz=(sx, 0.022, 0.186)), material="aluminum", name=f"standoff_{i}", material_class_id="metal.aluminum_bare")
    _publish_stations(ctx, "inline_beam", radial=False)
    return ModuleBuild(module_name="inline_beam", parts_emitted=["manifold"],
                       interfaces={"downstream": _body_iface()})


# --------------------------------------------------------------------------- #
# finger_form geometry — one mesh per form, reused across all N fingers
# --------------------------------------------------------------------------- #
def _corrugated_bellow_geom(ls: float) -> MeshGeometry:
    """Stacked oval corrugated bellows (S1 L38-L64)."""
    geom = MeshGeometry()
    geom.merge(BoxGeometry((0.022, 0.018, 0.082 * ls)).translate(0.020, 0.0, -0.088 * ls))
    z_list = [-0.050, -0.060, -0.071, -0.082, -0.093, -0.104, -0.115, -0.126]
    for i, z in enumerate(z_list):
        radius = 0.0195 if i % 2 == 0 else 0.0175
        fin = CylinderGeometry(radius, 0.0075, radial_segments=28, closed=True)
        fin.scale(1.10, 0.58, 1.0).translate(0.021, 0.0, z * ls)
        geom.merge(fin)
    tip = SphereGeometry(0.017, width_segments=20, height_segments=10)
    tip.scale(1.00, 0.62, 0.70).translate(0.020, 0.0, -0.137 * ls)
    geom.merge(tip)
    return geom


def _fiber_bellow_geom(ls: float) -> MeshGeometry:
    """Smooth tapered fiber-reinforced actuator body (S5 L38-L71)."""
    geom = MeshGeometry()
    z_top, z_bot = -0.048 * ls, -0.128 * ls
    r_top, r_bot = 0.018, 0.013
    n_slices = 12
    span = z_top - z_bot
    slice_h = span / n_slices
    for i in range(n_slices):
        t = (i + 0.5) / n_slices
        rr = r_top + t * (r_bot - r_top)
        z = z_top - (i + 0.5) * slice_h
        sl = CylinderGeometry(rr, slice_h * 1.05, radial_segments=28, closed=True)
        sl.translate(0.020, 0.0, z)
        geom.merge(sl)
    tip = SphereGeometry(0.014, width_segments=20, height_segments=10)
    tip.scale(1.0, 0.80, 0.75).translate(0.020, 0.0, -0.135 * ls)
    geom.merge(tip)
    return geom


def _fiber_wrap_geom(ls: float) -> MeshGeometry:
    """Helical fiber-wrap rib hugging the tapered body radius (S5 L74-L106, Rule 4)."""
    z_top, z_bot = -0.050 * ls, -0.126 * ls
    r_top, r_bot = 0.019, 0.014
    n_turns, pts_per_turn = 2.5, 12
    n_pts = int(n_turns * pts_per_turn) + 1
    points = []
    for i in range(n_pts):
        t = i / (n_pts - 1)
        z = z_top + t * (z_bot - z_top)
        rr = r_top + t * (r_bot - r_top)
        angle = t * n_turns * 2.0 * math.pi
        points.append((0.020 + rr * math.cos(angle), rr * math.sin(angle), z))
    return tube_from_spline_points(points, radius=0.0012, samples_per_segment=8, radial_segments=6, cap_ends=True)


def _ribbed_fin_shape(ls: float):
    """PneuNet external ribbed-fin bellows (S2 L55-L66, cadquery)."""
    shape = _cq_box((0.026, 0.030, 0.012), (0.006, 0.0, -0.006), fillet=0.003)
    shape = shape.union(_cq_box((0.016, 0.027, 0.074 * ls), (0.014, 0.0, -0.046 * ls), fillet=0.004))
    for i in range(5):
        z = (-0.021 - i * 0.0125) * ls
        shape = shape.union(_cq_box((0.031, 0.036, 0.009), (0.024, 0.0, z), fillet=0.0045))
    shape = shape.union(_cq_box((0.020, 0.028, 0.014), (0.021, 0.0, -0.086 * ls), fillet=0.005))
    return shape


def _bellow_mesh(form: str, ls: float):
    if form == "ribbed_fin_pneunet":
        return mesh_from_cadquery(_ribbed_fin_shape(ls), "finger_bellow_ribbed")
    if form == "fiber_cylinder":
        return mesh_from_geometry(_fiber_bellow_geom(ls), "finger_bellow_fiber")
    return mesh_from_geometry(_corrugated_bellow_geom(ls), "finger_bellow_corrugated")


def _finger_bottom_z(form: str, ls: float) -> float:
    """Local z of the proximal bellow's distal end per form family. The ribbed
    PneuNet body is shorter than the corrugated / fiber columns, so the serial
    knuckle joint (and thus the distal tip) must attach higher for it to stay in
    contact with the proximal finger (no isolated tip part)."""
    if form == "ribbed_fin_pneunet":
        # Attach into the proximal body (not at its exact tip) so the tip nests
        # and stays in contact across the whole finger_length_scale range.
        return -0.083 * ls
    return -0.126 * ls


def _tip_geom(form: str, ls: float) -> MeshGeometry:
    """Short distal continuation segment authored in tip-local frame (top at
    z=0, extends -z), matching the form family (S5m L70-L82). Element z-spans
    overlap head-to-tail so the tip mesh is one connected solid (no islands)."""
    geom = MeshGeometry()
    geom.merge(BoxGeometry((0.018, 0.026, 0.012)).translate(0.020, 0.0, -0.006))
    if form == "ribbed_fin_pneunet":
        for i in range(2):
            fin = BoxGeometry((0.030, 0.034, 0.012)).translate(0.024, 0.0, -0.013 - i * 0.011)
            geom.merge(fin)
    else:
        for i in range(2):
            fin = CylinderGeometry(0.017, 0.012, radial_segments=24, closed=True)
            fin.scale(1.05, 0.62, 1.0).translate(0.020, 0.0, -0.014 - i * 0.011)
            geom.merge(fin)
    tip = SphereGeometry(0.014, width_segments=18, height_segments=9)
    tip.scale(1.0, 0.66, 0.72).translate(0.020, 0.0, -0.036)
    geom.merge(tip)
    return geom


def _build_finger_form(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedSoftPneumaticGripperConfig = ctx.config  # type: ignore[assignment]
    m = ctx.model
    form = r.finger_form
    ls = r.finger_length_scale
    spg = m.meta["spg"]
    n = spg["n_fingers"]

    bellow = _bellow_mesh(form, ls)
    fiber = _fiber_wrap_geom(ls) if form == "fiber_cylinder" else None
    multi = r.actuation_mechanism == "multi_segment"
    tip_geom = _tip_geom(form, ls) if multi else None

    finger_parts: list[str] = []
    tip_parts: list[str] = []
    for idx in range(n):
        finger = m.part(f"finger_{idx}")
        finger.visual(Box((0.030, 0.034, 0.034)), origin=Origin(xyz=(0.012, 0.0, -0.017)),
                      material="aluminum", name="actuator_base", material_class_id="metal.aluminum_bare")
        # Long enough to always bridge the actuator block down to the bellow's
        # top chamber, even when a high finger_length_scale drops a tapered
        # fiber / corrugated bellow's top slice (no disconnected finger island).
        finger.visual(Box((0.019, 0.021, 0.034)), origin=Origin(xyz=(0.018, 0.0, -0.046)),
                      material="silicone", name="soft_neck", material_class_id="rubber.smooth_plain")
        finger.visual(bellow, origin=Origin(), material="silicone", name="bellow", material_class_id="rubber.smooth_plain")
        if fiber is not None:
            finger.visual(mesh_from_geometry(fiber, f"fiber_wrap_{idx}"), origin=Origin(), material="fiber", name="fiber_wrap", material_class_id="fabric.thread_yarn")
        elif form == "corrugated_oval":
            # Darker grip-valley insets seated into the corrugated bellow face
            # (Rule 4, host-derived — x=0.006 keeps them embedded in the oval
            # chamber wall so they never float). The ribbed PneuNet form already
            # carries its own external-fin surface texture, so it adds none.
            for j, z in enumerate((-0.058 * ls, -0.080 * ls, -0.102 * ls, -0.124 * ls)):
                finger.visual(Box((0.006, 0.016, 0.003)), origin=Origin(xyz=(0.006, 0.0, z)),
                              material="silicone_shadow", name=f"grip_valley_{j}", material_class_id="rubber.smooth_plain")
        finger_parts.append(f"finger_{idx}")
        if tip_geom is not None:
            tip = m.part(f"finger_{idx}_tip")
            tip.visual(mesh_from_geometry(tip_geom, f"finger_tip_mesh_{idx}"), origin=Origin(), material="silicone", name="bellow", material_class_id="rubber.smooth_plain")
            tip_parts.append(f"finger_{idx}_tip")

    m.meta["spg_fingers"] = {"fingers": finger_parts, "tips": tip_parts}
    return ModuleBuild(module_name=form, parts_emitted=finger_parts + tip_parts,
                       interfaces={"downstream": ctx.upstream_interface})


# --------------------------------------------------------------------------- #
# actuation_mechanism modules — every articulation + mechanism-specific parts
# --------------------------------------------------------------------------- #
def _emit_swivel_connector(m, idx: int, r) -> str:
    # Compact barbed hose port seated on the outboard face of the actuator block
    # and pointing straight outboard (+x), in the clear band above every bellow
    # form's top chamber. It swivels about the VERTICAL axis, so the barb pans
    # sideways (horizontally) through that clear band instead of tilting down
    # into the ribbed fins or up into the manifold hinge hardware.
    connector = m.part(f"hose_connector_{idx}")
    connector.visual(Cylinder(radius=0.0055, length=0.005),
                     origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                     material="nylon", name="port_collar", material_class_id="plastic.opaque_generic")
    connector.visual(Cylinder(radius=0.0042, length=0.014),
                     origin=Origin(xyz=(0.007, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                     material="nylon", name="barbed_port", material_class_id="plastic.opaque_generic")
    # Flexible stub trailing outboard and sideways, staying in the clear band;
    # its inboard end overlaps the barb so the connector is one connected solid.
    stub = tube_from_spline_points(
        [(0.012, 0.0, 0.0), (0.020, 0.006, 0.001), (0.027, 0.011, 0.002)],
        radius=0.0022, samples_per_segment=8, radial_segments=10, cap_ends=True)
    connector.visual(mesh_from_geometry(stub, f"hose_stub_{idx}"), material="rubber", name="hose_stub", material_class_id="rubber.smooth_plain")
    m.articulation(
        f"finger_to_connector_{idx}", ArticulationType.REVOLUTE,
        parent=m.get_part(f"finger_{idx}"), child=connector,
        origin=Origin(xyz=(0.028, 0.0, -0.004)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.35, velocity=1.2, lower=-r.swivel_range, upper=r.swivel_range),
    )
    return f"hose_connector_{idx}"


def _carriage_shape():
    """Sliding span carriage with dovetail tongue + clevis cheeks (S6 L69-L80)."""
    shape = _cq_box((0.044, 0.048, 0.012), (0.0, 0.0, 0.0), fillet=0.003)
    shape = shape.union(_cq_box((0.030, 0.018, 0.006), (0.0, 0.0, 0.008), fillet=0.001))
    shape = shape.union(_cq_box((0.026, 0.030, 0.004), (0.0, 0.0, -0.008), fillet=0.002))
    for sy in (-1.0, 1.0):
        shape = shape.union(_cq_box((0.028, 0.005, 0.016), (0.0, sy * 0.026, -0.004), fillet=0.001))
    return shape


def _build_actuation(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedSoftPneumaticGripperConfig = ctx.config  # type: ignore[assignment]
    m = ctx.model
    mech = r.actuation_mechanism
    spg = m.meta["spg"]
    stations = spg["stations"]
    manifold = m.get_part("manifold")
    parts: list[str] = []
    joints: list[str] = []

    bend_limits = MotionLimits(effort=6.0, velocity=1.6, lower=0.0, upper=r.bend_upper)

    if mech == "span_carriage":
        carriage_mesh = mesh_from_cadquery(_carriage_shape(), "span_carriage_body")
        for st in stations:
            idx, x, y, yaw = st["idx"], st["x"], st["y"], st["yaw"]
            carriage = m.part(f"finger_carriage_{idx}")
            carriage.visual(carriage_mesh, origin=Origin(), material="aluminum", name="carriage_body", material_class_id="metal.aluminum_bare")
            # PRISMATIC span slide along the outward (radial) direction.
            axis = (math.cos(yaw), math.sin(yaw), 0.0)
            m.articulation(
                f"manifold_to_carriage_{idx}", ArticulationType.PRISMATIC,
                parent=manifold, child=carriage,
                origin=Origin(xyz=(x, y, BEND_Z - 0.006), rpy=(0.0, 0.0, yaw)),
                axis=axis,
                motion_limits=MotionLimits(effort=12.0, velocity=0.05, lower=0.0, upper=r.span_travel),
            )
            # Finger bend re-parented onto the carriage.
            m.articulation(
                f"manifold_to_finger_{idx}", ArticulationType.REVOLUTE,
                parent=carriage, child=m.get_part(f"finger_{idx}"),
                origin=Origin(xyz=(0.0, 0.0, 0.006)), axis=(0.0, 1.0, 0.0),
                motion_limits=bend_limits,
            )
            parts.append(f"finger_carriage_{idx}")
            joints.extend([f"manifold_to_carriage_{idx}", f"manifold_to_finger_{idx}"])
            parts.append(_emit_swivel_connector(m, idx, r))
        m.meta["spg_mech"] = {"kind": "span_carriage", "carriages": [f"finger_carriage_{i['idx']}" for i in stations]}
        return ModuleBuild(module_name="span_carriage", parts_emitted=parts,
                           internal_articulations=joints, interfaces={"downstream": ctx.upstream_interface})

    # single_swivel and multi_segment: bend joint parented directly to manifold.
    for st in stations:
        idx, x, y, yaw = st["idx"], st["x"], st["y"], st["yaw"]
        m.articulation(
            f"manifold_to_finger_{idx}", ArticulationType.REVOLUTE,
            parent=manifold, child=m.get_part(f"finger_{idx}"),
            origin=Origin(xyz=(x, y, BEND_Z), rpy=(0.0, 0.0, yaw)), axis=(0.0, 1.0, 0.0),
            motion_limits=bend_limits,
        )
        joints.append(f"manifold_to_finger_{idx}")
        if mech == "multi_segment":
            # Serial knuckle: proximal finger -> distal tip (progressive curl).
            m.articulation(
                f"finger_{idx}_knuckle", ArticulationType.REVOLUTE,
                parent=m.get_part(f"finger_{idx}"), child=m.get_part(f"finger_{idx}_tip"),
                origin=Origin(xyz=(0.0, 0.0, _finger_bottom_z(r.finger_form, r.finger_length_scale))),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=5.0, velocity=1.5, lower=0.0, upper=r.knuckle_upper),
            )
            joints.append(f"finger_{idx}_knuckle")
        parts.append(_emit_swivel_connector(m, idx, r))
    m.meta["spg_mech"] = {"kind": mech}
    return ModuleBuild(module_name=mech, parts_emitted=parts,
                       internal_articulations=joints, interfaces={"downstream": ctx.upstream_interface})


# --------------------------------------------------------------------------- #
# Slot wiring
# --------------------------------------------------------------------------- #
_BASES = {
    "crossed_rail_radial": _build_crossed_rail_radial,
    "clevis_frame_opposing": _build_clevis_frame_opposing,
    "wrist_flange_radial": _build_wrist_flange_radial,
    "inline_beam": _build_inline_beam,
}
_FORMS = {
    "corrugated_oval": _build_finger_form,
    "ribbed_fin_pneunet": _build_finger_form,
    "fiber_cylinder": _build_finger_form,
}
_MECHS = {
    "single_swivel": _build_actuation,
    "multi_segment": _build_actuation,
    "span_carriage": _build_actuation,
}


def _slots(r: ResolvedSoftPneumaticGripperConfig) -> list[SlotSpec]:
    return [
        SlotSpec("base_manifold", _BASES, anchor_choice=r.base_arrangement),
        SlotSpec("finger_form", _FORMS, anchor_choice=r.finger_form),
        SlotSpec("actuation_mechanism", _MECHS, anchor_choice=r.actuation_mechanism),
    ]


def _mult_band(n: int) -> str:
    return f"n{n}"


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("base_manifold", r.base_arrangement),
        ("finger_form", r.finger_form),
        ("actuation_mechanism", r.actuation_mechanism),
        ("finger_count", _mult_band(r.finger_count)),
        ("palette_style", r.palette_style),
    ]


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_soft_pneumatic_gripper(
    config: SoftPneumaticGripperConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="soft_pneumatic_gripper", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)
    assemble(
        model,
        slots=_slots(r),
        rng=random.Random(0),
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_soft_pneumatic_gripper(seed: int) -> ArticulatedObject:
    return build_soft_pneumatic_gripper(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def _maybe_part(model: ArticulatedObject, name: str):
    return model.get_part(name) if name in {p.name for p in model.parts} else None


def _maybe_joint(model: ArticulatedObject, name: str):
    return model.get_articulation(name) if name in {a.name for a in model.articulations} else None


def _apply_captured_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    manifold = model.get_part("manifold")
    spg = model.meta.get("spg", {})
    base = spg.get("base")
    arrangement = spg.get("arrangement", "radial")
    # Per-station captured-interface allowances. Every station's finger rotates
    # about a metal pivot pin that necessarily runs through its own body, and
    # (span) rides a carriage / (multi) carries a distal tip — all applied per
    # idx inside the station loop so they cover EVERY finger, not just the last.
    for st in spg.get("stations", []):
        idx = st["idx"]
        finger = _maybe_part(model, f"finger_{idx}")
        if finger is None:
            continue
        # The pivot pin and yoke bridge pass through the finger root it hinges
        # about — captured, not a clearance defect. The pin also sweeps into the
        # top bellow chamber as the finger curls (it lies on the bend axis).
        ctx.allow_overlap(manifold, finger, elem_a=f"hinge_pin_{idx}", elem_b="actuator_base",
                          reason="Metal hinge pin is captured through the actuator block bore.")
        ctx.allow_overlap(manifold, finger, elem_a=f"hinge_pin_{idx}", elem_b="bellow",
                          reason="Pivot pin lies on the bend axis and stays embedded in the finger body as it curls.")
        ctx.allow_overlap(manifold, finger, elem_a=f"yoke_bridge_{idx}", elem_b="actuator_base",
                          reason="Actuator block nests just under the yoke bridge at the hinge.")
        if base == "clevis_frame_opposing":
            ctx.allow_overlap(manifold, finger, elem_a="machined_manifold", elem_b="actuator_base",
                              reason="Actuator block is captured inside the machined clevis frame cheeks.")
            ctx.allow_overlap(manifold, finger, elem_a="machined_manifold", elem_b="bellow",
                              reason="Soft actuator root is captured between the machined clevis cheeks at the hinge line.")
        connector = _maybe_part(model, f"hose_connector_{idx}")
        if connector is not None:
            # The whole swivel fitting seats on and pivots against the outboard
            # face of the finger's own actuator block (its only contact with the
            # finger — it rides in the clear band well above the bellow), so the
            # collar/barb brushing that block is a designed mount contact.
            ctx.allow_overlap(finger, connector,
                              reason="Hose swivel fitting seats on and pivots against the finger's actuator block.")
            ctx.allow_overlap(manifold, connector, elem_a=f"hinge_pin_{idx}", elem_b="port_collar",
                              reason="Swivel port is mounted at the finger's hinge station and brushes that station's pivot pin as the finger slides/bends.")
        tip = _maybe_part(model, f"finger_{idx}_tip")
        if tip is not None:
            ctx.allow_overlap(finger, tip, elem_a="bellow", elem_b="bellow",
                              reason="Distal tip stub nests on the proximal bellow at the knuckle joint.")
        carriage = _maybe_part(model, f"finger_carriage_{idx}")
        if carriage is not None:
            ctx.allow_overlap(manifold, carriage,
                              reason="Carriage dovetail tongue engages the manifold rail groove for the prismatic slide.")
            ctx.allow_overlap(carriage, finger, elem_a="carriage_body", elem_b="actuator_base",
                              reason="Finger root is captured by the carriage clevis cheeks.")
            ctx.allow_overlap(carriage, finger, elem_a="carriage_body", elem_b="bellow",
                              reason="Soft actuator root nests into the carriage clevis cheeks at the hinge.")
    # Two facing soft jaws (opposing clevis / radial N==2) are DESIGNED to
    # converge at full closure (the grasp) — the origin record declares this as
    # expect_overlap. Allow the full jaw pair (bellow / fiber_wrap / tip all
    # deform together). Inline N==2 fingers curl in parallel planes and never
    # face each other, so they are excluded and keep normal clearance.
    if spg.get("n_fingers") == 2 and arrangement != "inline":
        f0 = _maybe_part(model, "finger_0")
        f1 = _maybe_part(model, "finger_1")
        if f0 is not None and f1 is not None:
            ctx.allow_overlap(f0, f1,
                              reason="Opposing soft jaws deform together and meet when the gripper closes on an object.")
            t0 = _maybe_part(model, "finger_0_tip")
            t1 = _maybe_part(model, "finger_1_tip")
            if t0 is not None and t1 is not None:
                ctx.allow_overlap(t0, t1,
                                  reason="Opposing multi-segment tips meet at full closure.")
                ctx.allow_overlap(f0, t1,
                                  reason="Opposing jaw and neighbour tip meet at full closure.")
                ctx.allow_overlap(f1, t0,
                                  reason="Opposing jaw and neighbour tip meet at full closure.")


def run_soft_pneumatic_gripper_tests(
    model: ArticulatedObject, config: SoftPneumaticGripperConfig
) -> TestReport:
    ctx = TestContext(model)
    _apply_captured_overlaps(ctx, model)

    spg = model.meta.get("spg", {})
    n = spg.get("n_fingers", 0)
    arrangement = spg.get("arrangement", "radial")

    # Identity.
    ctx.check("manifold root exists", model.get_part("manifold") is not None)
    ctx.check(
        f"{n} soft bellows fingers exist",
        n >= 2 and all(model.get_part(f"finger_{i}") is not None for i in range(n)),
        details=f"n={n}",
    )
    for i in range(n):
        finger = model.get_part(f"finger_{i}")
        bend = model.get_articulation(f"manifold_to_finger_{i}")
        ctx.check(f"finger_{i} has a bellow visual", finger is not None and finger.get_visual("bellow") is not None)
        ctx.check(
            f"finger_{i} has a real non-fixed inward bend joint",
            bend is not None and bend.articulation_type == ArticulationType.REVOLUTE,
        )

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # Targeted mechanism semantics.
    def _center(part, elem="bellow"):
        aabb = ctx.part_element_world_aabb(part, elem=elem)
        if aabb is None:
            return None
        lo, hi = aabb
        return ((lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, (lo[2] + hi[2]) / 2.0)

    if n > 0:
        finger0 = model.get_part("finger_0")
        bend0 = model.get_articulation("manifold_to_finger_0")
        rest = _center(finger0)
        with ctx.pose({bend0: bend0.motion_limits.upper}):
            bent = _center(finger0)
        if rest is not None and bent is not None:
            if arrangement == "inline":
                ctx.check("finger_0 curls down/forward under pressure",
                          bent[2] < rest[2] - 0.010 or abs(bent[1] - rest[1]) > 0.015,
                          details=f"rest={rest}, bent={bent}")
            else:
                rr = math.hypot(rest[0], rest[1])
                br = math.hypot(bent[0], bent[1])
                ctx.check("finger_0 closes inward under pressure", br < rr - 0.010,
                          details=f"rest_r={rr:.4f}, bent_r={br:.4f}")

        conn = _maybe_part(model, "hose_connector_0")
        cj = _maybe_joint(model, "finger_to_connector_0")
        if conn is not None and cj is not None:
            rc = ctx.part_world_aabb(conn)
            with ctx.pose({cj: cj.motion_limits.upper}):
                sc = ctx.part_world_aabb(conn)
            if rc is not None and sc is not None:
                # Vertical-axis swivel pans the barb horizontally, so measure the
                # full 3D centroid shift (not just z) for the visible travel.
                shift = math.sqrt(
                    ((sc[0][0] + sc[1][0]) - (rc[0][0] + rc[1][0])) ** 2
                    + ((sc[0][1] + sc[1][1]) - (rc[0][1] + rc[1][1])) ** 2
                    + ((sc[0][2] + sc[1][2]) - (rc[0][2] + rc[1][2])) ** 2
                ) / 2.0
                ctx.check("hose connector 0 has visible swivel travel", shift > 0.0008,
                          details=f"rest={rc}, swivel={sc}, shift={shift:.5f}")

    mech = model.meta.get("spg_mech", {}).get("kind")
    if mech == "multi_segment":
        tip = _maybe_part(model, "finger_0_tip")
        knuckle = _maybe_joint(model, "finger_0_knuckle")
        if tip is not None and knuckle is not None:
            rt = _center(tip)
            with ctx.pose({knuckle: knuckle.motion_limits.upper}):
                ct = _center(tip)
            if rt is not None and ct is not None:
                moved = (abs(ct[0] - rt[0]) + abs(ct[2] - rt[2])) > 0.006
                ctx.check("multi-segment knuckle curls distal tip", moved, details=f"rest={rt}, curled={ct}")
    if mech == "span_carriage":
        c0 = _maybe_part(model, "finger_carriage_0")
        s0 = _maybe_joint(model, "manifold_to_carriage_0")
        if c0 is not None and s0 is not None:
            r0 = ctx.part_world_position(c0)
            with ctx.pose({s0: s0.motion_limits.upper}):
                w0 = ctx.part_world_position(c0)
            if r0 is not None and w0 is not None:
                ctx.check("span carriage 0 slides outward", math.hypot(w0[0] - r0[0], w0[1] - r0[1]) > 0.015,
                          details=f"rest={r0}, wide={w0}")

    # Full-travel non-penetration across every movable joint (Rule 5).
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)
    return ctx.report()


__all__ = [
    "SoftPneumaticGripperConfig",
    "ResolvedSoftPneumaticGripperConfig",
    "config_from_seed",
    "resolve_config",
    "build_soft_pneumatic_gripper",
    "build_seeded_soft_pneumatic_gripper",
    "slot_choices_for_seed",
    "run_soft_pneumatic_gripper_tests",
]
