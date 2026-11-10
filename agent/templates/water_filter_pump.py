# SPDX-License-Identifier: Apache-2.0

"""Water filter pump — modular procedural template.

A handheld, hand-powered water filter pump: a filter body/cartridge that source
water is forced through by a reciprocating / driven hand actuator with a real
non-fixed joint (piston plunger, pivoting lever, rotary crank, or squeeze bulb),
plus intake / outlet hose interfaces and a base (flat pad or folding tripod).

Structure is parallel-children off a root ``pump_body`` chassis (spec
``specs_modular_v1/water_filter_pump.md``). ``body_form`` builds ``pump_body``
and publishes ``model.meta["wfp"]`` mount/socket/base geometry; ``pump_actuation``,
``hose_ports`` and ``support_base`` each read that meta, emit their own parts +
joints parented to ``pump_body``, declare NO ``upstream`` interface (so the
assembler emits no auto chain joint) and re-export the body interface. Every
joint is authored directly with the correct type / mating / grandfather, exactly
as the 5-star source records do.

Sources (data/records/<id>/revisions/rev_000001/model.py):
  origin1 = rec_a-handheld-...72ff3145           (twin barrels + paddle piston + ribs)
  origin2 = rec_...1c2f03adc4a5434c99f27df29d239b97 (single cylinder + T-handle + ports)
  origin3 = rec_...4b72f2e9740148e2b07ac2a2dfaa6a66 (parallel filter+sleeve + bridges)
  var_lever_pump / var_rotary_crank / var_squeeze_bulb / var_tripod_stand /
  var_inline_coaxial / var_bottle_top / var_ring_pull_handle / var_inline_prefilter /
  var_grip_ribs_{dense,sparse} / var_bridge_webs_multi / probe_lever_twin_barrel
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
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
    CapsuleGeometry,
    Cylinder,
    CylinderGeometry,
    KnobGeometry,
    KnobGrip,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

BodyForm = Literal[
    "twin_barrel", "single_cylinder", "parallel_sleeve", "inline_coaxial", "bottle_top"
]
PumpActuation = Literal[
    "piston_paddle", "piston_thandle", "lever_pump", "rotary_crank", "squeeze_bulb"
]
HosePorts = Literal["fixed_hoses", "detachable_ports", "single_outlet", "fixed_hoses_prefilter"]
SupportBase = Literal["flat_base", "tripod_stand"]
HandleGripForm = Literal["tbar", "thandle", "ring_pull"]
PaletteStyle = Literal[
    "olive_classic", "dark_olive", "desert_tan", "graphite_grey", "blue_accent"
]

# --------------------------------------------------------------------------- #
# Palette presets — ⑥ colorway; every .visual(material=...) reads a mats name.
# rgba tuples; alpha < 1 only for the clear hose. (See cushion.py pattern.)
# --------------------------------------------------------------------------- #
PALETTE_STYLES: tuple[str, ...] = (
    "olive_classic",
    "dark_olive",
    "desert_tan",
    "graphite_grey",
    "blue_accent",
)

_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "olive_classic": {
        "body_main": (0.22, 0.38, 0.17, 1.0),
        "body_dark": (0.10, 0.20, 0.08, 1.0),
        "body_light": (0.34, 0.52, 0.25, 1.0),
        "grip_rubber": (0.05, 0.05, 0.05, 1.0),
        "metal_rod": (0.78, 0.82, 0.78, 1.0),
        "hose_clear": (0.86, 0.93, 1.0, 0.42),
        "fitting_grey": (0.30, 0.32, 0.30, 1.0),
        "accent": (0.10, 0.32, 0.86, 1.0),
    },
    "dark_olive": {
        "body_main": (0.15, 0.24, 0.10, 1.0),
        "body_dark": (0.07, 0.13, 0.05, 1.0),
        "body_light": (0.24, 0.36, 0.18, 1.0),
        "grip_rubber": (0.03, 0.03, 0.03, 1.0),
        "metal_rod": (0.70, 0.73, 0.72, 1.0),
        "hose_clear": (0.83, 0.90, 0.96, 0.42),
        "fitting_grey": (0.24, 0.26, 0.24, 1.0),
        "accent": (0.16, 0.38, 0.72, 1.0),
    },
    "desert_tan": {
        "body_main": (0.72, 0.62, 0.42, 1.0),
        "body_dark": (0.45, 0.38, 0.25, 1.0),
        "body_light": (0.82, 0.73, 0.55, 1.0),
        "grip_rubber": (0.12, 0.10, 0.08, 1.0),
        "metal_rod": (0.80, 0.82, 0.80, 1.0),
        "hose_clear": (0.90, 0.90, 0.86, 0.42),
        "fitting_grey": (0.35, 0.33, 0.30, 1.0),
        "accent": (0.55, 0.32, 0.14, 1.0),
    },
    "graphite_grey": {
        "body_main": (0.30, 0.31, 0.33, 1.0),
        "body_dark": (0.15, 0.16, 0.17, 1.0),
        "body_light": (0.45, 0.46, 0.48, 1.0),
        "grip_rubber": (0.05, 0.05, 0.06, 1.0),
        "metal_rod": (0.82, 0.84, 0.86, 1.0),
        "hose_clear": (0.88, 0.92, 1.0, 0.40),
        "fitting_grey": (0.20, 0.21, 0.22, 1.0),
        "accent": (0.90, 0.45, 0.10, 1.0),
    },
    "blue_accent": {
        "body_main": (0.16, 0.34, 0.52, 1.0),
        "body_dark": (0.08, 0.18, 0.30, 1.0),
        "body_light": (0.30, 0.50, 0.68, 1.0),
        "grip_rubber": (0.05, 0.05, 0.06, 1.0),
        "metal_rod": (0.80, 0.83, 0.85, 1.0),
        "hose_clear": (0.86, 0.93, 1.0, 0.42),
        "fitting_grey": (0.28, 0.30, 0.32, 1.0),
        "accent": (0.95, 0.75, 0.10, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class WaterFilterPumpConfig:
    body_form: BodyForm = "twin_barrel"
    pump_actuation: PumpActuation = "piston_paddle"
    hose_ports: HosePorts = "fixed_hoses"
    support_base: SupportBase = "flat_base"
    handle_grip_form: HandleGripForm = "tbar"
    palette_style: PaletteStyle = "olive_classic"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    stroke_scale: float = 1.0
    rib_count: int = 5
    web_count: int = 2
    scallop_count: int = 5
    leg_count: int = 3


@dataclass(frozen=True)
class ResolvedWaterFilterPumpConfig:
    body_form: BodyForm
    pump_actuation: PumpActuation
    hose_ports: HosePorts
    support_base: SupportBase
    handle_grip_form: HandleGripForm
    palette_style: PaletteStyle
    body_height_scale: float
    body_radius_scale: float
    stroke_scale: float
    rib_count: int
    web_count: int
    scallop_count: int
    leg_count: int
    palette: dict[str, tuple[float, float, float, float]]


def _resolve_choices(config: WaterFilterPumpConfig) -> tuple[str, str, str, str, str]:
    """Apply the compatibility gate: lever_pump on parallel_sleeve is excluded
    (swing clearance vs. the offset pump-sleeve column) -> demote to a
    T-handle piston. lever x twin_barrel is allowed (probe_lever_twin_barrel)."""
    body_form = str(config.body_form)
    actuation = str(config.pump_actuation)
    hose = str(config.hose_ports)
    base = str(config.support_base)
    grip = str(config.handle_grip_form)

    if body_form not in {"twin_barrel", "single_cylinder", "parallel_sleeve",
                          "inline_coaxial", "bottle_top"}:
        raise ValueError(f"Unsupported body_form: {body_form}")
    if actuation not in {"piston_paddle", "piston_thandle", "lever_pump",
                         "rotary_crank", "squeeze_bulb"}:
        raise ValueError(f"Unsupported pump_actuation: {actuation}")
    if hose not in {"fixed_hoses", "detachable_ports", "single_outlet",
                    "fixed_hoses_prefilter"}:
        raise ValueError(f"Unsupported hose_ports: {hose}")
    if base not in {"flat_base", "tripod_stand"}:
        raise ValueError(f"Unsupported support_base: {base}")

    # The parallel_sleeve's short offset pump sleeve sits beside a tall filter
    # cartridge, so a top-mounted lever/crank/bulb has no swing/sweep/seat
    # clearance (the cartridge cap is at actuator height). Restrict it to a
    # straight piston plunger down the sleeve (origin3's own mechanism).
    if actuation in {"lever_pump", "rotary_crank", "squeeze_bulb"} and body_form == "parallel_sleeve":
        actuation = "piston_thandle"
    # Detachable ports only exist on the forms with origin2 manifold sockets.
    if hose == "detachable_ports" and body_form not in {"single_cylinder", "bottle_top"}:
        hose = "fixed_hoses"
    # Grip form only meaningful for piston actuators.
    if actuation not in {"piston_paddle", "piston_thandle"}:
        grip = "tbar"
    return body_form, actuation, hose, base, grip


def config_from_seed(seed: int) -> WaterFilterPumpConfig:
    rng = random.Random(seed)
    body_form = rng.choice(
        ["twin_barrel", "single_cylinder", "parallel_sleeve", "inline_coaxial", "bottle_top"]
    )
    actuation = rng.choice(
        ["piston_paddle", "piston_thandle", "lever_pump", "rotary_crank", "squeeze_bulb"]
    )
    hose = rng.choice(
        ["fixed_hoses", "detachable_ports", "single_outlet", "fixed_hoses_prefilter"]
    )
    base = rng.choice(["flat_base", "tripod_stand"])
    grip = rng.choice(["tbar", "thandle", "ring_pull"])
    palette = rng.choice(list(PALETTE_STYLES))

    # Weighted small-N multiplicity (small counts common, tails rare).
    rib_count = rng.choice([3, 4, 5, 5, 6, 6, 7, 8, 10, 12])
    web_count = rng.choice([2, 2, 3, 3, 4, 5])
    scallop_count = rng.choice([3, 4, 5, 5, 6])
    leg_count = rng.choice([3, 3, 3, 4])

    return WaterFilterPumpConfig(
        body_form=body_form,
        pump_actuation=actuation,
        hose_ports=hose,
        support_base=base,
        handle_grip_form=grip,
        palette_style=palette,
        body_height_scale=round(rng.uniform(0.85, 1.20), 4),
        body_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        stroke_scale=round(rng.uniform(0.85, 1.15), 4),
        rib_count=rib_count,
        web_count=web_count,
        scallop_count=scallop_count,
        leg_count=leg_count,
    )


def resolve_config(config: WaterFilterPumpConfig) -> ResolvedWaterFilterPumpConfig:
    body_form, actuation, hose, base, grip = _resolve_choices(config)
    palette_style = str(config.palette_style)
    if palette_style not in _PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_style: {palette_style}")

    hs = max(0.85, min(float(config.body_height_scale), 1.20))
    rs = max(0.90, min(float(config.body_radius_scale), 1.12))
    ss = max(0.85, min(float(config.stroke_scale), 1.15))
    return ResolvedWaterFilterPumpConfig(
        body_form=body_form,  # type: ignore[arg-type]
        pump_actuation=actuation,  # type: ignore[arg-type]
        hose_ports=hose,  # type: ignore[arg-type]
        support_base=base,  # type: ignore[arg-type]
        handle_grip_form=grip,  # type: ignore[arg-type]
        palette_style=palette_style,  # type: ignore[arg-type]
        body_height_scale=hs,
        body_radius_scale=rs,
        stroke_scale=ss,
        rib_count=max(3, min(int(config.rib_count), 12)),
        web_count=max(2, min(int(config.web_count), 5)),
        scallop_count=max(3, min(int(config.scallop_count), 6)),
        leg_count=max(3, min(int(config.leg_count), 4)),
        palette=dict(_PALETTE_PRESETS[palette_style]),
    )


# --------------------------------------------------------------------------- #
# Mesh helpers (kept Mesh-typed per AUTHORING Rule 3)
# --------------------------------------------------------------------------- #
_ROT_Y90 = (0.0, math.pi / 2.0, 0.0)  # local +z -> world +x


def _knob_cap(diameter: float, height: float, *, count: int, depth: float, name: str) -> object:
    return mesh_from_geometry(
        KnobGeometry(
            diameter,
            height,
            body_style="cylindrical",
            grip=KnobGrip(style="ribbed", count=count, depth=depth, width=0.0018),
            edge_radius=0.001,
        ),
        name,
    )


def _curved_grip_panel(
    *, inner_radius: float, outer_radius: float, z_min: float, z_max: float,
    angle_min: float, angle_max: float, segments: int = 16,
) -> MeshGeometry:
    """Shallow raised curved pad on a cylindrical body (origin2 L30-75).
    Built around the body's actual radius so it hugs the surface (Rule 4)."""
    geom = MeshGeometry()
    ib: list[int] = []
    ob: list[int] = []
    it: list[int] = []
    ot: list[int] = []
    for i in range(segments + 1):
        t = angle_min + (angle_max - angle_min) * i / segments
        s, c = math.sin(t), math.cos(t)
        ib.append(geom.add_vertex(inner_radius * s, inner_radius * c, z_min))
        it.append(geom.add_vertex(inner_radius * s, inner_radius * c, z_max))
        ob.append(geom.add_vertex(outer_radius * s, outer_radius * c, z_min))
        ot.append(geom.add_vertex(outer_radius * s, outer_radius * c, z_max))
    for i in range(segments):
        geom.add_face(ob[i], ob[i + 1], ot[i + 1])
        geom.add_face(ob[i], ot[i + 1], ot[i])
        geom.add_face(ib[i + 1], ib[i], it[i])
        geom.add_face(ib[i + 1], it[i], it[i + 1])
        geom.add_face(it[i], ot[i], ot[i + 1])
        geom.add_face(it[i], ot[i + 1], it[i + 1])
        geom.add_face(ib[i + 1], ob[i + 1], ob[i])
        geom.add_face(ib[i + 1], ob[i], ib[i])
    geom.add_face(ib[0], ob[0], ot[0])
    geom.add_face(ib[0], ot[0], it[0])
    geom.add_face(ob[-1], ib[-1], it[-1])
    geom.add_face(ob[-1], it[-1], ot[-1])
    return geom


def _bottle_shell(height: float = 0.210) -> object:
    """Clear PET-style bottle (var_bottle_top L115-149)."""
    outer = [
        (0.000, 0.000), (0.028, 0.000), (0.032, 0.003), (0.034, 0.012),
        (0.034, 0.152), (0.032, 0.162), (0.018, 0.178), (0.017, 0.185),
        (0.017, 0.198), (0.018, height),
    ]
    inner = [
        (0.000, 0.002), (0.026, 0.002), (0.030, 0.005), (0.032, 0.014),
        (0.032, 0.150), (0.030, 0.160), (0.016, 0.176), (0.014, 0.183),
        (0.014, 0.198), (0.015, height),
    ]
    return mesh_from_geometry(
        LatheGeometry.from_shell_profiles(
            outer, inner, segments=48, start_cap="flat", end_cap="round", lip_samples=6
        ),
        "bottle_shell",
    )


def _thread_collar() -> object:
    """Threaded bottle-neck collar + transition shroud (var_bottle_top L86-112)."""
    profile = [
        (0.016, 0.000), (0.019, 0.002), (0.016, 0.004), (0.019, 0.006),
        (0.016, 0.008), (0.019, 0.010), (0.016, 0.012), (0.019, 0.014),
        (0.016, 0.016), (0.019, 0.018), (0.017, 0.021), (0.019, 0.024),
        (0.028, 0.030), (0.038, 0.036), (0.044, 0.041),
    ]
    return mesh_from_geometry(LatheGeometry(profile, segments=40, closed=True), "bottle_thread_collar")


def _squeeze_bulb_geom() -> object:
    """Ovoid elastomer squeeze bulb (var_squeeze_bulb L234-246)."""
    profile: list[tuple[float, float]] = []
    steps = 20
    for i in range(steps + 1):
        theta = math.pi * (i / steps)
        profile.append((0.022 * math.sin(theta), 0.048 * (1.0 - math.cos(theta)) * 0.5))
    return mesh_from_geometry(LatheGeometry(profile, segments=28, closed=True), "bulb_shell")


def _hose(name: str, points: list[tuple[float, float, float]], radius: float) -> object:
    return mesh_from_geometry(
        tube_from_spline_points(
            points, radius=radius, samples_per_segment=14, radial_segments=14, cap_ends=True,
            up_hint=(0.0, 1.0, 0.0),
        ),
        name,
    )


# --------------------------------------------------------------------------- #
# body_form modules — build root pump_body and publish model.meta["wfp"]
# --------------------------------------------------------------------------- #
def _body_iface(barrel_visual: str) -> InterfaceSpec:
    # Re-exported to downstream slots; never consumed by an auto chain joint.
    return InterfaceSpec(
        interface_name="body",
        part_name="pump_body",
        visual_name=barrel_visual,
        face_side="positive_z",
        anchor_local=(0.0, 0.0, 0.0),
    )


def _publish(model: ArticulatedObject, meta: dict) -> None:
    model.meta["wfp"] = meta


def _emit_mount_deck(body, mount_xy, cap_top_z: float, inner_r: float) -> float:
    """A small known-geometry cylinder deck at the pump-column top. All actuator
    hardware sits on it and nothing body-side protrudes above it, so crank/bulb/
    lever mounts never collide with a body cap. Returns mount_top_z (deck top)."""
    mx, my = mount_xy
    deck_h = 0.012
    body.visual(
        Cylinder(radius=inner_r + 0.006, length=deck_h),
        origin=Origin(xyz=(mx, my, cap_top_z - 0.004 + deck_h / 2.0)),
        material="body_dark", name="mount_deck", material_class_id="plastic.opaque_glossy_molded",
    )
    return cap_top_z - 0.004 + deck_h


def _build_twin_barrel(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedWaterFilterPumpConfig = ctx.config  # type: ignore[assignment]
    m = ctx.model
    body = m.part("pump_body")
    rs, hs = r.body_radius_scale, r.body_height_scale
    pump_r = 0.021 * rs
    filt_r = 0.018 * rs
    filt_dx = 0.036 * rs
    body_h = 0.150 * hs
    filt_h = 0.112 * hs
    collar_h = 0.016
    collar_top = body_h + collar_h

    body.visual(Cylinder(radius=pump_r + 0.004, length=0.007),
                origin=Origin(xyz=(0.0, 0.0, 0.0035)), material="body_dark", name="base_pad", material_class_id="plastic.opaque_glossy_molded")
    body.visual(Cylinder(radius=filt_r + 0.004, length=0.007),
                origin=Origin(xyz=(filt_dx, 0.0, 0.0035)), material="body_dark", name="filter_base_pad", material_class_id="plastic.opaque_glossy_molded")
    body.visual(Cylinder(radius=pump_r, length=body_h),
                origin=Origin(xyz=(0.0, 0.0, body_h / 2.0)), material="body_main", name="pump_barrel", material_class_id="plastic.opaque_glossy_molded")
    body.visual(Cylinder(radius=filt_r, length=filt_h),
                origin=Origin(xyz=(filt_dx, 0.0, filt_h / 2.0)), material="body_main", name="filter_barrel", material_class_id="plastic.opaque_glossy_molded")
    body.visual(Cylinder(radius=pump_r + 0.0025, length=collar_h),
                origin=Origin(xyz=(0.0, 0.0, body_h + collar_h / 2.0)), material="body_dark", name="top_collar", material_class_id="plastic.opaque_glossy_molded")
    # Static fluted filter cap on the filter barrel (Rule 1: non-articulating).
    body.visual(_knob_cap(0.024 * rs, 0.026, count=12, depth=0.001, name="filter_cap_knob"),
                origin=Origin(xyz=(filt_dx, 0.0, filt_h)), material="body_dark", name="filter_cap", material_class_id="plastic.patterned_textured")
    # Rear rubber grip pad (-x).
    body.visual(Box((0.006, 0.018, 0.085)),
                origin=Origin(xyz=(-(pump_r - 0.0016), 0.0, 0.070)),
                material="grip_rubber", name="grip_pad", material_class_id="rubber.smooth_plain")
    # Grip ribs (multiplicity) on the rear arc of the pump barrel, host-conformal.
    n = r.rib_count
    arc0, arc1 = math.radians(150.0), math.radians(210.0)
    for i in range(n):
        a = arc0 + (arc1 - arc0) * (i / max(1, n - 1))
        rr = pump_r + 0.0014 - 0.0018
        body.visual(Box((0.0028, 0.006, 0.055)),
                    origin=Origin(xyz=(rr * math.cos(a), rr * math.sin(a), 0.085), rpy=(0.0, 0.0, a)),
                    material="body_main", name=f"body_rib_{i}", material_class_id="plastic.patterned_textured")

    mount_top = _emit_mount_deck(body, (0.0, 0.0), collar_top, pump_r)
    _publish(m, {
        "mount_xy": (0.0, 0.0), "mount_top_z": mount_top,
        "barrel_inner_r": pump_r, "barrel_bottom_z": 0.007,
        "rod_overlap_visuals": ["pump_barrel", "top_collar", "mount_deck"],
        "outlet_anchor": (filt_dx + filt_r, 0.0, filt_h * 0.72, 1.0),
        "intake_anchor": (0.0, pump_r, 0.030, 2.0),  # +y face
        "base_center_xy": (filt_dx * 0.5, 0.0), "base_bottom_z": 0.0,
        "base_radius": filt_dx * 0.5 + pump_r + 0.01,
        "has_side_sockets": False,
    })
    return ModuleBuild(module_name="twin_barrel", parts_emitted=["pump_body"],
                       interfaces={"downstream": _body_iface("pump_barrel")})


def _single_cylinder_common(ctx: ModuleBuildContext, *, bottle: bool) -> tuple[float, float, float]:
    """Returns (R, body_top_z, manifold_top_z). The top cap + manifold stack is
    derived from the body top so it stays in contact at every height scale."""
    r: ResolvedWaterFilterPumpConfig = ctx.config  # type: ignore[assignment]
    m = ctx.model
    body = m.get_part("pump_body")
    rs, hs = r.body_radius_scale, r.body_height_scale
    R = 0.045 * rs
    H = 0.185 * hs
    body_top = 0.015 + H
    body.visual(Cylinder(radius=R, length=H),
                origin=Origin(xyz=(0.0, 0.0, 0.015 + H / 2.0)), material="body_main", name="cylindrical_body", material_class_id="plastic.opaque_glossy_molded")
    tc_h = 0.048
    tc_center = body_top - 0.014 + tc_h / 2.0
    tc_top = tc_center + tc_h / 2.0
    body.visual(Cylinder(radius=R + 0.0025, length=tc_h),
                origin=Origin(xyz=(0.0, 0.0, tc_center)), material="body_main", name="top_cap", material_class_id="plastic.opaque_glossy_molded")
    md_h = 0.020
    md_center = tc_top - 0.006 + md_h / 2.0
    md_top = md_center + md_h / 2.0
    body.visual(Cylinder(radius=0.026, length=md_h),
                origin=Origin(xyz=(0.0, 0.0, md_center)), material="body_dark", name="top_manifold_disk", material_class_id="plastic.opaque_glossy_molded")
    sock_z = tc_center
    body.visual(Cylinder(radius=0.012, length=0.010),
                origin=Origin(xyz=(-R - 0.007, 0.0, sock_z), rpy=_ROT_Y90),
                material="body_main", name="outlet_socket", material_class_id="plastic.opaque_glossy_molded")
    body.visual(Cylinder(radius=0.012, length=0.010),
                origin=Origin(xyz=(R + 0.007, 0.0, sock_z), rpy=_ROT_Y90),
                material="body_main", name="intake_socket", material_class_id="plastic.opaque_glossy_molded")
    # Rear black grip panel (-x face) + finger scallops (multiplicity) on it.
    body.visual(mesh_from_geometry(_curved_grip_panel(
        inner_radius=R - 0.0015, outer_radius=R + 0.006, z_min=0.055 * hs, z_max=body_top - 0.02,
        angle_min=math.radians(180 - 42), angle_max=math.radians(180 + 42)), "black_grip_panel"),
        material="grip_rubber", name="black_grip_panel", material_class_id="rubber.smooth_plain")
    n = r.scallop_count
    z0, z1 = 0.070 * hs, body_top - 0.03
    for i in range(n):
        z = z0 + (z1 - z0) * (i / max(1, n - 1))
        body.visual(mesh_from_geometry(
            CylinderGeometry(radius=0.0048, height=0.026, radial_segments=14)
            .rotate_y(math.pi / 2.0).translate(-(R + 0.001), 0.0, z), f"scallop_geo_{i}"),
            material="body_main", name=f"scallop_{i}", material_class_id="plastic.patterned_textured")
    return R, body_top, md_top


def _build_single_cylinder(ctx: ModuleBuildContext) -> ModuleBuild:
    m = ctx.model
    m.part("pump_body")
    R, body_top, md_top = _single_cylinder_common(ctx, bottle=False)
    body = m.get_part("pump_body")
    body.visual(Cylinder(radius=R + 0.002, length=0.030),
                origin=Origin(xyz=(0.0, 0.0, 0.015)), material="body_dark", name="bottom_cap", material_class_id="plastic.opaque_glossy_molded")
    mount_top = _emit_mount_deck(body, (0.0, 0.0), md_top, 0.013)
    anchor_z = body_top - 0.020
    _publish(m, {
        "mount_xy": (0.0, 0.0), "mount_top_z": mount_top,
        "barrel_inner_r": 0.013, "barrel_bottom_z": 0.0,
        "rod_overlap_visuals": ["cylindrical_body", "top_cap", "top_manifold_disk", "mount_deck"],
        "outlet_anchor": (-R, 0.0, anchor_z, -1.0),
        "intake_anchor": (R, 0.0, anchor_z, 1.0),
        "base_center_xy": (0.0, 0.0), "base_bottom_z": 0.0, "base_radius": R + 0.006,
        "has_side_sockets": True,
    })
    return ModuleBuild(module_name="single_cylinder", parts_emitted=["pump_body"],
                       interfaces={"downstream": _body_iface("cylindrical_body")})


def _build_bottle_top(ctx: ModuleBuildContext) -> ModuleBuild:
    m = ctx.model
    m.part("pump_body")
    R, body_top, md_top = _single_cylinder_common(ctx, bottle=True)
    body = m.get_part("pump_body")
    # Threaded collar at the base + a clear bottle hanging below, folded in as
    # body visuals (Rule 1: no articulation -> not separate parts).
    body.visual(_thread_collar(),
                origin=Origin(xyz=(0.0, 0.0, -0.018)), material="body_dark", name="bottle_thread_collar", material_class_id="plastic.patterned_textured")
    body.visual(_bottle_shell(0.200),
                origin=Origin(xyz=(0.0, 0.0, -0.196)), material="hose_clear", name="bottle_shell", material_class_id="plastic.clear_rigid")
    mount_top = _emit_mount_deck(body, (0.0, 0.0), md_top, 0.013)
    anchor_z = body_top - 0.020
    _publish(m, {
        "mount_xy": (0.0, 0.0), "mount_top_z": mount_top,
        "barrel_inner_r": 0.013, "barrel_bottom_z": 0.0,
        "rod_overlap_visuals": ["cylindrical_body", "top_cap", "top_manifold_disk", "mount_deck"],
        "outlet_anchor": (-R, 0.0, anchor_z, -1.0),
        "intake_anchor": (R, 0.0, anchor_z, 1.0),
        "base_center_xy": (0.0, 0.0), "base_bottom_z": 0.0, "base_radius": R + 0.006,
        "has_side_sockets": True,
    })
    return ModuleBuild(module_name="bottle_top", parts_emitted=["pump_body"],
                       interfaces={"downstream": _body_iface("cylindrical_body")})


def _build_parallel_sleeve(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedWaterFilterPumpConfig = ctx.config  # type: ignore[assignment]
    m = ctx.model
    body = m.part("pump_body")
    rs, hs = r.body_radius_scale, r.body_height_scale
    filt_r = 0.030 * rs
    filt_h = 0.235 * hs
    filt_x = 0.018
    sleeve_x = -0.035
    sleeve_r = 0.0145
    sleeve_h = 0.220 * hs
    body.visual(Cylinder(radius=filt_r, length=filt_h),
                origin=Origin(xyz=(filt_x, 0.0, 0.015 + filt_h / 2.0)), material="body_main", name="filter_body", material_class_id="plastic.opaque_glossy_molded")
    body.visual(Cylinder(radius=filt_r + 0.003, length=0.025),
                origin=Origin(xyz=(filt_x, 0.0, 0.018)), material="body_dark", name="base_cap", material_class_id="plastic.opaque_glossy_molded")
    body.visual(_knob_cap(0.066 * rs, 0.030, count=32, depth=0.0015, name="ribbed_filter_cap"),
                origin=Origin(xyz=(filt_x, 0.0, 0.015 + filt_h + 0.004)), material="body_main", name="ribbed_filter_cap", material_class_id="plastic.patterned_textured")
    body.visual(Cylinder(radius=sleeve_r, length=sleeve_h),
                origin=Origin(xyz=(sleeve_x, 0.0, 0.018 + sleeve_h / 2.0)), material="body_main", name="pump_sleeve", material_class_id="plastic.opaque_glossy_molded")
    # Front recess/label panel on the filter body (-y front), host-conformal.
    body.visual(Box((0.014, 0.004, 0.125 * hs)),
                origin=Origin(xyz=(filt_x, -(filt_r - 0.0005), 0.020 + filt_h * 0.5)),
                material="body_light", name="front_recess_panel", material_class_id="plastic.opaque_glossy_molded")
    # Bridge webs (multiplicity) evenly stacked between the two columns.
    n = r.web_count
    span_lo, span_hi = 0.070 * hs, 0.190 * hs
    web_cx = (filt_x + sleeve_x) / 2.0
    for i in range(n):
        z = span_lo + (span_hi - span_lo) * (i / max(1, n - 1))
        body.visual(Box((abs(filt_x - sleeve_x) + 0.006, 0.010, 0.028)),
                    origin=Origin(xyz=(web_cx, 0.010, z)), material="body_light", name=f"bridge_web_{i}", material_class_id="plastic.opaque_glossy_molded")

    mount_top = _emit_mount_deck(body, (sleeve_x, 0.0), 0.018 + sleeve_h, sleeve_r)
    _publish(m, {
        "mount_xy": (sleeve_x, 0.0), "mount_top_z": mount_top,
        "barrel_inner_r": sleeve_r, "barrel_bottom_z": 0.022,
        "rod_overlap_visuals": ["pump_sleeve", "mount_deck"],
        "outlet_anchor": (filt_x + filt_r, 0.0, 0.015 + filt_h * 0.92, 1.0),
        "intake_anchor": (filt_x + filt_r, 0.0, 0.015 + filt_h * 0.25, 1.0),
        "base_center_xy": (filt_x, 0.0), "base_bottom_z": 0.0, "base_radius": filt_r + 0.006,
        "has_side_sockets": False,
    })
    return ModuleBuild(module_name="parallel_sleeve", parts_emitted=["pump_body"],
                       interfaces={"downstream": _body_iface("pump_sleeve")})


def _build_inline_coaxial(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedWaterFilterPumpConfig = ctx.config  # type: ignore[assignment]
    m = ctx.model
    body = m.part("pump_body")
    rs, hs = r.body_radius_scale, r.body_height_scale
    cx = 0.0
    filt_r = 0.028 * rs
    filt_h = 0.200 * hs
    body.visual(Cylinder(radius=filt_r + 0.003, length=0.022),
                origin=Origin(xyz=(cx, 0.0, 0.016)), material="body_dark", name="base_cap", material_class_id="plastic.opaque_glossy_molded")
    body.visual(Cylinder(radius=filt_r, length=filt_h),
                origin=Origin(xyz=(cx, 0.0, 0.027 + filt_h / 2.0)), material="body_main", name="filter_body", material_class_id="plastic.opaque_glossy_molded")
    trans_z = 0.027 + filt_h + 0.011
    body.visual(_knob_cap(0.058 * rs, 0.022, count=28, depth=0.0014, name="ribbed_transition"),
                origin=Origin(xyz=(cx, 0.0, trans_z)), material="body_main", name="ribbed_transition", material_class_id="plastic.patterned_textured")
    barrel_r = 0.024 * rs
    barrel_h = 0.100 * hs
    barrel_z0 = trans_z + 0.011
    body.visual(Cylinder(radius=barrel_r, length=barrel_h),
                origin=Origin(xyz=(cx, 0.0, barrel_z0 + barrel_h / 2.0)), material="body_main", name="pump_barrel", material_class_id="plastic.opaque_glossy_molded")
    collar_z = barrel_z0 + barrel_h
    body.visual(Box((0.013, 0.004, 0.110 * hs)),
                origin=Origin(xyz=(cx, -(filt_r - 0.0005), 0.030 + filt_h * 0.5)),
                material="body_light", name="front_recess_panel", material_class_id="plastic.opaque_glossy_molded")
    mount_top = _emit_mount_deck(body, (cx, 0.0), collar_z, barrel_r)
    _publish(m, {
        "mount_xy": (cx, 0.0), "mount_top_z": mount_top,
        "barrel_inner_r": barrel_r, "barrel_bottom_z": 0.027,
        "rod_overlap_visuals": ["filter_body", "ribbed_transition", "pump_barrel", "mount_deck"],
        "outlet_anchor": (cx + filt_r, 0.0, 0.027 + filt_h * 0.85, 1.0),
        "intake_anchor": (cx + filt_r, 0.0, 0.027 + filt_h * 0.30, 1.0),
        "base_center_xy": (cx, 0.0), "base_bottom_z": 0.0, "base_radius": filt_r + 0.006,
        "has_side_sockets": False,
    })
    return ModuleBuild(module_name="inline_coaxial", parts_emitted=["pump_body"],
                       interfaces={"downstream": _body_iface("filter_body")})


# --------------------------------------------------------------------------- #
# pump_actuation modules
# --------------------------------------------------------------------------- #
def _wfp(ctx: ModuleBuildContext) -> dict:
    return ctx.model.meta["wfp"]


def _grip_on_rod(part, r: ResolvedWaterFilterPumpConfig, top_local: float) -> None:
    """Attach a T-bar / T-handle / ring-pull grip to the top of a piston rod."""
    grip = r.handle_grip_form
    if grip == "ring_pull":
        # Vertical D-ring pull loop; its bottom tube embeds onto the rod top so
        # the loop is connected to the rod (a flat loop would only encircle it).
        part.visual(mesh_from_geometry(
            TorusGeometry(radius=0.022, tube=0.005, radial_segments=14, tubular_segments=32)
            .rotate_x(math.pi / 2.0), "ring_pull_loop"),
            origin=Origin(xyz=(0.0, 0.0, top_local + 0.022)), material="metal_rod", name="handle_grip", material_class_id="metal.stainless_matte")
    elif grip == "thandle":
        part.visual(mesh_from_geometry(
            CapsuleGeometry(radius=0.012, length=0.100, radial_segments=18, height_segments=6)
            .rotate_y(math.pi / 2.0), "thandle_grip"),
            origin=Origin(xyz=(0.0, 0.0, top_local + 0.006)), material="body_main", name="handle_grip", material_class_id="plastic.opaque_glossy_molded")
    else:  # tbar paddle crossbar
        part.visual(Box((0.075, 0.018, 0.013)),
                    origin=Origin(xyz=(0.0, 0.0, top_local + 0.003)), material="body_main", name="handle_grip", material_class_id="plastic.opaque_glossy_molded")


def _build_piston(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedWaterFilterPumpConfig = ctx.config  # type: ignore[assignment]
    m = ctx.model
    meta = _wfp(ctx)
    mx, my = meta["mount_xy"]
    mtz = meta["mount_top_z"]
    bbz = meta["barrel_bottom_z"]
    bir = meta["barrel_inner_r"]
    stroke = round(0.082 * r.stroke_scale, 5)
    rod_r = max(0.004, min(0.008, bir - 0.003))

    part = m.part("pump_handle")
    # Rod stays deep in the barrel but clears the base caps / tripod hub.
    rod_bottom_local = (bbz + 0.035) - mtz  # negative
    rod_top_local = 0.028
    rod_len = rod_top_local - rod_bottom_local
    part.visual(Cylinder(radius=rod_r, length=rod_len),
                origin=Origin(xyz=(0.0, 0.0, (rod_top_local + rod_bottom_local) / 2.0)),
                material="metal_rod", name="plunger_rod", material_class_id="metal.stainless_matte")
    _grip_on_rod(part, r, rod_top_local)

    joint = m.articulation(
        "body_to_actuator", ArticulationType.PRISMATIC, parent=m.get_part("pump_body"), child=part,
        origin=Origin(xyz=(mx, my, mtz)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=45.0, velocity=0.35, lower=0.0, upper=stroke),
    )
    m.meta["wfp_actuator"] = {
        "part": "pump_handle", "joint": "body_to_actuator", "kind": "piston",
        "rod": "plunger_rod", "overlap": meta["rod_overlap_visuals"], "stroke": stroke,
    }
    return ModuleBuild(module_name=ctx.module_name, parts_emitted=["pump_handle"],
                       internal_articulations=[joint.name],
                       interfaces={"downstream": ctx.upstream_interface})


def _build_lever(ctx: ModuleBuildContext) -> ModuleBuild:
    m = ctx.model
    meta = _wfp(ctx)
    mx, my = meta["mount_xy"]
    mtz = meta["mount_top_z"]
    meta["barrel_bottom_z"]
    bir = meta["barrel_inner_r"]
    body = m.get_part("pump_body")
    # Pivot fulcrum post added to the body at the mount so the REVOLUTE origin
    # sits on real hardware (Rule 2 / origin-far honesty).
    body.visual(Cylinder(radius=0.011, length=0.016),
                origin=Origin(xyz=(mx, my, mtz + 0.003)), material="body_main", name="pivot_post", material_class_id="plastic.opaque_glossy_molded")

    part = m.part("pump_handle")
    part.visual(Cylinder(radius=0.013, length=0.016),
                origin=Origin(xyz=(0.0, 0.0, 0.0)), material="fitting_grey", name="pivot_boss", material_class_id="plastic.opaque_glossy_molded")
    rod_r = max(0.004, min(0.008, bir - 0.003))
    # Short piston stub: with the modest lever throw below it stays inside the
    # bore radius (sin(upper)*insertion < barrel radius) instead of swinging out.
    rod_len = 0.090
    part.visual(Cylinder(radius=rod_r, length=rod_len),
                origin=Origin(xyz=(0.0, 0.0, -rod_len / 2.0 + 0.004)), material="metal_rod", name="plunger_rod", material_class_id="metal.stainless_matte")
    # Lever arm extends -y and swings up (axis -x); grip at the far end.
    part.visual(Cylinder(radius=0.007, length=0.100),
                origin=Origin(xyz=(0.0, -0.058, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material="body_main", name="handle_stem", material_class_id="plastic.opaque_glossy_molded")
    part.visual(mesh_from_geometry(
        CapsuleGeometry(radius=0.013, length=0.050, radial_segments=18, height_segments=6),
        "lever_grip"),
        origin=Origin(xyz=(0.0, -0.116, 0.0)), material="body_main", name="handle_grip", material_class_id="plastic.opaque_glossy_molded")

    joint = m.articulation(
        "body_to_actuator", ArticulationType.REVOLUTE, parent=body, child=part,
        origin=Origin(xyz=(mx, my, mtz + 0.008)), axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=35.0, velocity=1.5, lower=0.0, upper=0.30),
    )
    m.meta["wfp_actuator"] = {
        "part": "pump_handle", "joint": "body_to_actuator", "kind": "lever",
        "rod": "plunger_rod", "overlap": meta["rod_overlap_visuals"],
        "pivot": ("pivot_post", "pivot_boss"),
    }
    return ModuleBuild(module_name="lever_pump", parts_emitted=["pump_handle"],
                       internal_articulations=[joint.name],
                       interfaces={"downstream": ctx.upstream_interface})


def _build_crank(ctx: ModuleBuildContext) -> ModuleBuild:
    m = ctx.model
    meta = _wfp(ctx)
    mx, my = meta["mount_xy"]
    mtz = meta["mount_top_z"]
    body = m.get_part("pump_body")
    body.visual(Cylinder(radius=0.013, length=0.014),
                origin=Origin(xyz=(mx, my, mtz + 0.004)), material="body_dark", name="crank_hub_boss", material_class_id="plastic.opaque_glossy_molded")

    part = m.part("crank_handle")
    part.visual(Cylinder(radius=0.010, length=0.012),
                origin=Origin(xyz=(0.0, 0.0, 0.002)), material="body_dark", name="crank_hub", material_class_id="plastic.opaque_glossy_molded")
    part.visual(Cylinder(radius=0.007, length=0.055),
                origin=Origin(xyz=(0.0275, 0.0, 0.006), rpy=_ROT_Y90),
                material="body_main", name="crank_arm", material_class_id="plastic.opaque_glossy_molded")
    part.visual(Cylinder(radius=0.013, length=0.034),
                origin=Origin(xyz=(0.055, 0.0, 0.006)), material="grip_rubber", name="crank_grip_knob", material_class_id="rubber.smooth_plain")

    joint = m.articulation(
        "body_to_actuator", ArticulationType.CONTINUOUS, parent=body, child=part,
        origin=Origin(xyz=(mx, my, mtz + 0.011)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=25.0, velocity=4.0),
    )
    m.meta["wfp_actuator"] = {
        "part": "crank_handle", "joint": "body_to_actuator", "kind": "crank",
        "hub": ("crank_hub_boss", "crank_hub"), "knob": "crank_grip_knob",
    }
    return ModuleBuild(module_name="rotary_crank", parts_emitted=["crank_handle"],
                       internal_articulations=[joint.name],
                       interfaces={"downstream": ctx.upstream_interface})


def _build_squeeze_bulb(ctx: ModuleBuildContext) -> ModuleBuild:
    m = ctx.model
    meta = _wfp(ctx)
    mx, my = meta["mount_xy"]
    mtz = meta["mount_top_z"]
    body = m.get_part("pump_body")
    neck_h = 0.010
    body.visual(Cylinder(radius=0.014, length=neck_h),
                origin=Origin(xyz=(mx, my, mtz + neck_h / 2.0)), material="body_dark", name="bulb_neck", material_class_id="plastic.opaque_glossy_molded")
    for i, (dx, dy) in enumerate(((0.010, 0.012), (-0.010, -0.012))):
        body.visual(Cylinder(radius=0.004, length=0.006),
                    origin=Origin(xyz=(mx + dx, my + dy, mtz - 0.006)),
                    material="body_dark", name=f"check_valve_nub_{i}", material_class_id="rubber.smooth_plain")

    part = m.part("squeeze_bulb")
    part.visual(_squeeze_bulb_geom(), origin=Origin(xyz=(0.0, 0.0, 0.003)),
                material="grip_rubber", name="bulb_shell", material_class_id="rubber.smooth_plain")
    part.visual(Cylinder(radius=0.013, length=0.006),
                origin=Origin(xyz=(0.0, 0.0, 0.003)), material="grip_rubber", name="bulb_base_collar", material_class_id="rubber.smooth_plain")

    joint = m.articulation(
        "body_to_actuator", ArticulationType.PRISMATIC, parent=body, child=part,
        origin=Origin(xyz=(mx, my, mtz + neck_h)), axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.20, lower=0.0, upper=0.012),
    )
    m.meta["wfp_actuator"] = {
        "part": "squeeze_bulb", "joint": "body_to_actuator", "kind": "bulb",
        "collar": ("bulb_neck", "bulb_base_collar"),
    }
    return ModuleBuild(module_name="squeeze_bulb", parts_emitted=["squeeze_bulb"],
                       internal_articulations=[joint.name],
                       interfaces={"downstream": ctx.upstream_interface})


# --------------------------------------------------------------------------- #
# hose_ports modules
# --------------------------------------------------------------------------- #
def _barb_and_hose(body, meta_anchor, *, name_prefix: str, down: bool, add_canister: bool,
                   tip: str) -> None:
    """Add an outward barb + spline hose + terminal fitting as body visuals."""
    ax, ay, az, sign = meta_anchor
    if abs(sign) == 2.0:  # +y face
        nx, ny = 0.0, 1.0
        rpy = (-math.pi / 2.0, 0.0, 0.0)
    else:
        nx, ny = (1.0 if sign > 0 else -1.0), 0.0
        rpy = _ROT_Y90
    barb_len = 0.014
    bx = ax + nx * barb_len / 2.0
    by = ay + ny * barb_len / 2.0
    body.visual(Cylinder(radius=0.005, length=barb_len),
                origin=Origin(xyz=(bx, by, az), rpy=rpy), material="fitting_grey", name=f"{name_prefix}_barb", material_class_id="plastic.opaque_glossy_molded")
    tipx = ax + nx * barb_len
    tipy = ay + ny * barb_len
    end_z = 0.045 if down else az
    pts = [
        (tipx, tipy, az),
        (tipx + nx * 0.045 + 0.006, tipy + ny * 0.045, az - 0.015),
        (tipx + nx * 0.075, tipy + ny * 0.075, (az + end_z) / 2.0),
        (tipx + nx * 0.085, tipy + ny * 0.085, end_z + 0.010),
        (tipx + nx * 0.080, tipy + ny * 0.080, end_z),
    ]
    body.visual(_hose(f"{name_prefix}_hose", pts, 0.0042), material="hose_clear", name=f"{name_prefix}_hose", material_class_id="plastic.clear_rigid")
    ex, ey, ez = pts[-1]
    if tip == "prefilter":
        body.visual(Cylinder(radius=0.010, length=0.028),
                    origin=Origin(xyz=(ex, ey, ez - 0.010)), material="grip_rubber", name=f"{name_prefix}_prefilter", material_class_id="rubber.sponge_foam")
    else:
        body.visual(Cylinder(radius=0.0066, length=0.022),
                    origin=Origin(xyz=(ex, ey, ez), rpy=(0.4, 0.0, 0.0)),
                    material="fitting_grey", name=f"{name_prefix}_fitting", material_class_id="plastic.opaque_glossy_molded")
    if add_canister:
        # Inline sediment canister spliced mid-run on the intake hose (Cylinder
        # primitives standing in for var_inline_prefilter's cadquery canister).
        mx = tipx + nx * 0.048
        my = tipy + ny * 0.048
        mz = az - 0.006
        body.visual(Cylinder(radius=0.011, length=0.036),
                    origin=Origin(xyz=(mx, my, mz), rpy=rpy), material="body_dark", name="inline_canister", material_class_id="plastic.opaque_glossy_molded")
        body.visual(Cylinder(radius=0.0124, length=0.005),
                    origin=Origin(xyz=(mx, my, mz), rpy=rpy), material="fitting_grey", name="canister_ring", material_class_id="plastic.opaque_glossy_molded")


def _build_fixed_hoses(ctx: ModuleBuildContext) -> ModuleBuild:
    m = ctx.model
    meta = _wfp(ctx)
    body = m.get_part("pump_body")
    _barb_and_hose(body, meta["intake_anchor"], name_prefix="intake", down=True,
                   add_canister=(ctx.module_name == "fixed_hoses_prefilter"), tip="prefilter")
    _barb_and_hose(body, meta["outlet_anchor"], name_prefix="outlet", down=False,
                   add_canister=False, tip="fitting")
    return ModuleBuild(module_name=ctx.module_name, parts_emitted=[],
                       interfaces={"downstream": ctx.upstream_interface})


def _build_single_outlet(ctx: ModuleBuildContext) -> ModuleBuild:
    m = ctx.model
    meta = _wfp(ctx)
    body = m.get_part("pump_body")
    _barb_and_hose(body, meta["outlet_anchor"], name_prefix="outlet", down=True,
                   add_canister=False, tip="fitting")
    return ModuleBuild(module_name="single_outlet", parts_emitted=[],
                       interfaces={"downstream": ctx.upstream_interface})


def _build_detachable_ports(ctx: ModuleBuildContext) -> ModuleBuild:
    m = ctx.model
    meta = _wfp(ctx)
    body = m.get_part("pump_body")
    parts: list[str] = []
    joints: list[str] = []
    for anchor, label, sign in (
        (meta["outlet_anchor"], "outlet_port", -1.0),
        (meta["intake_anchor"], "intake_port", 1.0),
    ):
        ax, ay, az, asign = anchor
        s = 1.0 if asign > 0 else -1.0
        # Socket boss on the body; the port collar seats on it with a small
        # (<overlap_tol) embed so the port stays connected to the grounded body
        # at rest. Rail slide -> joint grandfathered (rotated slide face).
        body.visual(Cylinder(radius=0.012, length=0.012),
                    origin=Origin(xyz=(ax + s * 0.005, ay, az), rpy=_ROT_Y90),
                    material="body_main", name=f"{label}_socket", material_class_id="plastic.opaque_glossy_molded")
        port = m.part(label)
        port.visual(Cylinder(radius=0.0105, length=0.010),
                    origin=Origin(xyz=(s * 0.002, 0.0, 0.0), rpy=_ROT_Y90),
                    material="body_dark", name="port_collar", material_class_id="plastic.opaque_glossy_molded")
        port.visual(Cylinder(radius=0.007, length=0.030),
                    origin=Origin(xyz=(s * 0.018, 0.0, 0.0), rpy=_ROT_Y90),
                    material="body_main", name="port_barb", material_class_id="plastic.opaque_glossy_molded")
        pts = [
            (s * 0.030, 0.0, 0.0),
            (s * 0.062, 0.0, -0.030),
            (s * 0.078, 0.0, -0.090),
            (s * 0.064, 0.0, -0.150),
            (s * 0.050, 0.0, -0.175),
        ]
        port.visual(_hose("port_hose", pts, 0.0044), material="hose_clear", name="port_hose", material_class_id="plastic.clear_rigid")
        port.visual(Cylinder(radius=0.008, length=0.024),
                    origin=Origin(xyz=(s * 0.050, 0.0, -0.185)), material="fitting_grey", name="port_fitting", material_class_id="plastic.opaque_glossy_molded")
        joint = m.articulation(
            f"body_to_{label}", ArticulationType.PRISMATIC, parent=body, child=port,
            origin=Origin(xyz=(ax + s * 0.010, ay, az)), axis=(s, 0.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=0.12, lower=0.0, upper=0.030),
        )
        parts.append(label)
        joints.append(joint.name)
    m.meta["wfp_ports"] = parts
    return ModuleBuild(module_name="detachable_ports", parts_emitted=parts,
                       internal_articulations=joints,
                       interfaces={"downstream": ctx.upstream_interface})


# --------------------------------------------------------------------------- #
# support_base modules
# --------------------------------------------------------------------------- #
def _build_flat_base(ctx: ModuleBuildContext) -> ModuleBuild:
    m = ctx.model
    meta = _wfp(ctx)
    body = m.get_part("pump_body")
    bcx, bcy = meta["base_center_xy"]
    br = meta.get("base_radius", 0.05)
    body.visual(Cylinder(radius=br + 0.006, length=0.006),
                origin=Origin(xyz=(bcx, bcy, meta["base_bottom_z"] + 0.003)),
                material="body_dark", name="foot_ring", material_class_id="plastic.opaque_glossy_molded")
    return ModuleBuild(module_name="flat_base", parts_emitted=[],
                       interfaces={"downstream": ctx.upstream_interface})


def _build_tripod(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedWaterFilterPumpConfig = ctx.config  # type: ignore[assignment]
    m = ctx.model
    meta = _wfp(ctx)
    body = m.get_part("pump_body")
    bcx, bcy = meta["base_center_xy"]
    bz = meta["base_bottom_z"] + 0.004
    hinge_r = meta.get("base_radius", 0.05) + 0.006
    leg_len = 0.065
    strut_len = leg_len - 0.008
    n = r.leg_count
    body.visual(Cylinder(radius=hinge_r, length=0.006),
                origin=Origin(xyz=(bcx, bcy, bz)), material="body_dark", name="tripod_hub", material_class_id="plastic.opaque_glossy_molded")
    parts: list[str] = []
    joints: list[str] = []
    for i in range(n):
        theta = 2.0 * math.pi * i / n
        ct, st = math.cos(theta), math.sin(theta)
        hx = bcx + hinge_r * ct
        hy = bcy + hinge_r * st
        body.visual(Cylinder(radius=0.003, length=0.014),
                    origin=Origin(xyz=(hx, hy, bz), rpy=(-math.pi / 2.0, 0.0, math.pi + theta)),
                    material="body_main", name=f"leg_boss_{i}", material_class_id="plastic.opaque_glossy_molded")
        leg = m.part(f"leg_{i}")
        leg.visual(Cylinder(radius=0.005, length=0.010),
                   origin=Origin(rpy=(-math.pi / 2.0, 0.0, math.pi + theta)),
                   material="body_main", name="pivot_eye", material_class_id="plastic.opaque_glossy_molded")
        leg.visual(Box((0.010, 0.006, strut_len)),
                   origin=Origin(xyz=(0.0, 0.0, -(strut_len / 2.0 + 0.004))),
                   material="body_main", name="strut", material_class_id="plastic.opaque_glossy_molded")
        leg.visual(Cylinder(radius=0.006, length=0.008),
                   origin=Origin(xyz=(0.0, 0.0, -(leg_len - 0.004))),
                   material="grip_rubber", name="foot", material_class_id="rubber.smooth_plain")
        joint = m.articulation(
            f"base_to_leg_{i}", ArticulationType.REVOLUTE, parent=body, child=leg,
            origin=Origin(xyz=(hx, hy, bz)), axis=(st, -ct, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=1.5, lower=0.0, upper=0.55),
        )
        parts.append(f"leg_{i}")
        joints.append(joint.name)
    m.meta["wfp_legs"] = parts
    return ModuleBuild(module_name="tripod_stand", parts_emitted=parts,
                       internal_articulations=joints,
                       interfaces={"downstream": ctx.upstream_interface})


# --------------------------------------------------------------------------- #
# Slot wiring
# --------------------------------------------------------------------------- #
_BODY_FORMS = {
    "twin_barrel": _build_twin_barrel,
    "single_cylinder": _build_single_cylinder,
    "parallel_sleeve": _build_parallel_sleeve,
    "inline_coaxial": _build_inline_coaxial,
    "bottle_top": _build_bottle_top,
}
_ACTUATORS = {
    "piston_paddle": _build_piston,
    "piston_thandle": _build_piston,
    "lever_pump": _build_lever,
    "rotary_crank": _build_crank,
    "squeeze_bulb": _build_squeeze_bulb,
}
_HOSES = {
    "fixed_hoses": _build_fixed_hoses,
    "fixed_hoses_prefilter": _build_fixed_hoses,
    "single_outlet": _build_single_outlet,
    "detachable_ports": _build_detachable_ports,
}
_BASES = {
    "flat_base": _build_flat_base,
    "tripod_stand": _build_tripod,
}


def _slots(r: ResolvedWaterFilterPumpConfig) -> list[SlotSpec]:
    return [
        SlotSpec("body_form", _BODY_FORMS, anchor_choice=r.body_form),
        SlotSpec("pump_actuation", _ACTUATORS, anchor_choice=r.pump_actuation),
        SlotSpec("hose_ports", _HOSES, anchor_choice=r.hose_ports),
        SlotSpec("support_base", _BASES, anchor_choice=r.support_base),
    ]


def _mult_band(n: int) -> str:
    return f"n{n}"


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    choices: list[tuple[str, str]] = [
        ("body_form", r.body_form),
        ("pump_actuation", r.pump_actuation),
        ("hose_ports", r.hose_ports),
        ("support_base", r.support_base),
    ]
    if r.pump_actuation in {"piston_paddle", "piston_thandle"}:
        choices.append(("handle_grip_form", r.handle_grip_form))
    if r.body_form == "twin_barrel":
        choices.append(("grip_rib_multiplicity", _mult_band(r.rib_count)))
    if r.body_form == "parallel_sleeve":
        choices.append(("bridge_web_multiplicity", _mult_band(r.web_count)))
    if r.body_form in {"single_cylinder", "bottle_top"}:
        choices.append(("scallop_multiplicity", _mult_band(r.scallop_count)))
    if r.support_base == "tripod_stand":
        choices.append(("tripod_leg_multiplicity", _mult_band(r.leg_count)))
    choices.append(("palette_style", r.palette_style))
    return choices


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_water_filter_pump(
    config: WaterFilterPumpConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="water_filter_pump", assets=assets)
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


def build_seeded_water_filter_pump(seed: int) -> ArticulatedObject:
    return build_water_filter_pump(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def _apply_captured_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    act = model.meta.get("wfp_actuator", {})
    body = model.get_part("pump_body")
    body_visuals = {v.name for v in body.visuals}
    if act:
        actuator = model.get_part(act["part"])
        if act["kind"] in {"piston", "lever"}:
            overlaps = list(act.get("overlap", []))
            # The rod hides inside the solid barrel/base proxy and behind
            # surface decoration on the barrel wall.
            overlaps += [n for n in ("bottom_cap", "base_cap", "base_pad",
                                     "filter_base_pad", "foot_ring", "tripod_hub",
                                     "black_grip_panel", "front_recess_panel")
                         if n in body_visuals]
            overlaps += [n for n in body_visuals
                         if n.startswith(("scallop_", "body_rib_", "bridge_web_"))]
            for v in overlaps:
                ctx.allow_overlap(body, actuator, elem_a=v, elem_b=act["rod"],
                                  reason="Piston/pump rod slides inside the solid barrel proxy.")
        if act["kind"] == "lever":
            post, boss = act["pivot"]
            for a in (post, "mount_deck", "top_collar"):
                if a not in body_visuals:
                    continue
                for b in (boss, "handle_stem", act["rod"]):
                    ctx.allow_overlap(body, actuator, elem_a=a, elem_b=b,
                                      reason="Lever pivot cluster is a captured fulcrum joint.")
        if act["kind"] == "crank":
            boss_body, hub = act["hub"]
            for a in (boss_body, "mount_deck", "top_collar"):
                if a in body_visuals:
                    ctx.allow_overlap(actuator, body, elem_a=hub, elem_b=a,
                                      reason="Crank hub seats in the hub boss (captured bearing).")
        if act["kind"] == "bulb":
            neck, collar = act["collar"]
            for a in (neck, "mount_deck", "check_valve_nub_0", "check_valve_nub_1"):
                if a not in body_visuals:
                    continue
                for b in (collar, "bulb_shell"):
                    ctx.allow_overlap(actuator, body, elem_a=b, elem_b=a,
                                      reason="Squeeze bulb seats on the neck (elastomer seal).")
    for i, leg in enumerate(model.meta.get("wfp_legs", [])):
        legp = model.get_part(leg)
        ctx.allow_overlap(body, legp, elem_a=f"leg_boss_{i}", elem_b="pivot_eye",
                          reason="Leg pivot eye captures the hinge boss pin.")
        ctx.allow_overlap(body, legp, elem_a="tripod_hub", elem_b="pivot_eye",
                          reason="Leg pivot eye nests at the hub disc.")


def run_water_filter_pump_tests(
    model: ArticulatedObject, config: WaterFilterPumpConfig
) -> TestReport:
    ctx = TestContext(model)
    _apply_captured_overlaps(ctx, model)

    # Identity: a filter body, a real actuator joint, and intake/outlet exist.
    body = model.get_part("pump_body")
    ctx.check("pump_body exists", body is not None, details="root chassis")
    act = model.meta.get("wfp_actuator", {})
    joint = model.get_articulation("body_to_actuator")
    ctx.check(
        "actuator has a real non-fixed joint",
        joint is not None and joint.articulation_type != ArticulationType.FIXED,
        details=f"type={getattr(joint, 'articulation_type', None)}",
    )

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # Targeted mechanism semantics per actuator kind.
    kind = act.get("kind")
    actuator = model.get_part(act["part"]) if act else None
    if actuator is not None and joint is not None and joint.motion_limits is not None:
        lo = joint.motion_limits.lower or 0.0
        hi = joint.motion_limits.upper if joint.motion_limits.upper is not None else math.pi
        if kind in {"piston", "bulb"}:
            with ctx.pose({joint: lo}):
                p0 = ctx.part_world_position(actuator)
            with ctx.pose({joint: hi}):
                p1 = ctx.part_world_position(actuator)
            moved = p0 is not None and p1 is not None and abs(p1[2] - p0[2]) > 0.008
            ctx.check(f"{kind} actuator translates", moved, details=f"p0={p0}, p1={p1}")
        elif kind == "lever":
            g0 = ctx.part_element_world_aabb(actuator, elem="handle_grip")
            with ctx.pose({joint: hi}):
                g1 = ctx.part_element_world_aabb(actuator, elem="handle_grip")
            lifted = (g0 is not None and g1 is not None
                      and (g1[0][2] + g1[1][2]) / 2.0 > (g0[0][2] + g0[1][2]) / 2.0 + 0.015)
            ctx.check("lever grip lifts when swung", lifted, details=f"g0={g0}, g1={g1}")
        elif kind == "crank":
            k0 = ctx.part_element_world_aabb(actuator, elem="crank_grip_knob")
            with ctx.pose({joint: math.pi}):
                k1 = ctx.part_element_world_aabb(actuator, elem="crank_grip_knob")
            swept = (k0 is not None and k1 is not None
                     and (abs((k0[0][0] + k0[1][0]) - (k1[0][0] + k1[1][0])) / 2.0 > 0.010
                          or abs((k0[0][1] + k0[1][1]) - (k1[0][1] + k1[1][1])) / 2.0 > 0.010))
            ctx.check("crank knob sweeps around hub", swept, details=f"k0={k0}, k1={k1}")

    # Detachable ports slide outward.
    for label in model.meta.get("wfp_ports", []):
        port = model.get_part(label)
        pj = model.get_articulation(f"body_to_{label}")
        rest = ctx.part_world_position(port)
        with ctx.pose({pj: pj.motion_limits.upper}):
            out = ctx.part_world_position(port)
        ctx.check(f"{label} detaches outward",
                  rest is not None and out is not None and abs(out[0] - rest[0]) > 0.020,
                  details=f"rest={rest}, out={out}")

    # Tripod legs splay outward.
    legs = model.meta.get("wfp_legs", [])
    if legs:
        leg0 = model.get_part("leg_0")
        lj = model.get_articulation("base_to_leg_0")
        rest = ctx.part_world_aabb(leg0)
        with ctx.pose({lj: lj.motion_limits.upper}):
            splay = ctx.part_world_aabb(leg0)
        ctx.check("leg_0 splays outward",
                  rest is not None and splay is not None
                  and (splay[1][0] - splay[0][0]) + (splay[1][1] - splay[0][1])
                  >= (rest[1][0] - rest[0][0]) + (rest[1][1] - rest[0][1]) - 0.002,
                  details=f"rest={rest}, splay={splay}")

    # Full-travel non-penetration across every movable joint (Rule 5).
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)
    return ctx.report()


__all__ = [
    "WaterFilterPumpConfig",
    "ResolvedWaterFilterPumpConfig",
    "config_from_seed",
    "resolve_config",
    "build_water_filter_pump",
    "build_seeded_water_filter_pump",
    "slot_choices_for_seed",
    "run_water_filter_pump_tests",
]
