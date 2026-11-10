# SPDX-License-Identifier: Apache-2.0

"""Large wheeled trashcan / wheelie bin — modular procedural template.

A large mobile waste container (240 L curbside cart -> 1100 L commercial
dumpster). Structure family (pattern = ``mixed``): a single static root
``body`` shell (cadquery loft of a rounded-rect profile, ``body_profile`` slot),
with three parallel module axes attaching:

  * ``body_profile`` (2): ``tapered_plastic`` (top-wide HDPE cart) /
    ``boxy_steel`` (near-straight steel dumpster). Chooses the root shell mesh
    + the cosmetic rib pattern. Mesh-helper dimension; adds no joint.
  * ``wheel_count`` (N in {2,4,6}): N CONTINUOUS ground wheels/casters rolling
    about +Y, contact patch at z=0. N=2 = rear axle pair (tapered only); N=4 =
    four corners; N=6 = four corners + a mid pair (needs body depth). The
    swivel kingpin is modelled as fixed-stem geometry fused into the shell
    (NOT a live DOF, per spec). Each wheel = TireGeometry+WheelGeometry mesh.
  * ``lid_count`` (N in {1,2,3}): the DEFINING articulation — N rear-hinged
    flip lids, each a REVOLUTE child about axis (0,-1,0) at the rear (-X) top
    rim, opening up/rearward. N=1 full-width / N=2 split twin / N=3 triple.
  * ``lift_iface`` (3): the lift / grab interface, inlined as body visuals
    (Rule 1, NO articulated parts): ``top_grab_lip`` (lid front lip + crown
    grip) / ``front_lift_comb`` (DIN trunnion bar + gusset tie-plates on the
    front wall) / ``side_grab_handles`` (molded grip bars proud of the side
    walls).

Sourced from ``articraft_template_authoring/specs_modular_v1/Urban_Environment_Large_Trashcan.md``
(2 converged parents P1 wheelie + P2 1100L, 8 slot-fork variants).

3 hard rules honoured: decorations are ``parent.visual`` (lift ifaces, ribs,
axle pins); every non-FIXED joint (lid REVOLUTE, wheel CONTINUOUS) declares a
MatingContract-or-grandfathered articulation with element-scoped allow_overlap;
the shell + wheels are cadquery/lathe meshes, NOT Box/Cylinder downgrades.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from math import pi
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireShoulder,
    TireSidewall,
    TireTread,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True


BodyProfile = Literal["tapered_plastic", "boxy_steel"]
LiftIface = Literal["top_grab_lip", "front_lift_comb", "side_grab_handles"]
PaletteStyle = Literal[
    "municipal_gray",
    "forest_green",
    "civic_blue",
    "hazard_orange",
    "hospital_white",
    "industrial_charcoal",
]

BODY_PROFILES: tuple[BodyProfile, ...] = ("tapered_plastic", "boxy_steel")
LIFT_IFACES: tuple[LiftIface, ...] = (
    "top_grab_lip",
    "front_lift_comb",
    "side_grab_handles",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "municipal_gray",
    "forest_green",
    "civic_blue",
    "hazard_orange",
    "hospital_white",
    "industrial_charcoal",
)

WHEEL_COUNTS: tuple[int, ...] = (2, 4, 6)
LID_COUNTS: tuple[int, ...] = (1, 2, 3)
# Multiplicity sampling weights (spec §Multiplicity).
WHEEL_WEIGHTS = {2: 0.35, 4: 0.45, 6: 0.20}
LID_WEIGHTS = {1: 0.40, 2: 0.40, 3: 0.20}

# Gating thresholds (resolved metric space, after scale).
N6_MIN_DEPTH = 0.95  # mid casters need a deep enough body
LID3_MIN_WIDTH = 0.90  # triple split needs a wide enough top


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "municipal_gray": {
        "body": (0.46, 0.48, 0.50, 1.0),
        "lid": (0.38, 0.40, 0.42, 1.0),
        "tire": (0.05, 0.05, 0.055, 1.0),
        "steel": (0.62, 0.64, 0.66, 1.0),
    },
    "forest_green": {
        "body": (0.10, 0.34, 0.20, 1.0),
        "lid": (0.07, 0.27, 0.15, 1.0),
        "tire": (0.04, 0.045, 0.04, 1.0),
        "steel": (0.55, 0.57, 0.58, 1.0),
    },
    "civic_blue": {
        "body": (0.07, 0.26, 0.58, 1.0),
        "lid": (0.05, 0.20, 0.46, 1.0),
        "tire": (0.03, 0.035, 0.04, 1.0),
        "steel": (0.60, 0.63, 0.66, 1.0),
    },
    "hazard_orange": {
        "body": (0.86, 0.40, 0.06, 1.0),
        "lid": (0.20, 0.20, 0.21, 1.0),
        "tire": (0.04, 0.04, 0.045, 1.0),
        "steel": (0.58, 0.60, 0.62, 1.0),
    },
    "hospital_white": {
        "body": (0.90, 0.91, 0.92, 1.0),
        "lid": (0.74, 0.76, 0.78, 1.0),
        "tire": (0.06, 0.06, 0.065, 1.0),
        "steel": (0.66, 0.68, 0.70, 1.0),
    },
    "industrial_charcoal": {
        "body": (0.13, 0.135, 0.14, 1.0),
        "lid": (0.18, 0.185, 0.19, 1.0),
        "tire": (0.02, 0.02, 0.022, 1.0),
        "steel": (0.50, 0.52, 0.54, 1.0),
    },
}


def _material_class_id(
    surface: Literal[
        "body",
        "lid",
        "side_handle",
        "lift_hardware",
        "wheel_hardware",
        "tire",
    ],
    body_profile: BodyProfile,
) -> str:
    """Return the formal material pool for one trashcan surface."""
    if surface in {"body", "lid", "side_handle"}:
        return (
            "plastic.opaque_generic"
            if body_profile == "tapered_plastic"
            else "metal.steel_galvanized"
        )
    if surface in {"lift_hardware", "wheel_hardware"}:
        return "metal.steel_galvanized"
    return "rubber.smooth_plain"


@dataclass(frozen=True)
class LargeTrashcanConfig:
    body_profile: BodyProfile | None = None
    lift_iface: LiftIface | None = None
    palette_style: PaletteStyle = "municipal_gray"
    wheel_count: int | None = None
    lid_count: int | None = None
    body_height_scale: float = 1.0
    body_width_scale: float = 1.0
    body_depth_scale: float = 1.0
    wheel_radius_scale: float = 1.0
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["municipal_gray"])
    )


@dataclass(frozen=True)
class ResolvedLargeTrashcanConfig:
    body_profile: BodyProfile
    lift_iface: LiftIface
    palette_style: PaletteStyle
    wheel_count: int
    lid_count: int
    # Nominal-by-profile dims, after scale.
    body_w: float  # top width (Y span)
    body_d: float  # depth (X span)
    body_h: float  # shell height
    top_w: float
    top_d: float
    wall_t: float
    bottom_z: float  # underside of shell
    top_z: float  # top rim z
    hinge_x: float
    hinge_z: float
    wheel_r: float
    wheel_z: float
    wheel_w: float
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _wheel_x_to_y() -> tuple[float, float, float]:
    """RPY rotating SDK wheel/tire local +X spin axis to world +Y."""
    return (0.0, 0.0, pi / 2.0)


# ---------------------------------------------------------------------------
# Procedural sampling (Contract 4: seed 0 is not special)
# ---------------------------------------------------------------------------
def _weighted(rng: random.Random, weights: dict[int, float]) -> int:
    keys = list(weights.keys())
    return rng.choices(keys, weights=[weights[k] for k in keys], k=1)[0]


def config_from_seed(seed: int) -> LargeTrashcanConfig:
    rng = random.Random(seed * 2654435761 & 0xFFFFFFFF)
    profile = rng.choice(BODY_PROFILES)

    width_scale = rng.uniform(0.92, 1.12)
    depth_scale = rng.uniform(0.95, 1.10)

    # Wheel count, gated by profile/depth.
    wheel_count = _weighted(rng, WHEEL_WEIGHTS)
    # N=2 only on the smaller tapered body.
    if wheel_count == 2 and profile != "tapered_plastic":
        wheel_count = 4
    # N=6 needs a deep body.
    base_depth = (0.74 if profile == "tapered_plastic" else 1.05) * depth_scale
    if wheel_count == 6 and base_depth < N6_MIN_DEPTH:
        wheel_count = 4

    # Lid count, gated by width.
    lid_count = _weighted(rng, LID_WEIGHTS)
    base_top_w = (0.60 if profile == "tapered_plastic" else 1.36) * width_scale
    if lid_count == 3 and base_top_w < LID3_MIN_WIDTH:
        lid_count = 2

    return LargeTrashcanConfig(
        body_profile=profile,
        lift_iface=rng.choice(LIFT_IFACES),
        palette_style=rng.choice(PALETTE_STYLES),
        wheel_count=wheel_count,
        lid_count=lid_count,
        body_height_scale=rng.uniform(0.92, 1.10),
        body_width_scale=width_scale,
        body_depth_scale=depth_scale,
        wheel_radius_scale=rng.uniform(0.90, 1.12),
    )


def resolve_config(config: LargeTrashcanConfig | None = None) -> ResolvedLargeTrashcanConfig:
    config = config or LargeTrashcanConfig()
    profile = config.body_profile or "tapered_plastic"
    lift = config.lift_iface or "top_grab_lip"
    if profile not in BODY_PROFILES:
        raise ValueError(f"Unsupported body_profile: {profile!r}")
    if lift not in LIFT_IFACES:
        raise ValueError(f"Unsupported lift_iface: {lift!r}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style!r}")

    hs = _clamp(config.body_height_scale, 0.92, 1.10)
    ws = _clamp(config.body_width_scale, 0.92, 1.12)
    ds = _clamp(config.body_depth_scale, 0.95, 1.10)
    rs = _clamp(config.wheel_radius_scale, 0.90, 1.12)

    if profile == "tapered_plastic":
        top_w, top_d, body_h = 0.60 * ws, 0.74 * ds, 0.94 * hs
        wall_t = 0.030
        wheel_r = 0.118 * rs
        bottom_z = 0.130
    else:  # boxy_steel
        # Real 1100 L dumpsters are rectangular: the lids hinge along the LONG
        # rear edge, so width (Y) exceeds depth (X) (~1.37 m x ~1.07 m).
        top_w, top_d, body_h = 1.36 * ws, 1.05 * ds, 1.18 * hs
        wall_t = 0.040
        wheel_r = 0.100 * rs
        bottom_z = 0.110
    wheel_w = 0.060

    # Ground clearance of the shell underside. Real bins drop the body to
    # ~8-13 cm above the contact patch; wheels/stems bridge the rest (the old
    # "floor above the wheel top" rule left a 22-25 cm void band under the
    # body, with wheels dangling on long stilts).
    top_z = bottom_z + body_h
    if profile == "boxy_steel" and top_w < 1.18 * top_d:
        # Real 1100 L dumpsters are oblong (lids hinge along the long rear
        # edge); scale draws near the extremes otherwise approach square.
        top_w = 1.18 * top_d

    # Axle height: the tread blocks stand ~4 mm proud of the nominal wheel
    # radius, so the joint sits slightly above r to keep the contact patch on
    # z=0 instead of digging in.
    wheel_z = wheel_r + 0.0038

    # Resolve wheel/lid counts (default to sampler-friendly values if absent).
    wheel_count = config.wheel_count if config.wheel_count in WHEEL_COUNTS else 4
    lid_count = config.lid_count if config.lid_count in LID_COUNTS else 1
    if wheel_count == 2 and profile != "tapered_plastic":
        wheel_count = 4
    if wheel_count == 6 and top_d < N6_MIN_DEPTH:
        wheel_count = 4
    if lid_count == 3 and top_w < LID3_MIN_WIDTH:
        lid_count = 2

    return ResolvedLargeTrashcanConfig(
        body_profile=profile,
        lift_iface=lift,
        palette_style=config.palette_style,
        wheel_count=wheel_count,
        lid_count=lid_count,
        body_w=top_w,
        body_d=top_d,
        body_h=body_h,
        top_w=top_w,
        top_d=top_d,
        wall_t=wall_t,
        bottom_z=bottom_z,
        top_z=top_z,
        hinge_x=-top_d * 0.5 + 0.020,
        hinge_z=top_z + 0.020,
        wheel_r=wheel_r,
        wheel_z=wheel_z,
        wheel_w=wheel_w,
        palette=dict(PALETTES[config.palette_style]),
    )


# ---------------------------------------------------------------------------
# Body shell mesh (Slot D)
# ---------------------------------------------------------------------------
def _shell_solid(r: ResolvedLargeTrashcanConfig):
    """Hollow lofted shell: bottom rrect -> top rrect, walls + floor, open top."""
    z0 = r.bottom_z
    z1 = r.top_z
    if r.body_profile == "tapered_plastic":
        bot_d, bot_w = r.top_d * 0.74, r.top_w * 0.80
    else:
        bot_d, bot_w = r.top_d * 0.94, r.top_w * 0.96
    fil_top = min(r.top_d, r.top_w) * 0.10
    fil_bot = min(bot_d, bot_w) * 0.10

    bot = (
        cq.Workplane("XY", origin=(0, 0, z0))
        .rect(bot_d, bot_w)
        .val()
    )
    top = (
        cq.Workplane("XY", origin=(0, 0, z1))
        .rect(r.top_d, r.top_w)
        .val()
    )
    outer = cq.Solid.makeLoft([bot, top])
    solid = cq.Workplane("XY").add(outer)
    try:
        solid = solid.edges("|Z").fillet(min(fil_top, fil_bot))
    except Exception:
        pass

    # Recess the mouth from the top (a shallow open cavity, not a full hollow):
    # keeps the collision shape connected through the solid lower body while
    # still reading as an open waste container. Depth ~55% of the body height.
    t = r.wall_t
    recess_depth = r.body_h * 0.55
    z_floor = z1 - recess_depth
    cav = (
        cq.Workplane("XY", origin=(0, 0, (z_floor + z1 + 0.02) / 2.0))
        .rect(r.top_d - 2 * t, r.top_w - 2 * t)
        .extrude((z1 + 0.02 - z_floor) / 2.0, both=True)
    )
    solid = solid.cut(cav)

    # Top rim collar (proud lip around the mouth), fully fused to the wall top.
    rim_outer = (
        cq.Workplane("XY", origin=(0, 0, z1 - 0.015))
        .rect(r.top_d + 0.04, r.top_w + 0.04)
        .extrude(0.030)
    )
    rim_inner = (
        cq.Workplane("XY", origin=(0, 0, z1 - 0.030))
        .rect(r.top_d - 2 * t, r.top_w - 2 * t)
        .extrude(0.080)
    )
    rim = rim_outer.cut(rim_inner)
    solid = solid.union(rim)
    if r.body_profile == "boxy_steel":
        solid = _add_skirt_and_wheel_wells(solid, r, z0, bot_d, bot_w)
    return solid, bot_d, bot_w


def _add_skirt_and_wheel_wells(solid, r: ResolvedLargeTrashcanConfig, z0, bot_d, bot_w):
    """Dumpster base skirt + caster wheel wells (boxy_steel only).

    The skirt is a perimeter apron ring dropping from the shell floor to 5.5 cm
    (the base frame of a real 1100 L dumpster). Each tucked caster gets a well
    pocket cut up through skirt and floor with ~6 mm clearance, leaving arch
    notches in the skirt like real caster cutouts. The stem boss/fork legs poke
    through the well ceiling and walls into the floor solid, keeping the whole
    body one fused component.
    """
    skirt_bottom = 0.055
    skirt_top = z0 + 0.030
    skirt = (
        cq.Workplane("XY", origin=(0, 0, skirt_bottom))
        .rect(bot_d + 0.012, bot_w + 0.012)
        .extrude(skirt_top - skirt_bottom)
    )
    skirt = skirt.cut(
        cq.Workplane("XY", origin=(0, 0, skirt_bottom - 0.005))
        .rect(bot_d - 0.050, bot_w - 0.050)
        .extrude(skirt_top - skirt_bottom + 0.010)
    )
    solid = solid.union(skirt)
    ceil_z = 2.0 * r.wheel_r + 0.012  # tire top (incl. tread) + ~4 mm clearance
    for x, y in _wheel_positions(r):
        solid = solid.cut(
            cq.Workplane("XY", origin=(x, y, (0.040 + ceil_z) / 2.0)).box(
                2.0 * r.wheel_r + 0.012, r.wheel_w + 0.020, ceil_z - 0.040
            )
        )
    return solid


def _body_mesh(r: ResolvedLargeTrashcanConfig, assets):
    solid, bot_d, bot_w = _shell_solid(r)

    # Cosmetic ribs fused into the front shell wall (loop-emitted; cosmetic
    # axis). Each rib is centered ON the wall front face so ~half its depth is
    # embedded in the wall solid -> they fuse into one connected component.
    # Ribs tunnel from outside the front face through the (possibly sloped) wall
    # into the cavity, so the union always fuses to a single solid regardless of
    # taper -> one mesh component (no intra-part islands).
    rib_depth = 0.090
    x_rib = r.top_d * 0.5 - 0.005 - rib_depth * 0.3
    if r.body_profile == "tapered_plastic":
        n = 4
        for i in range(n):
            yy = (-0.5 + (i + 0.5) / n) * (r.top_w * 0.7)
            rib = cq.Workplane("XY", origin=(x_rib, yy, r.bottom_z + r.body_h * 0.5)).box(
                rib_depth, 0.022, r.body_h * 0.72
            )
            solid = solid.union(rib)
    else:
        n = max(3, int(r.body_h / 0.22))
        for i in range(n):
            zc = r.bottom_z + (i + 0.7) / (n + 0.4) * r.body_h
            rib = cq.Workplane("XY", origin=(x_rib, 0.0, zc)).box(
                rib_depth, r.top_w * 0.92, 0.026
            )
            solid = solid.union(rib)
    solid = solid.clean()
    return mesh_from_cadquery(solid, "body", assets=assets, tolerance=0.0008, angular_tolerance=0.12)


def _wall_hw_y(r: ResolvedLargeTrashcanConfig, z: float) -> float:
    """Outer wall half-width (Y) at height z, following the loft taper."""
    bot_w = r.top_w * (0.80 if r.body_profile == "tapered_plastic" else 0.96)
    frac = _clamp((z - r.bottom_z) / r.body_h, 0.0, 1.0)
    return (bot_w + (r.top_w - bot_w) * frac) * 0.5


# Fixed wheel-stem / housing fused into the shell (one per wheel position).
# Authored at local origin (0,0,0); placed at (x,y,0) by the visual origin.
def _wheel_stem(r: ResolvedLargeTrashcanConfig, inboard_sign: float, reach: float):
    """A fixed stem reaching from inside the shell floor down to the wheel axle
    (z=R), with fork legs straddling the tire and a captured axle pin. Built as
    ONE connected solid; an inboard bracket arm (toward the shell, by `reach`
    along -Y*inboard_sign) laps the shell wall/floor for real support."""
    # Fuse through the shell floor; on boxy_steel the boss must also clear the
    # wheel-well ceiling so it stays embedded in the floor solid.
    z_top = max(r.bottom_z + r.wall_t + 0.010, 2.0 * r.wheel_r + 0.036)
    z_axle = r.wheel_z
    boss = cq.Workplane("XY", origin=(0, 0, (z_top + z_axle) / 2.0)).box(
        0.064, 0.064, (z_top - z_axle)
    )
    # Inboard bracket arm laps deep into the shell wall (reach + generous embed)
    # so the stem is fused to the body shell solid for real support.
    arm_len = reach + 0.090
    arm = cq.Workplane(
        "XY", origin=(0, -inboard_sign * (arm_len / 2.0 - 0.020), z_top - 0.030)
    ).box(0.060, arm_len, 0.055)
    boss = boss.union(arm)
    # Two fork legs straddling the tire (clear of the sidewall bulge).
    for sx in (-1.0, 1.0):
        leg = cq.Workplane(
            "XY", origin=(0, sx * (r.wheel_w / 2.0 + 0.018), z_axle + 0.010)
        ).box(0.030, 0.018, 0.070)
        boss = boss.union(leg)
    # Captured axle pin through the hub (X-axis), fused into the fork.
    pin = cq.Workplane("XZ", origin=(0, 0, z_axle)).circle(0.012).extrude(
        r.wheel_w / 2.0 + 0.024, both=True
    )
    boss = boss.union(pin)
    return boss


# ---------------------------------------------------------------------------
# Wheel mesh (Slot A) — SDK TireGeometry + WheelGeometry rim
# ---------------------------------------------------------------------------
def _wheel_meshes(r: ResolvedLargeTrashcanConfig, assets):
    # SDK wheels/tires are authored with the spin axle along local +X and width
    # along X. Build as a realistic small utility/caster wheel, then rotate the
    # whole visual by +90 deg about Z at placement so +X maps to the joint's +Y.
    tire_inner_r = r.wheel_r * 0.72
    hub_r = max(0.018, r.wheel_r * 0.22)
    rim_mesh = mesh_from_geometry(
        WheelGeometry(
            tire_inner_r,
            r.wheel_w * 0.78,
            rim=WheelRim(
                inner_radius=tire_inner_r * 0.56,
                flange_height=max(0.004, r.wheel_r * 0.045),
                flange_thickness=0.004,
                bead_seat_depth=0.003,
            ),
            hub=WheelHub(radius=hub_r, width=r.wheel_w * 0.62, cap_style="domed"),
            face=WheelFace(dish_depth=0.004, front_inset=0.002, rear_inset=0.002),
            spokes=WheelSpokes(
                style="straight",
                count=5,
                thickness=max(0.003, r.wheel_r * 0.035),
                window_radius=max(0.006, r.wheel_r * 0.09),
            ),
            bore=WheelBore(style="round", diameter=0.016),
            center=True,
        ),
        "wheel_rim",
    )
    tire = TireGeometry(
        r.wheel_r,
        r.wheel_w,
        inner_radius=tire_inner_r,
        carcass=TireCarcass(belt_width_ratio=0.76, sidewall_bulge=0.03),
        tread=TireTread(style="block", depth=0.0045, count=18, land_ratio=0.58),
        sidewall=TireSidewall(style="square", bulge=0.015),
        shoulder=TireShoulder(width=0.006, radius=0.003),
        center=True,
    )
    tire_mesh = mesh_from_geometry(tire, "wheel_tire")
    return rim_mesh, tire_mesh


def _wheel_positions(r: ResolvedLargeTrashcanConfig) -> list[tuple[float, float]]:
    """(x, y) ground positions for each wheel; z = R derived at build time."""
    n = r.wheel_count
    if r.body_profile == "tapered_plastic":
        # Wheels beside the tapered body: the tire's inner sidewall clears the
        # sloped wall at the tire's top z by ~5 mm (no more 5.8 cm splay).
        track = _wall_hw_y(r, 2.0 * r.wheel_r + 0.008) + r.wheel_w * 0.5 + 0.005
        cx = r.top_d * 0.40
    else:
        # Casters tucked under the body inside the skirt outline, like a real
        # dumpster; the wheel well keeps ~6 mm clearance around each tire.
        track = _wall_hw_y(r, r.bottom_z) - r.wheel_w * 0.5 - 0.015
        cx = r.top_d * 0.34
    if n == 2:
        # Rear axle pair (at -X), small front skids implicit.
        rear_x = -r.top_d * 0.40
        return [(rear_x, +track), (rear_x, -track)]
    if n == 4:
        return [(sx * cx, sy * track) for sx in (-1.0, 1.0) for sy in (1.0, -1.0)]
    # n == 6: four corners + mid pair.
    pos = [(sx * cx, sy * track) for sx in (-1.0, 1.0) for sy in (1.0, -1.0)]
    pos += [(0.0, +track), (0.0, -track)]
    return pos


# ---------------------------------------------------------------------------
# Lid mesh (Slot B)
# ---------------------------------------------------------------------------
def _lid_mesh(r: ResolvedLargeTrashcanConfig, half_w: float, idx: int, assets):
    """One lid panel. Authored in a hinge-line local frame: the hinge edge is
    at local x=0 (so the part origin lands inside geometry), the plate extends
    +X over the mouth; +Y/-Y span = panel width. Domed slightly up (+Z)."""
    plate_len = r.top_d + 0.020  # slight overhang past the front rim
    t = 0.034
    # Plate: from hinge edge (x=0) forward to +X.
    plate = cq.Workplane("XY", origin=(plate_len / 2.0, 0.0, 0.0)).box(plate_len, 2 * half_w, t)
    try:
        plate = plate.edges("|Z").fillet(0.020)
    except Exception:
        pass
    if r.body_profile == "tapered_plastic":
        # Gentle dome rib down the center.
        dome = cq.Workplane("XY", origin=(plate_len * 0.5, 0.0, t * 0.4)).box(
            plate_len * 0.9, 2 * half_w * 0.5, t * 0.7
        )
        plate = plate.union(dome)
    # Knuckle barrel along the hinge edge (gives the part real hinge hardware
    # at the joint origin x=0). A small solid core cube guarantees the joint
    # origin (0,0,0) sits inside the child collision mesh (origin baseline).
    knuckle = (
        cq.Workplane("XZ", origin=(0.0, 0.0, 0.0))
        .circle(0.028)
        .extrude(half_w, both=True)
    )
    plate = plate.union(knuckle)
    # Axial hinge bore: leaves a cylindrical surface ~6 mm from the part origin
    # so the joint origin (0,0,0) sits within the articulation-origin baseline.
    bore = cq.Workplane("XZ", origin=(0.0, 0.0, 0.0)).circle(0.007).extrude(half_w + 0.01, both=True)
    plate = plate.cut(bore)
    # Front skirt that laps the rim when closed.
    skirt = cq.Workplane("XY", origin=(plate_len - 0.020, 0.0, -0.020)).box(
        0.030, 2 * half_w * 0.96, 0.050
    )
    plate = plate.union(skirt)
    return mesh_from_cadquery(plate, f"lid_{idx}", assets=assets, tolerance=0.001)


def _lid_layout(r: ResolvedLargeTrashcanConfig) -> list[tuple[float, float]]:
    """(y_center, half_width) per lid panel, splitting the mouth across Y."""
    n = r.lid_count
    usable = r.top_w + 0.010  # slight overhang
    gap = 0.008
    panel_w = usable / n - gap
    half = panel_w / 2.0
    if n == 1:
        return [(0.0, half)]
    centers = [(-(n - 1) / 2.0 + i) * (usable / n) for i in range(n)]
    return [(c, half) for c in centers]


# ---------------------------------------------------------------------------
# Lift interface visuals (Slot C) — inlined body visuals, NO joints
# ---------------------------------------------------------------------------
def _lift_comb_visuals(body, r, mats, assets):
    """Front DIN trunnion bar on standoff gussets, proud of the front wall.

    The bar sits 7 cm off the wall (a real lift comb, not a flush stripe); the
    gusset plates bridge from 2 cm inside the wall out past the bar, fusing
    both into one supported assembly.
    """
    x_front = r.top_d * 0.5
    z_bar = r.bottom_z + r.body_h * 0.42
    bar = cq.Workplane("XZ", origin=(0, 0, 0)).circle(0.026).extrude(r.top_w * 0.46, both=True)
    bar_mesh = mesh_from_cadquery(bar, "trunnion_bar", assets=assets)
    body.visual(
        bar_mesh,
        material=mats["steel"],
        name="trunnion_bar",
        origin=Origin(xyz=(x_front + 0.070, 0.0, z_bar)),
        material_class_id=_material_class_id("lift_hardware", r.body_profile),
    )
    for i, sy in enumerate((-1.0, 1.0)):
        gus = cq.Workplane("XY", origin=(x_front + 0.036, sy * r.top_w * 0.30, z_bar)).box(
            0.112, 0.030, 0.16
        )
        gus_mesh = mesh_from_cadquery(gus, f"gusset_{i}", assets=assets)
        body.visual(
            gus_mesh,
            material=mats["steel"],
            name=f"gusset_{i}",
            material_class_id=_material_class_id("lift_hardware", r.body_profile),
        )


def _side_handle_visuals(body, r, mats, assets):
    """Two molded grip bars proud of the ±Y side walls."""
    z_h = r.bottom_z + r.body_h * 0.80
    for i, sy in enumerate((-1.0, 1.0)):
        # Anchor on the ACTUAL wall face at this height (the loft tapers), not
        # the top-rim width -- otherwise the grip floats off the sloped wall.
        y_face = sy * _wall_hw_y(r, z_h)
        grip = cq.Workplane("XY", origin=(0, y_face + sy * 0.040, z_h)).box(
            r.top_d * 0.34, 0.042, 0.055
        )
        # Mounting posts bridge from inside the wall through to the grip bar.
        for sx in (-1.0, 1.0):
            post = cq.Workplane(
                "XY", origin=(sx * r.top_d * 0.14, y_face + sy * 0.005, z_h)
            ).box(0.034, 0.062, 0.050)
            grip = grip.union(post)
        grip = grip.clean()
        grip_mesh = mesh_from_cadquery(grip, f"side_handle_{i}", assets=assets)
        body.visual(
            grip_mesh,
            material=mats["steel"],
            name=f"side_handle_{i}",
            material_class_id=_material_class_id("side_handle", r.body_profile),
        )


def _top_grip_visuals(body, r, mats, assets):
    """Recessed crown grip lip on the rear rim (a top grab feature)."""
    # A molded back grip proud of the rear (-X) exterior wall, just below the
    # rim, behind the lid hinge so it clears the closed lid. Embedded into the
    # rear wall for support.
    x_back = -r.top_d * 0.5
    z_g = r.top_z - 0.060
    grip = cq.Workplane("XY", origin=(x_back - 0.010, 0.0, z_g)).box(
        0.070, r.top_w * 0.5, 0.045
    )
    grip_mesh = mesh_from_cadquery(grip, "crown_grip", assets=assets)
    body.visual(
        grip_mesh,
        material=mats["body"],
        name="crown_grip",
        material_class_id=_material_class_id("body", r.body_profile),
    )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_large_trashcan(
    config: LargeTrashcanConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="large_trashcan", assets=assets)
    mats = {
        key: model.material(f"trashcan_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in r.palette.items()
    }

    # ---- Slot D: body shell (root) ----
    body = model.part("body")
    body.visual(
        _body_mesh(r, assets),
        material=mats["body"],
        name="shell",
        material_class_id=_material_class_id("body", r.body_profile),
    )
    positions = _wheel_positions(r)
    # Fixed wheel stems (with captured axle pin + inboard bracket) fused into the
    # shell. Each stem's bracket reaches from the wheel inboard to lap the shell.
    for i, (x, y) in enumerate(positions):
        sign = 1.0 if y >= 0 else -1.0
        reach = max(0.0, abs(y) - r.top_w * 0.5)
        stem_mesh = mesh_from_cadquery(_wheel_stem(r, sign, reach), f"wheel_stem_{i}", assets=assets)
        body.visual(
            stem_mesh,
            material=mats["body"],
            name=f"wheel_stem_{i}",
            origin=Origin(xyz=(x, y, 0.0)),
            material_class_id=_material_class_id("wheel_hardware", r.body_profile),
        )
    body.inertial = Inertial.from_geometry(
        Box((r.top_d, r.top_w, r.body_h)),
        mass=14.0,
        origin=Origin(xyz=(0.0, 0.0, r.bottom_z + r.body_h * 0.5)),
    )

    # ---- Slot C: lift interface (inlined body visuals) ----
    if r.lift_iface == "front_lift_comb":
        _lift_comb_visuals(body, r, mats, assets)
    elif r.lift_iface == "side_grab_handles":
        _side_handle_visuals(body, r, mats, assets)
    else:
        _top_grip_visuals(body, r, mats, assets)

    # ---- Slot A: wheels (CONTINUOUS roll about +Y) ----
    rim_mesh, tire_mesh = _wheel_meshes(r, assets)
    wheel_origin = Origin(rpy=_wheel_x_to_y())
    for i, (x, y) in enumerate(positions):
        wheel = model.part(f"wheel_{i}")
        wheel.visual(
            rim_mesh,
            material=mats["steel"],
            name=f"rim_{i}",
            origin=wheel_origin,
            material_class_id=_material_class_id("wheel_hardware", r.body_profile),
        )
        wheel.visual(
            tire_mesh,
            material=mats["tire"],
            name=f"tire_{i}",
            origin=wheel_origin,
            material_class_id=_material_class_id("tire", r.body_profile),
        )
        wheel.inertial = Inertial.from_geometry(
            Box((2 * r.wheel_r, r.wheel_w, 2 * r.wheel_r)),
            mass=1.2,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        model.articulation(
            f"body_to_wheel_{i}",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=wheel,
            origin=Origin(xyz=(x, y, r.wheel_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=5.0, velocity=20.0),
        )

    # ---- Slot B: lids (REVOLUTE about (0,-1,0) at rear top rim) — DEFINING ----
    for i, (y_c, half_w) in enumerate(_lid_layout(r)):
        lid = model.part(f"lid_{i}")
        lid.visual(
            _lid_mesh(r, half_w, i, assets),
            material=mats["lid"],
            name=f"lid_panel_{i}",
            material_class_id=_material_class_id("lid", r.body_profile),
        )
        lid.inertial = Inertial.from_geometry(
            Box((r.top_d, 2 * half_w, 0.04)),
            mass=2.5,
            origin=Origin(xyz=(r.top_d * 0.5, 0.0, 0.0)),
        )
        model.articulation(
            f"body_to_lid_{i}",
            ArticulationType.REVOLUTE,
            parent=body,
            child=lid,
            origin=Origin(xyz=(r.hinge_x, y_c, r.hinge_z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=18.0, velocity=1.6, lower=0.0, upper=1.90),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_large_trashcan(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_large_trashcan(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Slot choices (Contract 4: drives module_topology_diversity)
# ---------------------------------------------------------------------------
def slot_choices_for_config(r: ResolvedLargeTrashcanConfig) -> list[tuple[str, str]]:
    return [
        ("body_profile", r.body_profile),
        ("wheel_count", f"n{r.wheel_count}"),
        ("lid_count", f"n{r.lid_count}"),
        ("lift_iface", r.lift_iface),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_large_trashcan_tests(
    object_model: ArticulatedObject, config: LargeTrashcanConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    names = {p.name for p in object_model.parts}

    ctx.check("body_present", "body" in names)
    ctx.check(
        "wheel_count_matches",
        sum(1 for n in names if n.startswith("wheel_") and not n.startswith("wheel_stem"))
        == r.wheel_count,
    )
    ctx.check("lid_count_matches", sum(1 for n in names if n.startswith("lid_")) == r.lid_count)

    wheel_joints = [j for j in object_model.articulations if j.name.startswith("body_to_wheel_")]
    ctx.check(
        "wheels_continuous_axis_y",
        len(wheel_joints) == r.wheel_count
        and all(
            j.articulation_type == ArticulationType.CONTINUOUS and j.axis == (0.0, 1.0, 0.0)
            for j in wheel_joints
        ),
    )
    lid_joints = [j for j in object_model.articulations if j.name.startswith("body_to_lid_")]
    ctx.check(
        "lids_revolute_axis_neg_y",
        len(lid_joints) == r.lid_count
        and all(
            j.articulation_type == ArticulationType.REVOLUTE and j.axis == (0.0, -1.0, 0.0)
            for j in lid_joints
        ),
    )

    # Captured-pin overlaps: each wheel hub straddles its body-fused stem (fork
    # legs + axle pin); each lid skirt laps the body rim when closed.
    body = object_model.get_part("body")
    for i in range(r.wheel_count):
        wp = object_model.get_part(f"wheel_{i}")
        for elem_b in (f"tire_{i}", f"rim_{i}"):
            ctx.allow_overlap(
                body,
                wp,
                elem_a=f"wheel_stem_{i}",
                elem_b=elem_b,
                reason="Wheel hub rotates around the captured body-fused axle pin / fork.",
            )
    for i in range(r.lid_count):
        lp = object_model.get_part(f"lid_{i}")
        ctx.allow_overlap(
            body,
            lp,
            elem_a="shell",
            elem_b=f"lid_panel_{i}",
            reason="Closed lid skirt laps the body top rim.",
        )
    return ctx.report()


__all__ = [
    "__modular__",
    "LargeTrashcanConfig",
    "ResolvedLargeTrashcanConfig",
    "config_from_seed",
    "resolve_config",
    "build_large_trashcan",
    "build_seeded_large_trashcan",
    "slot_choices_for_seed",
    "run_large_trashcan_tests",
]
