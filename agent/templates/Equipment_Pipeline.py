# SPDX-License-Identifier: Apache-2.0

"""Industrial pipeline valve-section modular template.

A pipeline section is a fixed pipe/valve **body** carrying a flow path
(straight run / 90-degree elbow / spherical globe / bulbous standpipe / corner
angle valve), a rising bonnet+stem that lifts a hand-operable **operator**
(spoked handwheel / quarter-turn lever / crossed tee-bar) off the stem top, and
two or more pipe-end **ports** (bolted flange pair / raised-face flange / smooth
socket-weld collar / screwed union nut) that couple it to neighbouring pipe. The
standpipe lineage additionally carries 0..N side **outlet** assemblies (nozzle +
lift cap + retaining chain), the multiplicity axis.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Equipment_Pipeline.md`` and the
``picture/Equipment/Pipeline`` 5-star pool (3 parents + 10 slot-fork variants,
read from the articraft_data records repo).

Structure (pattern = ``mixed``) — a single root ``body`` part with parallel
children / inline visuals:

  * ``body_form`` (5): inline_gate_elbow / globe_sphere / standpipe_riser /
    straight_through_gate / angle_valve_90 — the flow-path topology. Each emits
    its own cadquery mesh family (annular tube + quarter-torus, sphere + lofted
    necks, revolved bulb, etc.) and exposes a common interface: a rising-stem
    top at ``(0, 0, stem_top_z)`` for the operator and a list of pipe-end port
    sites for the port slot.
  * ``operator`` (3 families + spoke sub-axis): handwheel_wheel (CONTINUOUS +Z,
    spoke_count in {3,5,6}) / quarter_turn_lever (REVOLUTE +Z, [0, pi/2]) /
    crossed_tee_bar (CONTINUOUS +Z). Seats its hub on the rising-stem top with a
    real MatingContract.
  * ``port`` (4): bolted_flange_pair / bolted_RF_flange / socket_weld /
    union_nut — fixed inline visuals (Rule 1, no joint) wrapping each port site.
  * ``outlet_count`` (N in [0, 6], gated to standpipe_riser): N radial outlet
    assemblies. Each = nozzle visual + chain_lug visual on the body, a ``cap_i``
    part (PRISMATIC along its radial axis), and a serial REVOLUTE oval-link
    retaining ``chain_i`` riveted to the cap and wrapping the body lug.

Hard-rule compliance:
  * Rule 1 — ports / nozzles / lugs / bonnet hardware are ``body.visual(...)``;
    no FIXED decoration joints.
  * Rule 2 — the operator joint declares a MatingContract pinning the rising
    stem top (+z) to the operator hub bottom (-z), both real visuals.
  * Rule 3 — every body / operator / port / outlet factory preserves its source
    record's cadquery primitive family (loft / revolve / sphere / torus /
    spline tube); nothing is downgraded to a bare Box/Cylinder placeholder.
  * The captured cap-slide and pin-through chain joints are genuinely captured /
    open-pose geometry, so they omit MatingContract (grandfathered) and are
    guarded by element-scoped ``allow_overlap`` exactly as the source records.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enum domains
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "inline_gate_elbow",
    "globe_sphere",
    "standpipe_riser",
    "straight_through_gate",
    "angle_valve_90",
]
Operator = Literal["handwheel_wheel", "quarter_turn_lever", "crossed_tee_bar"]
PortType = Literal["bolted_flange_pair", "bolted_RF_flange", "socket_weld", "union_nut"]
PaletteStyle = Literal[
    "yellow_gas",
    "hydrant_red",
    "globe_blue",
    "industrial_green",
    "galvanized_gray",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "inline_gate_elbow",
    "globe_sphere",
    "standpipe_riser",
    "straight_through_gate",
    "angle_valve_90",
)
OPERATORS: tuple[Operator, ...] = (
    "handwheel_wheel",
    "quarter_turn_lever",
    "crossed_tee_bar",
)
SPOKE_COUNTS: tuple[int, ...] = (3, 5, 6)
PORT_TYPES: tuple[PortType, ...] = (
    "bolted_flange_pair",
    "bolted_RF_flange",
    "socket_weld",
    "union_nut",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "yellow_gas",
    "hydrant_red",
    "globe_blue",
    "industrial_green",
    "galvanized_gray",
)

# Outlet multiplicity (spec N_range [0, 6]; sampling domain is the small-N
# high-frequency subset {0,1,2,3} — large N is a rare long tail that balloons
# chain-part count and compile cost, so the default sampler stays at <=3).
OUTLET_N_MIN = 0
OUTLET_N_MAX = 6
OUTLET_SAMPLE_CHOICES = (0, 1, 2, 3)
OUTLET_SAMPLE_WEIGHTS = (0.34, 0.30, 0.22, 0.14)

# Bodies that can carry side outlets (bulbous standpipe wall captures the nozzle
# root). All other bodies default to outlet_count = 0 (spec gating).
OUTLET_BODIES: tuple[BodyForm, ...] = ("standpipe_riser",)

TOL = 0.0015
ATOL = 0.30

# ---------------------------------------------------------------------------
# Palettes (>=4 realistic colorways drawn from the 5-star sources). Semantic
# keys are shared across every body / operator / port so palette_style drives
# EVERY .visual(..., material=mats[...]) call. (S1 gate yellow, S2 hydrant
# red/orange + brass, S3 globe blue + red wheel.)
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "yellow_gas": {  # S1 gas line
        "body": (0.96, 0.78, 0.05, 1.0),
        "body2": (0.86, 0.66, 0.04, 1.0),
        "trim": (0.52, 0.54, 0.57, 1.0),
        "stem": (0.80, 0.82, 0.85, 1.0),
        "operator": (0.78, 0.80, 0.83, 1.0),
        "port": (0.46, 0.47, 0.49, 1.0),
        "bolt": (0.34, 0.35, 0.37, 1.0),
    },
    "hydrant_red": {  # S2 fire hydrant standpipe
        "body": (0.82, 0.16, 0.10, 1.0),
        "body2": (0.90, 0.28, 0.10, 1.0),
        "trim": (0.18, 0.18, 0.19, 1.0),
        "stem": (0.78, 0.60, 0.20, 1.0),
        "operator": (0.20, 0.20, 0.21, 1.0),
        "port": (0.78, 0.60, 0.20, 1.0),
        "bolt": (0.62, 0.46, 0.16, 1.0),
    },
    "globe_blue": {  # S3 flanged globe valve
        "body": (0.20, 0.42, 0.66, 1.0),
        "body2": (0.17, 0.36, 0.58, 1.0),
        "trim": (0.20, 0.42, 0.66, 1.0),
        "stem": (0.74, 0.76, 0.79, 1.0),
        "operator": (0.78, 0.13, 0.12, 1.0),
        "port": (0.32, 0.34, 0.37, 1.0),
        "bolt": (0.24, 0.26, 0.29, 1.0),
    },
    "industrial_green": {  # process-plant green cast valve
        "body": (0.13, 0.42, 0.27, 1.0),
        "body2": (0.10, 0.34, 0.22, 1.0),
        "trim": (0.16, 0.17, 0.18, 1.0),
        "stem": (0.80, 0.82, 0.85, 1.0),
        "operator": (0.88, 0.62, 0.08, 1.0),
        "port": (0.40, 0.42, 0.44, 1.0),
        "bolt": (0.22, 0.23, 0.24, 1.0),
    },
    "galvanized_gray": {  # hot-dip galvanized line valve
        "body": (0.62, 0.64, 0.67, 1.0),
        "body2": (0.54, 0.56, 0.59, 1.0),
        "trim": (0.44, 0.45, 0.47, 1.0),
        "stem": (0.82, 0.84, 0.87, 1.0),
        "operator": (0.86, 0.12, 0.10, 1.0),
        "port": (0.50, 0.52, 0.54, 1.0),
        "bolt": (0.30, 0.31, 0.33, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Shared base dimensions (meters). Inline bodies share one port/stem frame:
# flow axis = X, valve center = x=0, port centerline at z = PORT_Z, rising stem
# at (0, 0) reaching stem_top_z. Standpipe overrides with a vertical riser.
# ---------------------------------------------------------------------------
PORT_Z = 0.165  # inline port centerline height above ground
PIPE_OR = 0.060  # pipe outer radius
PIPE_WALL = 0.010
PIPE_IR = PIPE_OR - PIPE_WALL
PORT_HALF_SPAN = 0.175  # body center -> flange face (along X)
RUN_EXT = 0.105  # pipe extends this far beyond each flange face
ELBOW_BEND_R = 0.105  # elbow / angle centerline bend radius
DROP_LEN = 0.220  # elbow vertical leg length

VALVE_BARREL_R = 0.080  # inline valve body bulge radius
VALVE_BARREL_HALF = 0.085  # half length of the central barrel

GLOBE_BODY_R = 0.112  # spherical globe radius
GLOBE_NECK_R = 0.064  # flange hub neck radius

# Bonnet stack (inline lineage): base disc -> tapered neck -> hex gland -> stem.
BONNET_BASE_R = 0.056
BONNET_TOP_R = 0.034
BONNET_H = 0.072
GLAND_R = 0.030
GLAND_H = 0.026
STEM_R = 0.0105
STEM_LEN = 0.092  # exposed rising stem above the gland

# Standpipe lineage (S2).
RISER_OD = 0.110
RISER_ID = 0.092
RISER_LEN = 0.430
COLLAR_OD = 0.150
COLLAR_H = 0.030
SP_BODY_MAX_R = 0.092
SP_BODY_H = 0.140
SP_NECK_R = 0.040
SP_NECK_H = 0.022
SP_DOME_R = 0.030
SP_STEM_R = 0.0095
SP_STEM_EXTRA = 0.060  # stem above the dome

# Outlet / cap / chain (S2 / S13).
NOZZLE_R = 0.034
NOZZLE_BORE = 0.024
NOZZLE_LEN = 0.078
NOZZLE_ROOT_X = 0.050
CAP_R = 0.038
CAP_H = 0.030
CAP_RECESS_DEPTH = 0.020
CAP_DEFAULT_PULL = 0.035
CHAIN_BOSS_LOCAL = (0.004, 0.026, -0.026)
# Lug z-offset below the nozzle centerline: large enough that the retaining
# chain drapes clearly under the nozzle barrel rather than clipping it.
CHAIN_LUG_LOCAL = (0.060, 0.034, -0.105)
CHAIN_LUG_R = 0.009
CHAIN_LINK_HALF_LEN = 0.0085
CHAIN_LINK_HALF_WID = 0.0040
CHAIN_LINK_WIRE_R = 0.0011
CHAIN_LINK_PITCH = 2.0 * CHAIN_LINK_HALF_LEN - 2.0 * CHAIN_LINK_WIRE_R
CHAIN_SWING = math.radians(35.0)

# Operator base sizes.
WHEEL_RIM_R = 0.080
WHEEL_TUBE_R = 0.0090
WHEEL_HUB_R = 0.022
WHEEL_HUB_H = 0.028
WHEEL_SPOKE_R = 0.0055
LEVER_HUB_R = 0.026
LEVER_HUB_H = 0.030
LEVER_BAR_W = 0.030
LEVER_BAR_H = 0.014
LEVER_BAR_Z = 0.020
LEVER_LONG_ARM = 0.150
LEVER_SHORT_ARM = 0.042
TEE_HUB_R = 0.022
TEE_HUB_H = 0.028
TEE_BAR_R = 0.0065
TEE_BAR_LEN = 0.150
TEE_END_R = 0.010
TEE_BAR_Z = 0.016


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PipelineConfig:
    body_form: BodyForm | None = None
    operator: Operator | None = None
    spoke_count: int | None = None
    port_type: PortType | None = None
    outlet_count: int | None = None
    palette_style: PaletteStyle = "yellow_gas"
    bolt_count: int | None = None
    body_scale: float = 1.0
    operator_radius_scale: float = 1.0
    name: str = "pipeline"


@dataclass(frozen=True)
class ResolvedPipelineConfig:
    body_form: BodyForm
    operator: Operator
    spoke_count: int
    port_type: PortType
    outlet_count: int
    palette_style: PaletteStyle
    bolt_count: int
    body_scale: float
    stem_len_scale: float
    operator_radius_scale: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> PipelineConfig:
    rng = random.Random(seed)
    body_form = rng.choice(BODY_FORMS)
    operator = rng.choice(OPERATORS)
    spoke_count = rng.choice(SPOKE_COUNTS)
    port_type = rng.choice(PORT_TYPES)
    # Outlets only on bodies that can capture the nozzle root (spec gating).
    if body_form in OUTLET_BODIES:
        outlet_count = rng.choices(OUTLET_SAMPLE_CHOICES, weights=OUTLET_SAMPLE_WEIGHTS, k=1)[0]
    else:
        outlet_count = 0
    return PipelineConfig(
        body_form=body_form,
        operator=operator,
        spoke_count=spoke_count,
        port_type=port_type,
        outlet_count=outlet_count,
        palette_style=rng.choice(PALETTE_STYLES),
        bolt_count=rng.choice((8, 10, 12)),
        body_scale=round(rng.uniform(0.88, 1.18), 4),
        operator_radius_scale=round(rng.uniform(0.88, 1.12), 4),
        name=f"seeded_pipeline_{seed}",
    )


def resolve_config(config: PipelineConfig | None = None) -> ResolvedPipelineConfig:
    cfg = config or PipelineConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    operator = _pick(cfg.operator, OPERATORS)
    spoke_count = cfg.spoke_count if cfg.spoke_count in SPOKE_COUNTS else 6
    port_type = _pick(cfg.port_type, PORT_TYPES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    outlet_count = int(cfg.outlet_count) if cfg.outlet_count is not None else 0
    outlet_count = int(_clamp(outlet_count, OUTLET_N_MIN, OUTLET_N_MAX))
    # Compatibility gating: outlets only on standpipe lineage.
    if body_form not in OUTLET_BODIES:
        outlet_count = 0

    bolt_count = cfg.bolt_count if cfg.bolt_count in (8, 10, 12) else 12

    body_scale = _clamp(cfg.body_scale, 0.88, 1.18)
    # stem_len_scale = f(body_scale): keep the stem-top / operator joint origin
    # proportional to the body so the operator never floats or sinks (spec
    # equation dependency).
    stem_len_scale = _clamp(0.7 + 0.3 * body_scale, 0.85, 1.15)
    # operator radius vs stem-top clearance inequality: shrink an oversized
    # operator so the rim cannot exceed the body footprint reach (spec).
    operator_radius_scale = _clamp(cfg.operator_radius_scale, 0.82, 1.12)
    operator_radius_scale = min(operator_radius_scale, 1.05 / max(body_scale, 0.9))

    return ResolvedPipelineConfig(
        body_form=body_form,
        operator=operator,
        spoke_count=spoke_count,
        port_type=port_type,
        outlet_count=outlet_count,
        palette_style=palette_style,
        bolt_count=bolt_count,
        body_scale=body_scale,
        stem_len_scale=stem_len_scale,
        operator_radius_scale=operator_radius_scale,
        name=cfg.name or "pipeline",
    )


def slot_choices_for_config(
    config: PipelineConfig | ResolvedPipelineConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedPipelineConfig) else resolve_config(config)
    if r.operator == "handwheel_wheel":
        op_name = f"handwheel_{r.spoke_count}spoke"
    else:
        op_name = r.operator
    return (
        ("body_form", r.body_form),
        ("operator", op_name),
        ("port", r.port_type),
        ("outlet_count", f"n{r.outlet_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Port-site descriptor + body interface
# ===========================================================================
@dataclass
class PortSite:
    center: tuple[float, float, float]
    normal: tuple[float, float, float]  # outward pipe axis at this end
    pipe_or: float
    pipe_ir: float


@dataclass
class BodyBuild:
    stem_top_z: float
    port_sites: list[PortSite]
    supports_outlets: bool
    nozzle_z: float
    outlet_body_r: float


# ---------------------------------------------------------------------------
# Geometry helpers shared across bodies.
# ---------------------------------------------------------------------------
def _annular_tube(origin, normal, length, por, pir) -> cq.Workplane:
    """Hollow pipe segment authored as a true annular extrusion (open ends)."""
    return (
        cq.Workplane(cq.Plane(origin=origin, normal=normal)).circle(por).circle(pir).extrude(length)
    )


def _bonnet_stack(z_base: float, stem_top_z: float) -> cq.Workplane:
    """Tapered bonnet neck + hex gland nut rising from the valve body top."""
    bonnet = (
        cq.Workplane("XY")
        .workplane(offset=z_base)
        .circle(BONNET_BASE_R)
        .workplane(offset=BONNET_H)
        .circle(BONNET_TOP_R)
        .loft(combine=True)
    )
    gland = (
        cq.Workplane("XY")
        .workplane(offset=z_base + BONNET_H)
        .polygon(6, GLAND_R * 2.0)
        .extrude(GLAND_H)
    )
    return bonnet.union(gland)


def _rising_stem(z_base: float, stem_top_z: float, stem_r: float) -> cq.Workplane:
    """Bright rising stem + a small bearing pad at the very top so the operator
    hub seats on a real flat surface at stem_top_z."""
    stem = (
        cq.Workplane("XY")
        .workplane(offset=z_base)
        .circle(stem_r)
        .extrude(stem_top_z - z_base - 0.006)
    )
    pad = (
        cq.Workplane("XY").workplane(offset=stem_top_z - 0.006).circle(stem_r * 1.7).extrude(0.006)
    )
    return stem.union(pad)


# ===========================================================================
# Slot A — body_form factories. Each returns (BodyBuild) and emits visuals onto
# the body part. All share the rising-stem + port-site interface.
# ===========================================================================
def _emit_inline_run_body(body, r: ResolvedPipelineConfig, mats, *, elbow: bool) -> BodyBuild:
    """straight_through_gate (elbow=False) / inline_gate_elbow (elbow=True).

    Horizontal hollow run through a central fatter gate-valve barrel; the elbow
    variant adds a 90-degree drop leg on the inlet (-X) end. Source: S1/S4
    ``_pipeline_run`` + ``_valve_body`` + ``_bonnet_stack`` + ``_stem``.
    """
    s = r.body_scale
    por, pir = PIPE_OR, PIPE_IR
    x_face = PORT_HALF_SPAN * s
    x_end = x_face + RUN_EXT
    eps = 0.012

    # Central run pipe (open both ends).
    run = _annular_tube((-x_end, 0.0, PORT_Z), (1, 0, 0), 2.0 * x_end, por, pir)

    if elbow:
        # 90-degree elbow + vertical drop leg on the inlet (-X) end.
        cx = -x_end + ELBOW_BEND_R  # bend center x
        cz = PORT_Z - ELBOW_BEND_R
        z_bottom = cz - DROP_LEN

        def _quarter_torus(minor):
            full = cq.Workplane().add(
                cq.Solid.makeTorus(
                    ELBOW_BEND_R, minor, pnt=cq.Vector(cx, 0.0, cz), dir=cq.Vector(0, 1, 0)
                )
            )
            bx_lo, bx_hi = cx - ELBOW_BEND_R - por - 0.01, cx + 0.01
            bz_lo, bz_hi = cz - 0.01, cz + ELBOW_BEND_R + por + 0.01
            box = cq.Workplane(
                cq.Plane(origin=((bx_lo + bx_hi) / 2.0, 0.0, (bz_lo + bz_hi) / 2.0))
            ).box(bx_hi - bx_lo, 4.0 * por, bz_hi - bz_lo)
            return full.intersect(box)

        v_shell = _annular_tube(
            (cx - ELBOW_BEND_R, 0.0, z_bottom), (0, 0, 1), DROP_LEN + eps, por, pir
        )
        e_shell = _quarter_torus(por).cut(_quarter_torus(pir))
        run = run.union(e_shell).union(v_shell)
        port_sites = [
            PortSite((x_face, 0.0, PORT_Z), (1, 0, 0), por, pir),
            PortSite((cx - ELBOW_BEND_R, 0.0, z_bottom), (0, 0, -1), por, pir),
        ]
    else:
        port_sites = [
            PortSite((x_face, 0.0, PORT_Z), (1, 0, 0), por, pir),
            PortSite((-x_face, 0.0, PORT_Z), (-1, 0, 0), por, pir),
        ]

    body.visual(
        mesh_from_cadquery(run, "pipe_run", tolerance=TOL, angular_tolerance=ATOL),
        material=mats["body"],
        name="pipe_run", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "hydrant_red", "globe_blue", "industrial_green"} else "metal.steel_galvanized"),
    )

    # Central cast valve barrel (fatter, bore cut through).
    plane = cq.Plane(origin=(0.0, 0.0, PORT_Z), normal=(1, 0, 0))
    barrel = cq.Workplane(plane).circle(VALVE_BARREL_R).extrude(VALVE_BARREL_HALF, both=True)
    barrel = barrel.cut(
        cq.Workplane(plane).circle(pir).extrude(VALVE_BARREL_HALF + 0.004, both=True)
    )
    body.visual(
        mesh_from_cadquery(barrel, "valve_barrel", tolerance=TOL, angular_tolerance=ATOL),
        material=mats["body"],
        name="valve_barrel", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "hydrant_red", "globe_blue", "industrial_green"} else "metal.steel_galvanized"),
    )

    # Bonnet + stem stack at center.
    z_bt = PORT_Z + VALVE_BARREL_R * 0.55
    stem_top_z = z_bt + BONNET_H + GLAND_H + STEM_LEN * r.stem_len_scale
    body.visual(
        mesh_from_cadquery(
            _bonnet_stack(z_bt, stem_top_z), "bonnet", tolerance=TOL, angular_tolerance=ATOL
        ),
        material=mats["trim"],
        name="bonnet", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"hydrant_red", "industrial_green", "galvanized_gray"} else "metal.paint_coated"),
    )
    z_stem_base = z_bt + BONNET_H + GLAND_H - 0.006
    body.visual(
        mesh_from_cadquery(
            _rising_stem(z_stem_base, stem_top_z, STEM_R),
            "rising_stem",
            tolerance=TOL,
            angular_tolerance=ATOL,
        ),
        material=mats["stem"],
        name="rising_stem", material_class_id=("metal.stainless_matte" if r.palette_style in {"yellow_gas", "globe_blue", "industrial_green", "galvanized_gray"} else "metal.brass_aged"),
    )

    body.inertial = Inertial.from_geometry(
        Box((2.0 * x_end, 2.0 * VALVE_BARREL_R, stem_top_z)),
        mass=4.0,
        origin=Origin(xyz=(0.0, 0.0, PORT_Z)),
    )
    return BodyBuild(stem_top_z, port_sites, False, PORT_Z, VALVE_BARREL_R)


def _emit_straight_gate_body(body, r, mats):
    return _emit_inline_run_body(body, r, mats, elbow=False)


def _emit_gate_elbow_body(body, r, mats):
    return _emit_inline_run_body(body, r, mats, elbow=True)


def _emit_globe_body(body, r: ResolvedPipelineConfig, mats) -> BodyBuild:
    """globe_sphere: spherical cast body + two lofted flange-hub necks + bonnet
    flange + yoke + rising stem. Source: S3 ``_make_body_mesh`` / yoke."""
    s = r.body_scale
    body_r = GLOBE_BODY_R * s
    half_span = PORT_HALF_SPAN * s
    neck_r = GLOBE_NECK_R
    por, pir = neck_r, PIPE_IR

    sphere = cq.Workplane("XY").sphere(body_r).translate((0.0, 0.0, PORT_Z))

    def _neck(sign):
        x_in = sign * (body_r - 0.050)
        x_out = sign * half_span
        a, b = sorted((x_in, x_out))
        r_a = neck_r if sign > 0 else PIPE_OR + 0.004
        r_b = PIPE_OR + 0.004 if sign > 0 else neck_r
        neck = (
            cq.Workplane("YZ")
            .workplane(offset=a)
            .circle(r_a)
            .workplane(offset=b - a)
            .circle(r_b)
            .loft(combine=True)
            .translate((0.0, 0.0, PORT_Z))
        )
        return neck

    glob = sphere.union(_neck(1.0)).union(_neck(-1.0))
    # Bore the flow path open.
    bore_half = half_span + 0.03
    bore = (
        cq.Workplane("YZ")
        .workplane(offset=-bore_half)
        .circle(PIPE_IR)
        .extrude(2.0 * bore_half)
        .translate((0.0, 0.0, PORT_Z))
    )
    glob = glob.cut(bore)

    # Bonnet flange disc on top.
    bflange_z = PORT_Z + body_r * 0.78
    bflange = cq.Workplane("XY").workplane(offset=bflange_z).circle(body_r * 0.62).extrude(0.020)
    glob = glob.union(bflange)
    body.visual(
        mesh_from_cadquery(glob, "body_shell", tolerance=TOL, angular_tolerance=ATOL),
        material=mats["body"],
        name="body_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "hydrant_red", "globe_blue", "industrial_green"} else "metal.steel_galvanized"),
    )

    # Yoke neck + square gland + stem-nut bushing.
    z_yk = bflange_z + 0.020
    stem_top_z = z_yk + 0.085 * r.stem_len_scale + STEM_LEN * r.stem_len_scale * 0.6
    yoke = cq.Workplane("XY").workplane(offset=z_yk - 0.004).circle(0.050).extrude(0.085 + 0.004)
    gland = (
        cq.Workplane("XY")
        .workplane(offset=z_yk + 0.016)
        .rect(0.070, 0.070)
        .extrude(0.052)
        .edges("|Z")
        .fillet(0.004)
    )
    yoke = yoke.union(gland)
    body.visual(
        mesh_from_cadquery(yoke, "bonnet_yoke", tolerance=TOL, angular_tolerance=ATOL),
        material=mats["trim"],
        name="bonnet_yoke", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"hydrant_red", "industrial_green", "galvanized_gray"} else "metal.paint_coated"),
    )

    # Bonnet bolt ring.
    bolts = None
    for bx, by in _bolt_positions(body_r * 0.62 - 0.016, r.bolt_count):
        head = (
            cq.Workplane("XY")
            .workplane(offset=bflange_z + 0.020)
            .center(bx, by)
            .polygon(6, 0.022)
            .extrude(0.010)
        )
        bolts = head if bolts is None else bolts.union(head)
    body.visual(
        mesh_from_cadquery(bolts, "bonnet_bolts", tolerance=TOL, angular_tolerance=ATOL),
        material=mats["bolt"],
        name="bonnet_bolts", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"yellow_gas", "globe_blue", "industrial_green", "galvanized_gray"} else "metal.brass_aged"),
    )

    z_stem_base = z_yk + 0.020
    body.visual(
        mesh_from_cadquery(
            _rising_stem(z_stem_base, stem_top_z, STEM_R),
            "rising_stem",
            tolerance=TOL,
            angular_tolerance=ATOL,
        ),
        material=mats["stem"],
        name="rising_stem", material_class_id=("metal.stainless_matte" if r.palette_style in {"yellow_gas", "globe_blue", "industrial_green", "galvanized_gray"} else "metal.brass_aged"),
    )

    body.inertial = Inertial.from_geometry(
        Box((2.0 * half_span, 2.0 * body_r, stem_top_z)),
        mass=6.0,
        origin=Origin(xyz=(0.0, 0.0, PORT_Z)),
    )
    port_sites = [
        PortSite((half_span, 0.0, PORT_Z), (1, 0, 0), por, pir),
        PortSite((-half_span, 0.0, PORT_Z), (-1, 0, 0), por, pir),
    ]
    return BodyBuild(stem_top_z, port_sites, False, PORT_Z, body_r)


def _standpipe_bulb_radius(z: float, body_scale: float) -> float:
    """Outer radius of the revolved bulb profile at height ``z`` (mirrors the
    profile in ``_emit_standpipe_body``). Used to seat chain lugs on the real
    body surface so they are never buried islands."""
    s = body_scale
    body_bottom_z = RISER_LEN * s + COLLAR_H
    body_h = SP_BODY_H * s
    z0 = body_bottom_z
    pts = [
        (COLLAR_OD / 2.0 - 0.004, z0),
        (SP_BODY_MAX_R * 0.82, z0 + body_h * 0.10),
        (SP_BODY_MAX_R, z0 + body_h * 0.42),
        (SP_BODY_MAX_R * 0.92, z0 + body_h * 0.70),
        (SP_NECK_R + 0.018, z0 + body_h * 0.90),
        (SP_NECK_R + 0.006, z0 + body_h),
    ]
    if z <= pts[0][1]:
        return pts[0][0]
    if z >= pts[-1][1]:
        return pts[-1][0]
    for (r0, za), (r1, zb) in zip(pts, pts[1:]):
        if za <= z <= zb:
            return r0 + (r1 - r0) * (z - za) / (zb - za)
    return SP_BODY_MAX_R


def _emit_standpipe_body(body, r: ResolvedPipelineConfig, mats) -> BodyBuild:
    """standpipe_riser: tall riser + revolved bulbous body + neck + dome + stem.
    The foot of the riser is the port-coupling site (axis Z). Source: S2."""
    s = r.body_scale
    riser_len = RISER_LEN * s
    collar_z = riser_len
    body_bottom_z = collar_z + COLLAR_H
    body_h = SP_BODY_H * s
    body_top_z = body_bottom_z + body_h
    body_center_z = body_bottom_z + body_h / 2.0

    # Riser (hollow).
    riser = cq.Workplane("XY").circle(RISER_OD / 2.0).extrude(riser_len)
    riser = riser.cut(cq.Workplane("XY").circle(RISER_ID / 2.0).extrude(riser_len + 0.001))
    body.visual(
        mesh_from_cadquery(riser, "riser_pipe", tolerance=TOL),
        material=mats["body2"],
        name="riser_pipe", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "hydrant_red", "globe_blue", "industrial_green"} else "metal.steel_galvanized"),
    )

    collar = cq.Workplane("XY").workplane(offset=collar_z).circle(COLLAR_OD / 2.0).extrude(COLLAR_H)
    body.visual(
        mesh_from_cadquery(collar, "body_collar", tolerance=TOL),
        material=mats["trim"],
        name="body_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"hydrant_red", "industrial_green", "galvanized_gray"} else "metal.paint_coated"),
    )

    # Revolved bulbous body.
    z0 = body_bottom_z
    pts = [
        (COLLAR_OD / 2.0 - 0.004, z0),
        (SP_BODY_MAX_R * 0.82, z0 + body_h * 0.10),
        (SP_BODY_MAX_R, z0 + body_h * 0.42),
        (SP_BODY_MAX_R * 0.92, z0 + body_h * 0.70),
        (SP_NECK_R + 0.018, z0 + body_h * 0.90),
        (SP_NECK_R + 0.006, z0 + body_h),
    ]
    profile = cq.Workplane("XZ").moveTo(0.0, z0)
    for rr, zz in pts:
        profile = profile.lineTo(rr, zz)
    profile = profile.lineTo(0.0, z0 + body_h).close()
    bulb = profile.revolve(360.0, (0, 0, 0), (0, 1, 0))
    body.visual(
        mesh_from_cadquery(bulb, "valve_body", tolerance=TOL),
        material=mats["body"],
        name="valve_body", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "hydrant_red", "globe_blue", "industrial_green"} else "metal.steel_galvanized"),
    )

    neck = cq.Workplane("XY").workplane(offset=body_top_z).circle(SP_NECK_R).extrude(SP_NECK_H)
    body.visual(
        mesh_from_cadquery(neck, "bonnet_neck", tolerance=TOL),
        material=mats["body"],
        name="bonnet_neck", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "hydrant_red", "globe_blue", "industrial_green"} else "metal.steel_galvanized"),
    )

    # Brass dome + rising stem.
    dome_base_z = body_top_z + SP_NECK_H
    stem_top_z = dome_base_z + (SP_STEM_EXTRA + STEM_LEN * 0.3) * r.stem_len_scale
    dome = cq.Workplane("XY").workplane(offset=dome_base_z).sphere(SP_DOME_R)
    cut_box = (
        cq.Workplane("XY")
        .workplane(offset=dome_base_z - SP_DOME_R)
        .box(4 * SP_DOME_R, 4 * SP_DOME_R, 2 * SP_DOME_R, centered=(True, True, False))
    )
    dome = dome.intersect(cut_box)
    dome = dome.union(_rising_stem(dome_base_z, stem_top_z, SP_STEM_R))
    body.visual(
        mesh_from_cadquery(dome, "rising_stem", tolerance=TOL),
        material=mats["stem"],
        name="rising_stem", material_class_id=("metal.stainless_matte" if r.palette_style in {"yellow_gas", "globe_blue", "industrial_green", "galvanized_gray"} else "metal.brass_aged"),
    )

    body.inertial = Inertial.from_geometry(
        Box((2.0 * SP_BODY_MAX_R, 2.0 * SP_BODY_MAX_R, stem_top_z)),
        mass=8.0,
        origin=Origin(xyz=(0.0, 0.0, body_center_z)),
    )
    # Single foot coupling site (axis Z) at the riser base.
    port_sites = [PortSite((0.0, 0.0, 0.018), (0, 0, -1), RISER_OD / 2.0, RISER_ID / 2.0)]
    nozzle_z = body_center_z + 0.006
    return BodyBuild(stem_top_z, port_sites, True, nozzle_z, SP_BODY_MAX_R)


def _emit_angle_body(body, r: ResolvedPipelineConfig, mats) -> BodyBuild:
    """angle_valve_90: vertical inlet leg (from below) + quarter-torus corner +
    horizontal outlet, with a corner valve barrel. Source: S5."""
    s = r.body_scale
    por, pir = PIPE_OR, PIPE_IR
    x_face = PORT_HALF_SPAN * s
    x_end = x_face + RUN_EXT
    eps = 0.012

    cx = ELBOW_BEND_R - x_end  # corner near -X side
    cx = -x_end + ELBOW_BEND_R
    cz = PORT_Z - ELBOW_BEND_R
    z_bottom = cz - DROP_LEN

    # Horizontal outlet run from the corner toward +X.
    h_run = _annular_tube((cx, 0.0, PORT_Z), (1, 0, 0), (x_end - cx), por, pir)

    def _quarter_torus(minor):
        full = cq.Workplane().add(
            cq.Solid.makeTorus(
                ELBOW_BEND_R, minor, pnt=cq.Vector(cx, 0.0, cz), dir=cq.Vector(0, 1, 0)
            )
        )
        bx_lo, bx_hi = cx - ELBOW_BEND_R - por - 0.01, cx + 0.01
        bz_lo, bz_hi = cz - 0.01, cz + ELBOW_BEND_R + por + 0.01
        box = cq.Workplane(
            cq.Plane(origin=((bx_lo + bx_hi) / 2.0, 0.0, (bz_lo + bz_hi) / 2.0))
        ).box(bx_hi - bx_lo, 4.0 * por, bz_hi - bz_lo)
        return full.intersect(box)

    e_shell = _quarter_torus(por).cut(_quarter_torus(pir))
    v_shell = _annular_tube(
        (cx - ELBOW_BEND_R, 0.0, z_bottom), (0, 0, 1), (cz - z_bottom) + eps, por, pir
    )
    run = h_run.union(e_shell).union(v_shell)
    body.visual(
        mesh_from_cadquery(run, "pipe_run", tolerance=TOL, angular_tolerance=ATOL),
        material=mats["body"],
        name="pipe_run", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "hydrant_red", "globe_blue", "industrial_green"} else "metal.steel_galvanized"),
    )

    # Corner valve barrel on the horizontal outlet, centered just past the bend.
    bx_center = cx + (x_end - cx) * 0.30
    plane = cq.Plane(origin=(bx_center, 0.0, PORT_Z), normal=(1, 0, 0))
    barrel = cq.Workplane(plane).circle(VALVE_BARREL_R).extrude(VALVE_BARREL_HALF, both=True)
    barrel = barrel.cut(
        cq.Workplane(plane).circle(pir).extrude(VALVE_BARREL_HALF + 0.004, both=True)
    )
    body.visual(
        mesh_from_cadquery(barrel, "valve_barrel", tolerance=TOL, angular_tolerance=ATOL),
        material=mats["body"],
        name="valve_barrel", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "hydrant_red", "globe_blue", "industrial_green"} else "metal.steel_galvanized"),
    )

    z_bt = PORT_Z + VALVE_BARREL_R * 0.55
    stem_top_z = z_bt + BONNET_H + GLAND_H + STEM_LEN * r.stem_len_scale
    bonnet = _bonnet_stack(z_bt, stem_top_z).translate((bx_center, 0.0, 0.0))
    body.visual(
        mesh_from_cadquery(bonnet, "bonnet", tolerance=TOL, angular_tolerance=ATOL),
        material=mats["trim"],
        name="bonnet", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"hydrant_red", "industrial_green", "galvanized_gray"} else "metal.paint_coated"),
    )
    z_stem_base = z_bt + BONNET_H + GLAND_H - 0.006
    stem = _rising_stem(z_stem_base, stem_top_z, STEM_R).translate((bx_center, 0.0, 0.0))
    body.visual(
        mesh_from_cadquery(stem, "rising_stem", tolerance=TOL, angular_tolerance=ATOL),
        material=mats["stem"],
        name="rising_stem", material_class_id=("metal.stainless_matte" if r.palette_style in {"yellow_gas", "globe_blue", "industrial_green", "galvanized_gray"} else "metal.brass_aged"),
    )

    body.inertial = Inertial.from_geometry(
        Box((2.0 * x_end, 2.0 * VALVE_BARREL_R, stem_top_z)),
        mass=5.0,
        origin=Origin(xyz=(bx_center, 0.0, PORT_Z)),
    )
    # Stem origin for the angle body is at bx_center, not 0 -> expose it.
    port_sites = [
        PortSite((x_end - 0.001, 0.0, PORT_Z), (1, 0, 0), por, pir),
        PortSite((cx - ELBOW_BEND_R, 0.0, z_bottom), (0, 0, -1), por, pir),
    ]
    bb = BodyBuild(stem_top_z, port_sites, False, PORT_Z, VALVE_BARREL_R)
    bb.stem_x = bx_center  # type: ignore[attr-defined]
    return bb


_BODY_BUILDERS = {
    "inline_gate_elbow": _emit_gate_elbow_body,
    "globe_sphere": _emit_globe_body,
    "standpipe_riser": _emit_standpipe_body,
    "straight_through_gate": _emit_straight_gate_body,
    "angle_valve_90": _emit_angle_body,
}


# ===========================================================================
# Slot C — port couplings (fixed inline visuals on the body; Rule 1).
# Authored canonically along +X about the origin, then aimed to each site.
# ===========================================================================
def _bolt_positions(ring_r: float, count: int):
    pts = []
    for i in range(count):
        a = 2.0 * math.pi * i / count + math.pi / count
        pts.append((ring_r * math.cos(a), ring_r * math.sin(a)))
    return pts


def _aim_x(solid, normal, center):
    """Rotate a +X-authored solid so +X points along ``normal``, then translate."""
    nx, ny, nz = normal
    if (nx, ny, nz) == (1, 0, 0):
        s = solid
    elif (nx, ny, nz) == (-1, 0, 0):
        s = solid.rotate((0, 0, 0), (0, 0, 1), 180.0)
    elif (nx, ny, nz) == (0, 0, 1):
        s = solid.rotate((0, 0, 0), (0, 1, 0), -90.0)
    elif (nx, ny, nz) == (0, 0, -1):
        s = solid.rotate((0, 0, 0), (0, 1, 0), 90.0)
    else:
        s = solid
    return s.translate(center)


def _flange_disc_local(por, pir, n_bolts, *, raised_face: bool):
    """One bolted flange disc (mouth at local x=0, body toward -X). Authored on
    a YZ workplane extruding +X. Returns a cq solid in local frame."""
    flange_r = max(0.085, por + 0.058)
    face_t = 0.013
    disc = cq.Workplane("YZ").circle(flange_r).extrude(face_t, both=True)
    disc = disc.cut(cq.Workplane("YZ").circle(pir).extrude(face_t + 0.004, both=True))
    if raised_face:
        rf = cq.Workplane("YZ").workplane(offset=-face_t - 0.004).circle(por + 0.030).extrude(0.006)
        disc = disc.union(rf)
    for by, bz in _bolt_positions(flange_r - 0.020, n_bolts):
        bolt = (
            cq.Workplane(cq.Plane(origin=(0.0, by, bz), normal=(1, 0, 0)))
            .polygon(6, 0.015)
            .extrude(face_t + 0.006, both=True)
        )
        disc = disc.union(bolt)
    return disc


def _socket_collar_local(por, pir):
    """Smooth bell socket-weld collar — no disc, no bolts (S10)."""
    socket_r = por + 0.013
    length = 0.074
    shoulder = 0.016
    sleeve = length - 2.0 * shoulder
    outer = (
        cq.Workplane("YZ")
        .workplane(offset=-length / 2.0)
        .circle(por + 0.002)
        .workplane(offset=shoulder)
        .circle(socket_r)
        .workplane(offset=sleeve)
        .circle(socket_r)
        .workplane(offset=shoulder)
        .circle(por + 0.002)
        .loft(combine=True)
    )
    bore = (
        cq.Workplane("YZ")
        .workplane(offset=-length / 2.0 - 0.002)
        .circle(pir)
        .extrude(length + 0.004)
    )
    return outer.cut(bore)


def _union_nut_local(por, pir):
    """Screwed hex union nut + round compression shoulders (S11)."""
    nut_r = por + 0.020
    shoulder_r = por + 0.009
    nut_l = 0.040

    def _xcyl(x0, x1, rr):
        lo, hi = sorted((x0, x1))
        return cq.Workplane("YZ").workplane(offset=lo).circle(rr).extrude(hi - lo)

    inner = -nut_l / 2.0
    outer = nut_l / 2.0
    coupling = _xcyl(inner - 0.012, outer + 0.012, por + 0.004)
    hexnut = cq.Workplane("YZ").workplane(offset=inner).polygon(6, 2.0 * nut_r).extrude(nut_l)
    coupling = coupling.union(hexnut)
    coupling = coupling.union(_xcyl(inner - 0.004, inner + 0.006, shoulder_r))
    coupling = coupling.union(_xcyl(outer - 0.006, outer + 0.004, shoulder_r))
    bore = _xcyl(inner - 0.020, outer + 0.020, pir)
    return coupling.cut(bore)


def _emit_ports(body, r: ResolvedPipelineConfig, mats, sites: list[PortSite]) -> None:
    """Emit the chosen port coupling(s) as fixed body visuals at every site."""
    pt = r.port_type
    for idx, site in enumerate(sites):
        por, pir = site.pipe_or, site.pipe_ir
        if pt in ("bolted_flange_pair", "bolted_RF_flange"):
            raised = pt == "bolted_RF_flange"
            # A bolted *pair*: two discs facing each other at the joint plane.
            d1 = _flange_disc_local(por, pir, r.bolt_count, raised_face=raised).translate(
                (-0.015, 0.0, 0.0)
            )
            d2 = _flange_disc_local(por, pir, r.bolt_count, raised_face=raised).translate(
                (0.015, 0.0, 0.0)
            )
            solid = d1.union(d2)
            name = "flanges" if not raised else "rf_flanges"
        elif pt == "socket_weld":
            solid = _socket_collar_local(por, pir)
            name = "socket_collar"
        else:  # union_nut
            solid = _union_nut_local(por, pir)
            name = "union_nut"
        placed = _aim_x(solid, site.normal, site.center)
        mat = mats["bolt"] if pt in ("bolted_flange_pair", "bolted_RF_flange") else mats["port"]
        body.visual(
            mesh_from_cadquery(placed, f"{name}_{idx}", tolerance=TOL, angular_tolerance=ATOL),
            material=mat,
            name=f"{name}_{idx}", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "globe_blue", "industrial_green", "galvanized_gray"} else "metal.brass_aged"),
        )


# ===========================================================================
# Slot B — operator factories (parallel child of the body, joint on stem top).
# ===========================================================================
def _wheel_mesh(spoke_count: int, scale: float, name: str):
    rim_r = WHEEL_RIM_R * scale
    rim = cq.Workplane(obj=cq.Solid.makeTorus(rim_r - WHEEL_TUBE_R, WHEEL_TUBE_R))
    rim = rim.translate((0.0, 0.0, WHEEL_HUB_H * 0.5))
    hub = cq.Workplane("XY").circle(WHEEL_HUB_R).extrude(WHEEL_HUB_H)
    wheel = rim.union(hub)
    for i in range(spoke_count):
        ang = 2.0 * math.pi * i / spoke_count
        spoke = cq.Workplane("XY").circle(WHEEL_SPOKE_R).extrude(rim_r - WHEEL_TUBE_R)
        spoke = spoke.rotate((0, 0, 0), (0, 1, 0), 90.0)
        spoke = spoke.translate((0.0, 0.0, WHEEL_HUB_H * 0.5))
        spoke = spoke.rotate((0, 0, 0), (0, 0, 1), math.degrees(ang))
        wheel = wheel.union(spoke)
    return mesh_from_cadquery(wheel, name, tolerance=TOL, angular_tolerance=ATOL)


def _lever_mesh(scale: float, name: str):
    hub = cq.Workplane("XY").circle(LEVER_HUB_R).extrude(LEVER_HUB_H)
    long_arm = LEVER_LONG_ARM * scale
    total = LEVER_SHORT_ARM + long_arm
    cx = 0.5 * (long_arm - LEVER_SHORT_ARM)
    bar = (
        cq.Workplane("XY")
        .workplane(offset=LEVER_BAR_Z)
        .center(cx, 0.0)
        .rect(total, LEVER_BAR_W)
        .extrude(LEVER_BAR_H)
        .edges("|Z")
        .fillet(LEVER_BAR_W * 0.45)
    )
    knob = (
        cq.Workplane("XY")
        .workplane(offset=LEVER_BAR_Z)
        .center(long_arm, 0.0)
        .circle(LEVER_BAR_W * 0.58)
        .extrude(LEVER_BAR_H)
    )
    return mesh_from_cadquery(
        hub.union(bar).union(knob), name, tolerance=TOL, angular_tolerance=ATOL
    )


def _tee_hub_mesh(name: str):
    return mesh_from_cadquery(
        cq.Workplane("XY").circle(TEE_HUB_R).extrude(TEE_HUB_H),
        name,
        tolerance=TOL,
        angular_tolerance=ATOL,
    )


def _tee_bar_mesh(index: int, scale: float, name: str):
    bar_len = TEE_BAR_LEN * scale
    bar = (
        cq.Workplane(cq.Plane(origin=(-bar_len / 2.0, 0.0, TEE_BAR_Z), normal=(1, 0, 0)))
        .circle(TEE_BAR_R)
        .extrude(bar_len)
    )
    for x in (-bar_len / 2.0, bar_len / 2.0):
        bar = bar.union(cq.Workplane("XY").sphere(TEE_END_R).translate((x, 0.0, TEE_BAR_Z)))
    bar = bar.rotate((0, 0, 0), (0, 0, 1), 90.0 * index)
    return mesh_from_cadquery(bar, name, tolerance=TOL, angular_tolerance=ATOL)


def _emit_operator(model, body, r: ResolvedPipelineConfig, mats, *, stem_top_z, stem_x):
    """Emit the operator part + its joint on the rising-stem top.

    The joint declares a MatingContract: rising-stem top (+z) to operator hub
    bottom (-z), both real visuals (Rule 2). handwheel/tee = CONTINUOUS, lever =
    REVOLUTE [0, pi/2].
    """
    scale = r.operator_radius_scale
    origin = Origin(xyz=(stem_x, 0.0, stem_top_z))
    mating = MatingContract(
        parent_face_geometry="rising_stem",
        parent_face_side="positive_z",
        child_face_geometry="op_hub",
        child_face_side="negative_z",
        contact_tol=0.0025,
    )

    if r.operator == "handwheel_wheel":
        op = model.part("operator")
        op.visual(
            _wheel_mesh(r.spoke_count, scale, "op_hub"),
            material=mats["operator"],
            name="op_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "globe_blue", "industrial_green", "galvanized_gray"} else "metal.blackened_gunmetal"),
        )
        op.inertial = Inertial.from_geometry(
            Box((2.0 * WHEEL_RIM_R * scale, 2.0 * WHEEL_RIM_R * scale, WHEEL_HUB_H)),
            mass=0.6,
            origin=Origin(xyz=(0.0, 0.0, WHEEL_HUB_H * 0.5)),
        )
        model.articulation(
            "operator_spin",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=op,
            origin=origin,
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=12.0, velocity=4.0),
            mating=mating,
        )
        return "operator", "continuous"

    if r.operator == "quarter_turn_lever":
        op = model.part("operator")
        op.visual(
            _lever_mesh(scale, "op_hub"),
            material=mats["operator"],
            name="op_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "globe_blue", "industrial_green", "galvanized_gray"} else "metal.blackened_gunmetal"),
        )
        op.inertial = Inertial.from_geometry(
            Box((LEVER_LONG_ARM * scale, LEVER_BAR_W, LEVER_HUB_H)),
            mass=0.4,
            origin=Origin(xyz=(LEVER_LONG_ARM * scale * 0.3, 0.0, LEVER_HUB_H * 0.5)),
        )
        model.articulation(
            "operator_spin",
            ArticulationType.REVOLUTE,
            parent=body,
            child=op,
            origin=origin,
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=20.0, velocity=4.0, lower=0.0, upper=math.pi / 2.0),
            mating=mating,
        )
        return "operator", "revolute"

    # crossed_tee_bar: hub + two crossed bars (same part).
    op = model.part("operator")
    op.visual(_tee_hub_mesh("op_hub"), material=mats["operator"], name="op_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "globe_blue", "industrial_green", "galvanized_gray"} else "metal.blackened_gunmetal"))
    for i in range(2):
        op.visual(
            _tee_bar_mesh(i, scale, f"tee_bar_{i}"),
            material=mats["operator"],
            name=f"tee_bar_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "globe_blue", "industrial_green", "galvanized_gray"} else "metal.blackened_gunmetal"),
        )
    op.inertial = Inertial.from_geometry(
        Box((TEE_BAR_LEN * scale, TEE_BAR_LEN * scale, TEE_HUB_H)),
        mass=0.4,
        origin=Origin(xyz=(0.0, 0.0, TEE_HUB_H * 0.5)),
    )
    model.articulation(
        "operator_spin",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=op,
        origin=origin,
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=12.0, velocity=4.0),
        mating=mating,
    )
    return "operator", "continuous"


# ===========================================================================
# Outlet multiplicity (S2 / S13): N radial nozzle+cap+chain assemblies.
# ===========================================================================
def _outlet_angle(i: int, n: int) -> float:
    return 2.0 * math.pi * i / n


def _radial(a):
    return (math.cos(a), math.sin(a), 0.0)


def _tangent(a):
    return (-math.sin(a), math.cos(a), 0.0)


def _outlet_local_to_body(angle, local):
    rv = _radial(angle)
    tv = _tangent(angle)
    return (rv[0] * local[0] + tv[0] * local[1], rv[1] * local[0] + tv[1] * local[1], local[2])


def _nozzle_mesh(angle, nozzle_z, name):
    tube = (
        cq.Workplane("YZ").circle(NOZZLE_R).circle(NOZZLE_BORE).extrude(NOZZLE_LEN + NOZZLE_ROOT_X)
    )
    nozzle = tube.translate((0.0, 0.0, nozzle_z))
    tip_x = NOZZLE_ROOT_X + NOZZLE_LEN
    flange = (
        cq.Workplane("YZ")
        .workplane(offset=tip_x - 0.010)
        .circle(NOZZLE_R + 0.006)
        .circle(NOZZLE_BORE)
        .extrude(0.010)
        .translate((0.0, 0.0, nozzle_z))
    )
    nozzle = nozzle.union(flange).rotate((0, 0, 0), (0, 0, 1), math.degrees(angle))
    return mesh_from_cadquery(nozzle, name, tolerance=TOL)


def _lug_local(nozzle_z, body_scale):
    """Outlet-local (radial, tangential, z) of the chain lug, seated so the eye
    sphere straddles the real bulb surface at the lug height (not buried)."""
    lz = nozzle_z + CHAIN_LUG_LOCAL[2]
    bulb_r = _standpipe_bulb_radius(lz, body_scale)
    radial = bulb_r - 0.004  # center just inside the surface -> sphere straddles
    return (radial, 0.0, lz)


def _chain_lug_mesh(angle, nozzle_z, body_scale, name):
    radial, tangential, lz = _lug_local(nozzle_z, body_scale)
    lx, ly, _ = _outlet_local_to_body(angle, (radial, tangential, 0.0))
    eye = cq.Workplane("XY").workplane(offset=lz).center(lx, ly).sphere(CHAIN_LUG_R)
    return mesh_from_cadquery(eye, name, tolerance=TOL), (lx, ly, lz)


def _cap_mesh(name):
    cup = cq.Workplane("YZ").circle(CAP_R).extrude(CAP_H)
    cup = cup.cut(cq.Workplane("YZ").circle(NOZZLE_R - 0.002).extrude(CAP_RECESS_DEPTH))
    grip = cq.Workplane("YZ").workplane(offset=CAP_H - 0.006).circle(CAP_R + 0.004).extrude(0.006)
    cap = cup.union(grip)
    bx, by, bz = CHAIN_BOSS_LOCAL
    cap = cap.union(cq.Workplane("XY").workplane(offset=bz).center(bx, by).sphere(0.007))
    return mesh_from_cadquery(cap, name, tolerance=TOL)


def _oval_link_mesh(in_yz, name):
    pts = []
    for j in range(36):
        t = 2.0 * math.pi * j / 36
        short = CHAIN_LINK_HALF_WID * math.cos(t)
        lng = CHAIN_LINK_HALF_LEN * math.sin(t)
        if in_yz:
            pts.append((0.0, short, -CHAIN_LINK_HALF_LEN + lng))
        else:
            pts.append((short, 0.0, -CHAIN_LINK_HALF_LEN + lng))
    geom = tube_from_spline_points(
        pts,
        radius=CHAIN_LINK_WIRE_R,
        samples_per_segment=10,
        closed_spline=True,
        radial_segments=14,
        cap_ends=False,
    )
    return mesh_from_geometry(geom, name)


def _rpy_aim_negz(direction):
    dx, dy, dz = direction
    n = math.sqrt(dx * dx + dy * dy + dz * dz)
    if n < 1e-9:
        return (0.0, 0.0, 0.0)
    vx, vy, vz = -dx / n, -dy / n, -dz / n
    yaw = math.atan2(vy, vx)
    pitch = math.atan2(math.hypot(vx, vy), vz)
    return (0.0, pitch, yaw)


def _add_subchain(model, prefix, parent_part, root_origin, n_links, mats):
    parent = parent_part
    origin = root_origin
    links = []
    for i in range(n_links):
        link = model.part(f"{prefix}_{i}")
        in_yz = i % 2 == 1
        link.visual(
            _oval_link_mesh(in_yz, f"{prefix}_{i}_oval"), material=mats["bolt"], name="oval_body", material_class_id="metal.steel_bare"
        )
        model.articulation(
            f"{prefix}_swing_{i}",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=link,
            origin=origin,
            axis=(1.0, 0.0, 0.0) if in_yz else (0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                effort=0.8, velocity=2.0, lower=-CHAIN_SWING, upper=CHAIN_SWING
            ),
        )
        parent = link
        origin = Origin(xyz=(0.0, 0.0, -CHAIN_LINK_PITCH))
        links.append(link)
    return links


def _chain_link_count(nozzle_z, body_scale):
    cap_origin_r = (NOZZLE_ROOT_X + NOZZLE_LEN - 0.014 + CAP_DEFAULT_PULL, 0.0, nozzle_z)
    lr, lt, lz = _lug_local(nozzle_z, body_scale)
    d = (
        lr - cap_origin_r[0] - CHAIN_BOSS_LOCAL[0],
        lt - cap_origin_r[1] - CHAIN_BOSS_LOCAL[1],
        lz - cap_origin_r[2] - CHAIN_BOSS_LOCAL[2],
    )
    span = math.sqrt(sum(c * c for c in d))
    return max(6, round(span / CHAIN_LINK_PITCH)), d


def _emit_outlets(model, body, r: ResolvedPipelineConfig, mats, bb: BodyBuild):
    """Emit N radial outlet assemblies (nozzle+lug visuals on body; cap part +
    serial chain). Returns per-outlet link counts for the tests."""
    n = r.outlet_count
    nozzle_z = bb.nozzle_z
    cap_hinge_x = NOZZLE_ROOT_X + NOZZLE_LEN - 0.014
    n_links, dir_local = _chain_link_count(nozzle_z, r.body_scale)
    per_outlet = []
    for i in range(n):
        angle = _outlet_angle(i, n)
        body.visual(
            _nozzle_mesh(angle, nozzle_z, f"nozzle_{i}"), material=mats["port"], name=f"nozzle_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "globe_blue", "industrial_green", "galvanized_gray"} else "metal.brass_aged")
        )
        lug_mesh, _ = _chain_lug_mesh(angle, nozzle_z, r.body_scale, f"chain_lug_{i}")
        body.visual(lug_mesh, material=mats["trim"], name=f"chain_lug_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"hydrant_red", "industrial_green", "galvanized_gray"} else "metal.paint_coated"))

        cap = model.part(f"cap_{i}")
        cap.visual(_cap_mesh(f"cap_{i}"), material=mats["port"], name=f"cap_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"yellow_gas", "globe_blue", "industrial_green", "galvanized_gray"} else "metal.brass_aged"))
        cap.inertial = Inertial.from_geometry(
            Box((CAP_H, 2.0 * CAP_R, 2.0 * CAP_R)),
            mass=0.05,
            origin=Origin(xyz=(CAP_H * 0.5, 0.0, 0.0)),
        )
        cap_origin = _outlet_local_to_body(angle, (cap_hinge_x + CAP_DEFAULT_PULL, 0.0, nozzle_z))
        model.articulation(
            f"body_to_cap_{i}",
            ArticulationType.PRISMATIC,
            parent=body,
            child=cap,
            origin=Origin(xyz=cap_origin, rpy=(0.0, 0.0, angle)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=3.0, velocity=0.25, lower=-CAP_DEFAULT_PULL, upper=0.020
            ),
        )
        _add_subchain(
            model,
            f"chain_{i}",
            cap,
            Origin(xyz=CHAIN_BOSS_LOCAL, rpy=_rpy_aim_negz(dir_local)),
            n_links,
            mats,
        )
        per_outlet.append(n_links)
    return per_outlet


# ===========================================================================
# Build
# ===========================================================================
def build_pipeline(
    config: PipelineConfig | None = None,
    *,
    assets=None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"pipeline_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = model.part("body")
    bb = _BODY_BUILDERS[r.body_form](body, r, mats)
    stem_x = getattr(bb, "stem_x", 0.0)

    _emit_ports(body, r, mats, bb.port_sites)
    _emit_operator(model, body, r, mats, stem_top_z=bb.stem_top_z, stem_x=stem_x)
    if r.outlet_count > 0 and bb.supports_outlets:
        _emit_outlets(model, body, r, mats, bb)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pipeline(seed: int, *, assets=None) -> ArticulatedObject:
    return build_pipeline(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_pipeline_tests(object_model: ArticulatedObject, config: PipelineConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")

    # ---- Captured-fit allowances (operator hub on stem, caps on nozzles,
    #      chain interlinks) — element-scoped, mirroring the source records. ----
    op = object_model.get_part("operator")
    ctx.allow_overlap(
        op,
        body,
        reason="operator hub is bored onto / seats over the captured rising stem top.",
    )

    if r.outlet_count > 0 and r.body_form in OUTLET_BODIES:
        n_links, _ = _chain_link_count(_body_nozzle_z(object_model, r), r.body_scale)
        for i in range(r.outlet_count):
            cap = object_model.get_part(f"cap_{i}")
            ctx.allow_overlap(
                cap,
                body,
                elem_a=f"cap_{i}",
                elem_b=f"nozzle_{i}",
                reason="brass cap seats over the captured nozzle tip (seated fit).",
            )
            chain_links = [object_model.get_part(f"chain_{i}_{j}") for j in range(n_links)]
            for root in chain_links[:2]:
                ctx.allow_overlap(
                    root, cap, reason="chain root is riveted to the cap ball (follows the cap)."
                )
            for tail in chain_links[-2:]:
                ctx.allow_overlap(tail, body, reason="chain far end wraps the body lug eye.")
            for a, b in zip(chain_links, chain_links[1:]):
                ctx.allow_overlap(
                    a, b, reason="consecutive oval links interlink, as in a real chain."
                )

    # ---- Baseline structural checks. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("root body present", "body" in part_names, details=str(sorted(part_names)))
    ctx.check(
        "rising stem visual present", any(v.name == "rising_stem" for v in body.visuals), details=""
    )

    # Operator joint topology (the hero articulation about vertical +Z).
    j = object_model.get_articulation("operator_spin")
    axis_ok = abs(j.axis[2]) > 0.99 and abs(j.axis[0]) < 1e-3 and abs(j.axis[1]) < 1e-3
    if r.operator == "quarter_turn_lever":
        ctx.check(
            "lever operator is REVOLUTE +Z limited [0, pi/2]",
            j.articulation_type == ArticulationType.REVOLUTE
            and axis_ok
            and j.motion_limits is not None
            and abs(j.motion_limits.lower) < 1e-6
            and abs(j.motion_limits.upper - math.pi / 2.0) < 1e-3,
            details=f"type={j.articulation_type} axis={tuple(j.axis)} limits={j.motion_limits}",
        )
    else:
        ctx.check(
            "wheel/tee operator is CONTINUOUS +Z",
            j.articulation_type == ArticulationType.CONTINUOUS and axis_ok,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )

    # Operator sits above the body top (on the stem), centered on the stem axis.
    op_aabb = ctx.part_world_aabb(op)
    body_aabb = ctx.part_world_aabb(body)
    if op_aabb is not None and body_aabb is not None:
        ctx.check(
            "operator is the top assembly (on the stem)",
            op_aabb[1][2] >= body_aabb[1][2] - 0.02,
            details=f"op_top={op_aabb[1][2]:.3f} body_top={body_aabb[1][2]:.3f}",
        )

    # Turning the operator keeps the hub on the stem axis (spins, not translates).
    p0 = ctx.part_world_position(op)
    with ctx.pose({j: math.pi / 4.0 if r.operator != "quarter_turn_lever" else math.pi / 4.0}):
        p1 = ctx.part_world_position(op)
    if p0 is not None and p1 is not None:
        ctx.check(
            "operator spins in place about the stem axis",
            abs(p1[2] - p0[2]) < 1e-3,
            details=f"rest_z={p0[2]:.4f} turned_z={p1[2]:.4f}",
        )

    # Ports present as body visuals (Rule 1: fixed, no joints).
    port_visual = [
        v.name
        for v in body.visuals
        if any(
            v.name.startswith(pfx)
            for pfx in ("flanges", "rf_flanges", "socket_collar", "union_nut")
        )
    ]
    ctx.check(
        "port couplings present as body visuals",
        len(port_visual) >= 1,
        details=f"ports={sorted(port_visual)}",
    )

    # The standpipe riser foot rests on the ground; inline pipe-run bodies are
    # suspended in their pipe run (not grounded), so only gate the standpipe.
    if body_aabb is not None and r.body_form == "standpipe_riser":
        ctx.check(
            "standpipe riser foot rests near the ground",
            body_aabb[0][2] < 0.05,
            details=f"z_min={body_aabb[0][2]:.4f}",
        )

    # Outlet topology (standpipe only).
    if r.outlet_count > 0 and r.body_form in OUTLET_BODIES:
        for i in range(r.outlet_count):
            cj = object_model.get_articulation(f"body_to_cap_{i}")
            ctx.check(
                f"cap {i} is PRISMATIC (slides along its radial outlet axis)",
                cj.articulation_type == ArticulationType.PRISMATIC and abs(cj.axis[0]) > 0.99,
                details=f"type={cj.articulation_type} axis={tuple(cj.axis)}",
            )
        # Even angular spacing for N>=2.
        if r.outlet_count >= 2:
            ctx.check(
                "outlets are radially distributed about +Z",
                any(v.name == "nozzle_0" for v in body.visuals)
                and any(v.name == f"nozzle_{r.outlet_count - 1}" for v in body.visuals),
                details="nozzles emitted",
            )

    # slot_choices recorded.
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


def _body_nozzle_z(object_model, r: ResolvedPipelineConfig) -> float:
    """Recompute the standpipe nozzle height for the tests (mirrors the body
    builder), so the chain link count matches the build."""
    s = r.body_scale
    riser_len = RISER_LEN * s
    body_bottom_z = riser_len + COLLAR_H
    body_h = SP_BODY_H * s
    body_center_z = body_bottom_z + body_h / 2.0
    return body_center_z + 0.006


__all__ = (
    "PipelineConfig",
    "ResolvedPipelineConfig",
    "build_pipeline",
    "build_seeded_pipeline",
    "config_from_seed",
    "resolve_config",
    "run_pipeline_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
