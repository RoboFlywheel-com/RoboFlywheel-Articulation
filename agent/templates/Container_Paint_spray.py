# SPDX-License-Identifier: Apache-2.0

"""Container paint spray — modular procedural template (aerosol spray-paint can).

Category identity: an upright, slim-and-tall metal aerosol spray-paint can. The
``can_body`` (ROOT) rests on z=0 with its axis along +Z, rises through a straight
/ waisted / oval wall into a crimped shoulder dome and a short central valve
stem boss. Two independent functional layers parent directly to the can body
(parallel children, no serial chain, no multiplicity):

  * ``body_section`` (3) — the ROOT ``can_body`` mesh: straight equal-diameter
    cylinder (extrude wall + lofted crimp dome), a waisted lathe body (revolve
    of a closed XZ spline half-profile with a concave upper-third waist), or a
    flat-oval body (loft of ellipse sections, X-wide Y-narrow ~1.75:1). All emit
    a crimped dome + central valve stem boss + a splatter label band.
  * ``actuator`` (4, the active spray mechanism; >=1 non-fixed joint each):
      - press_button: small rounded button on the valve stem, ``nozzle_press``
        PRISMATIC -Z (~0.004 m) presses the valve. 1 part / 1 joint.
      - trigger_lever: Montana-style finger lever + fixed ``trigger_housing``
        visual; ``trigger_squeeze`` REVOLUTE +Y swings inward and down on the
        valve. 1 part / 1 joint + 1 fixed visual.
      - pistol_grip: clip-on can-gun adapter (C-clamp + handle + linkage arm +
        plunger) on a ``grip_mount`` FIXED, carrying a ``trigger`` on a
        ``trigger_pull`` REVOLUTE +Y. 2 parts / 2 joints (body->grip->trigger).
      - fan_spin_cap: wide oval fan cap stem on ``fan_cap_press`` PRISMATIC -Z,
        carrying a broad oval ``fan_cap`` head on ``fan_cap_twist`` REVOLUTE +Z
        (twist switches the spray fan). 2 parts / 2 joints (body->stem->head).
  * ``closure_cap`` (4; ``no_cap_collar`` is the only capless one):
      - lift_off_cap: hollow dust cap shell, ``cap_lift`` PRISMATIC +Z big
        travel (~0.09 m) lifts clear of the actuator. 1 part / 1 joint.
      - flip_top_cap: one-piece flip lid hinged at the rear shoulder,
        ``cap_hinge`` REVOLUTE +X (q=0 closed, +q flips up); 2 fixed
        ``hinge_ear`` visuals on the body. 1 part / 1 joint.
      - screw_cap: threaded cap decoupled through a massless ``cap_carrier``:
        ``cap_unscrew`` CONTINUOUS +Z then ``cap_lift`` PRISMATIC +Z; a fixed
        ``threaded_collar`` visual on the body. 2 parts (cap + carrier) /
        2 joints.
      - no_cap_collar: NO cap part — a low ``collar_ring`` + 6 ``grip_ridge``
        fixed visuals + a red ``lock_tab`` on ``tab_slide`` PRISMATIC -Y that
        slides under the nozzle lip to lock it. 1 part / 1 joint.

The three axes are orthogonal: trigger / pistol / fan all keep their dust cap;
only ``no_cap_collar`` removes the cap. 4 x 4 x 3 = 48 topology combos; cap x
actuator = 16 already clears ``module_topology_diversity``.

Continuous size variation (height / radius / cap-height / lift-travel /
press scales) lives in ``resolve_config`` as clamped params and the derived
``cap_bore_r`` / ``clamp_inner_r`` equations; never as slot candidates.
``palette_style`` (9 colorways + bound finish) only drives material rgba.

Sources (articraft_data ``picture/Container/Paint spray`` 5-star pool): parent
``5eaf6974`` (straight + press_button + lift_off), plus qwen forks
``var_flip_top`` / ``var_screw_cap`` / ``var_no_cap_collar`` (cap),
``var_trigger_lever`` / ``var_pistol_grip`` / ``var_fan_spin_cap`` (actuator),
``var_waisted_body`` / ``var_oval_section`` (body).

Canonical spec:
``articraft_template_authoring/specs_modular_v1/Container_Paint_spray.md``
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    CylinderGeometry,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodySection = Literal["straight_cylinder", "waisted_body", "oval_section"]
Actuator = Literal["press_button", "trigger_lever", "pistol_grip", "fan_spin_cap"]
ClosureCap = Literal["lift_off_cap", "flip_top_cap", "screw_cap", "no_cap_collar"]
PaletteStyle = Literal[
    "classic_white_splatter",
    "matte_black_pro",
    "safety_red",
    "industrial_blue",
    "hi_vis_yellow",
    "primer_grey",
    "brushed_aluminum",
    "metallic_silver_blue",
    "two_tone_black_orange",
]

BODY_SECTIONS: tuple[BodySection, ...] = (
    "straight_cylinder",
    "waisted_body",
    "oval_section",
)
ACTUATORS: tuple[Actuator, ...] = (
    "press_button",
    "trigger_lever",
    "pistol_grip",
    "fan_spin_cap",
)
CLOSURE_CAPS: tuple[ClosureCap, ...] = (
    "lift_off_cap",
    "flip_top_cap",
    "screw_cap",
    "no_cap_collar",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_white_splatter",
    "matte_black_pro",
    "safety_red",
    "industrial_blue",
    "hi_vis_yellow",
    "primer_grey",
    "brushed_aluminum",
    "metallic_silver_blue",
    "two_tone_black_orange",
)

# ---------------------------------------------------------------------------
# Palettes: 9 colorways, each bound to an explicit finish dimension. Material
# rgba is anchored in the 5-star sources (parent / trigger / pistol / fan /
# screw / oval / waisted / no_cap / flip) for the first six; the last three are
# plausible real-spray-can extrapolations anchored on source metal accents. The
# finish key only tweaks rgba (metallic brightens, matte desaturates, brushed
# alu shares the body color on the label) — it never touches geometry or slots.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Palette:
    finish: str
    metal: tuple[float, float, float, float]
    cap: tuple[float, float, float, float]
    accent: tuple[float, float, float, float]
    label: tuple[float, float, float, float]


PALETTES: dict[PaletteStyle, _Palette] = {
    "classic_white_splatter": _Palette(
        finish="glossy_print",
        metal=(0.78, 0.80, 0.83, 1.0),
        cap=(0.20, 0.21, 0.20, 1.0),
        accent=(0.16, 0.16, 0.17, 1.0),
        label=(0.90, 0.90, 0.92, 1.0),
    ),
    "matte_black_pro": _Palette(
        finish="matte",
        metal=(0.74, 0.76, 0.79, 1.0),
        cap=(0.10, 0.10, 0.12, 1.0),
        accent=(0.12, 0.12, 0.13, 1.0),
        label=(0.14, 0.14, 0.15, 1.0),
    ),
    "safety_red": _Palette(
        finish="glossy_print",
        metal=(0.78, 0.80, 0.83, 1.0),
        cap=(0.78, 0.14, 0.10, 1.0),
        accent=(0.72, 0.18, 0.12, 1.0),
        label=(0.90, 0.90, 0.92, 1.0),
    ),
    "industrial_blue": _Palette(
        finish="glossy_print",
        metal=(0.78, 0.80, 0.83, 1.0),
        cap=(0.18, 0.20, 0.24, 1.0),
        accent=(0.16, 0.18, 0.22, 1.0),
        label=(0.12, 0.55, 0.82, 1.0),
    ),
    "hi_vis_yellow": _Palette(
        finish="hi_vis_safety",
        metal=(0.78, 0.80, 0.83, 1.0),
        cap=(0.16, 0.16, 0.17, 1.0),
        accent=(0.18, 0.18, 0.18, 1.0),
        label=(0.95, 0.82, 0.10, 1.0),
    ),
    "primer_grey": _Palette(
        finish="primer_matte",
        metal=(0.74, 0.75, 0.78, 1.0),
        cap=(0.70, 0.73, 0.77, 1.0),
        accent=(0.58, 0.60, 0.63, 1.0),
        label=(0.88, 0.89, 0.91, 1.0),
    ),
    "brushed_aluminum": _Palette(
        finish="brushed_aluminum",
        metal=(0.82, 0.83, 0.85, 1.0),
        cap=(0.70, 0.73, 0.77, 1.0),
        accent=(0.65, 0.67, 0.70, 1.0),
        label=(0.82, 0.83, 0.85, 1.0),
    ),
    "metallic_silver_blue": _Palette(
        finish="metallic",
        metal=(0.80, 0.82, 0.86, 1.0),
        cap=(0.26, 0.27, 0.30, 1.0),
        accent=(0.30, 0.34, 0.42, 1.0),
        label=(0.18, 0.42, 0.70, 1.0),
    ),
    "two_tone_black_orange": _Palette(
        finish="two_tone",
        metal=(0.78, 0.80, 0.83, 1.0),
        cap=(0.12, 0.12, 0.13, 1.0),
        accent=(0.92, 0.45, 0.08, 1.0),
        label=(0.92, 0.45, 0.08, 1.0),
    ),
}


# ---------------------------------------------------------------------------
# Nominal geometry (meters). All shared with the 5-star sources; scaled per
# build by resolve_config.
# ---------------------------------------------------------------------------
CAN_R = 0.0325            # nominal body radius (~0.065 m dia)
CAN_RX = 0.035            # oval half-width (X)
CAN_RY = 0.020            # oval half-depth (Y) — flat oval
BODY_TOP = 0.150          # straight wall ends / dome begins
DOME_TOP = 0.176          # crimped dome top (mounting cup rim)
VALVE_TOP = 0.182         # central valve stem top
NOZZLE_SEAT_Z = 0.176     # actuator seat (valve seat)
CAP_BOTTOM = 0.150        # cap seat z (lift/screw cap lower rim)
LABEL_H = 0.105           # label band height
NOZZLE_PRESS = 0.004      # nominal press travel
CAP_LIFT = 0.090          # nominal lift-off cap travel

# waisted-body section nominal params
WAIST_SHOULDER_R = 0.024
WAIST_START_Z = 0.090
WAIST_END_Z = 0.115
WAIST_DOME_START_Z = 0.148


@dataclass(frozen=True)
class ContainerPaintSprayConfig:
    body_section: BodySection = "straight_cylinder"
    actuator: Actuator = "press_button"
    closure_cap: ClosureCap = "lift_off_cap"
    palette_style: PaletteStyle = "classic_white_splatter"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    cap_height_scale: float = 1.0
    cap_lift_travel_scale: float = 1.0
    actuator_press_scale: float = 1.0
    name: str = "container_paint_spray"


@dataclass(frozen=True)
class ResolvedContainerPaintSprayConfig:
    body_section: BodySection
    actuator: Actuator
    closure_cap: ClosureCap
    palette_style: PaletteStyle
    body_height_scale: float
    body_radius_scale: float
    cap_height_scale: float
    cap_lift_travel_scale: float
    actuator_press_scale: float
    # derived geometry (world z heights and radii)
    can_r: float
    can_rx: float
    can_ry: float
    body_top: float
    dome_top: float
    valve_top: float
    seat_z: float          # actuator valve-seat z (== dome_top)
    cap_seat_z: float      # cap seat z
    cap_seat_r: float      # body wall radius at the cap seat (per section)
    label_h: float
    press_travel: float
    cap_lift_travel: float
    cap_bore_r: float      # cap/clamp inner radius equation
    clamp_inner_r: float   # pistol clamp inner radius
    grip_center_z: float   # pistol clamp center z
    actuator_top_z: float  # world z of the tallest actuator point (for lift sizing)
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerPaintSprayConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return ContainerPaintSprayConfig(
        body_section=rng.choice(BODY_SECTIONS),
        actuator=rng.choice(ACTUATORS),
        closure_cap=rng.choice(CLOSURE_CAPS),
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.88, 1.18), 4),
        body_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        cap_height_scale=round(rng.uniform(0.85, 1.15), 4),
        cap_lift_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        actuator_press_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_container_paint_spray_{seed}",
    )


def resolve_config(
    config: ContainerPaintSprayConfig | None = None,
) -> ResolvedContainerPaintSprayConfig:
    cfg = config or ContainerPaintSprayConfig()
    body_section = _pick(cfg.body_section, BODY_SECTIONS)
    actuator = _pick(cfg.actuator, ACTUATORS)
    closure_cap = _pick(cfg.closure_cap, CLOSURE_CAPS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    h_scale = _clamp(cfg.body_height_scale, 0.88, 1.18)
    r_scale = _clamp(cfg.body_radius_scale, 0.90, 1.12)
    ch_scale = _clamp(cfg.cap_height_scale, 0.85, 1.15)
    clt_scale = _clamp(cfg.cap_lift_travel_scale, 0.85, 1.10)
    press_scale = _clamp(cfg.actuator_press_scale, 0.90, 1.10)

    # Radius scales the wall; oval keeps its X:Y ratio.
    can_r = CAN_R * r_scale
    can_rx = CAN_RX * r_scale
    can_ry = CAN_RY * r_scale

    # Height scale lifts BODY_TOP -> DOME_TOP -> valve / cap seats together.
    body_top = BODY_TOP * h_scale
    dome_top = body_top + (DOME_TOP - BODY_TOP) * h_scale
    valve_top = dome_top + (VALVE_TOP - DOME_TOP) * h_scale
    seat_z = dome_top  # actuator seats on the valve cup at the dome top
    label_h = LABEL_H * h_scale

    press_travel = NOZZLE_PRESS * press_scale

    # cap_bore_r equation: the cap/skirt inner radius follows the body wall
    # radius AT THE CAP SEAT HEIGHT (different per section) + a clearance, so the
    # skirt actually sleeves over real wall instead of floating in air. The
    # straight/oval body is full-radius up to body_top; the waisted body has
    # already narrowed to the shoulder there, so its cap seats lower over the
    # narrow shoulder wall (waisted source pattern). A tiny NEGATIVE clearance
    # (interference) keeps the inner skirt wall in real contact with the body so
    # the cap is never support-disconnected; the captured-fit overlap is allowed.
    cap_clearance = 0.0006
    if body_section == "waisted_body":
        cap_seat_r = WAIST_SHOULDER_R * r_scale
        # Seat on the established narrow upper wall (between waist end and the
        # dome start), so the skirt sleeves over real SHOULDER_R wall.
        cap_seat_z = (WAIST_DOME_START_Z * h_scale) - 0.010
    elif body_section == "oval_section":
        cap_seat_r = max(can_rx, can_ry)  # cap clears the oval footprint
        cap_seat_z = body_top
    else:
        cap_seat_r = can_r
        cap_seat_z = body_top
    cap_bore_r = cap_seat_r + cap_clearance
    # pistol C-clamp inner radius adapts to oval (max of rx/ry + gap).
    clamp_inner_r = max(can_r, can_rx, can_ry) + 0.0020

    # pistol clamp center: on the straight upper wall. For the waisted body it
    # must stay below the waist start so it grips a full-diameter section; the
    # straight / oval bodies are full-radius up to body_top, so keep it high.
    if body_section == "waisted_body":
        grip_center_z = min(0.120 * h_scale, (WAIST_START_Z * h_scale) - 0.015)
        grip_center_z = max(grip_center_z, 0.060)
    else:
        grip_center_z = 0.120 * h_scale

    # Tallest actuator top in world z (so cap lift always clears it). press/fan
    # seat at dome_top and rise ~0.020-0.030; trigger housing rises higher.
    actuator_top_by_kind = {
        "press_button": seat_z + 0.020,
        "trigger_lever": dome_top + 0.024 + 0.012,  # housing + lever swing top
        "pistol_grip": dome_top + 0.014,            # plunger over valve
        "fan_spin_cap": seat_z + 0.010 + 0.014 + 0.004,
    }
    actuator_top_z = actuator_top_by_kind[actuator]

    # cap_lift_travel inequality: travel must raise the cap above the actuator
    # top with margin. Project up if the sampled scale is too small.
    base_lift = CAP_LIFT * h_scale * clt_scale
    needed = (actuator_top_z - cap_seat_z) + 0.012
    cap_lift_travel = max(base_lift, needed)

    return ResolvedContainerPaintSprayConfig(
        body_section=body_section,
        actuator=actuator,
        closure_cap=closure_cap,
        palette_style=palette,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        cap_height_scale=ch_scale,
        cap_lift_travel_scale=clt_scale,
        actuator_press_scale=press_scale,
        can_r=can_r,
        can_rx=can_rx,
        can_ry=can_ry,
        body_top=body_top,
        dome_top=dome_top,
        valve_top=valve_top,
        seat_z=seat_z,
        cap_seat_z=cap_seat_z,
        cap_seat_r=cap_seat_r,
        label_h=label_h,
        press_travel=press_travel,
        cap_lift_travel=cap_lift_travel,
        cap_bore_r=cap_bore_r,
        clamp_inner_r=clamp_inner_r,
        grip_center_z=grip_center_z,
        actuator_top_z=actuator_top_z,
        name=cfg.name or "container_paint_spray",
    )


def with_overrides(
    config: ContainerPaintSprayConfig, **kwargs: object
) -> ContainerPaintSprayConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerPaintSprayConfig | ResolvedContainerPaintSprayConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedContainerPaintSprayConfig)
        else resolve_config(config)
    )
    return (
        ("body_section", r.body_section),
        ("actuator", r.actuator),
        ("closure_cap", r.closure_cap),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Slot C — can_body (ROOT). Three section builders, all emit a crimped dome +
# central valve stem boss. straight = extrude wall + loft dome; waisted =
# revolve of a closed XZ spline half-profile; oval = loft of ellipse sections.
# ===========================================================================
def _straight_body_solid(r: ResolvedContainerPaintSprayConfig) -> cq.Workplane:
    """Straight equal-diameter can (parent ``_can_body_solid``)."""
    R = r.can_r
    bt = r.body_top
    dt = r.dome_top
    vt = r.valve_top
    body = cq.Workplane("XY").circle(R + 0.0012).extrude(0.006)
    body = body.union(
        cq.Workplane("XY").workplane(offset=0.005).circle(R).extrude(bt - 0.005)
    )
    dome = (
        cq.Workplane("XY")
        .workplane(offset=bt - 0.001)
        .circle(R)
        .workplane(offset=0.006)
        .circle(R - 0.001)
        .workplane(offset=0.004)
        .circle(R - 0.006)
        .workplane(offset=(dt - bt) - 0.010)
        .circle(0.014)
        .loft(ruled=False)
    )
    body = body.union(dome)
    body = body.union(
        cq.Workplane("XY")
        .workplane(offset=dt - 0.001)
        .circle(0.006)
        .extrude(vt - dt + 0.001)
    )
    return body


def _waisted_body_solid(r: ResolvedContainerPaintSprayConfig) -> cq.Workplane:
    """Waisted can: revolve of a closed XZ spline half-profile (waisted source).

    Full-diameter lower wall, concave waist spline narrowing to a shoulder, a
    dome spline curving inward to the cup rim, then the valve stem."""
    R = r.can_r
    Rr = WAIST_SHOULDER_R * r.body_radius_scale
    Rrim = R + 0.0012
    h = r.body_height_scale
    ws = WAIST_START_Z * h
    we = WAIST_END_Z * h
    ds = WAIST_DOME_START_Z * h
    dt = r.dome_top
    vt = r.valve_top
    profile = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(Rrim, 0.0)
        .lineTo(Rrim, 0.006)
        .lineTo(R, 0.007)
        .lineTo(R, ws)
        .spline(
            [
                (R - 0.002, ws + 0.005),
                (R - 0.005, ws + 0.010),
                (Rr + 0.002, ws + 0.018),
                (Rr, we),
            ],
            includeCurrent=True,
            periodic=False,
            tangents=[(0.0, 1.0), (0.0, 1.0)],
        )
        .lineTo(Rr, ds)
        .spline(
            [
                (Rr - 0.002, ds + 0.005),
                (0.019, ds + 0.012),
                (0.016, ds + 0.020),
                (0.014, dt - 0.001),
            ],
            includeCurrent=True,
            periodic=False,
            tangents=[(0.0, 1.0), (-0.5, 1.0)],
        )
        .lineTo(0.014, dt)
        .lineTo(0.006, dt)
        .lineTo(0.006, vt)
        .lineTo(0.0, vt)
        .close()
    )
    return profile.revolve(360, (0.0, 0.0), (0.0, 1.0))


def _oval_body_solid(r: ResolvedContainerPaintSprayConfig) -> cq.Workplane:
    """Flat-oval can: extruded oval wall + loft of ellipse sections to a round
    cup (oval source). The straight wall is a flat extrude (not a spline loft)
    so the base stays exactly on z=0 with no downward bulge; only the crimp dome
    above body_top is a loft."""
    rx = r.can_rx
    ry = r.can_ry
    bt = r.body_top
    dt = r.dome_top
    vt = r.valve_top
    extra = 0.0012
    # Bottom rolled-seam rim (flat extrude, base at z=0).
    body = cq.Workplane("XY").ellipse(rx + extra, ry + extra).extrude(0.006)
    # Straight oval wall (flat extrude), reaching a touch above body_top so it
    # fuses robustly with the dome loft (a hairline overlap leaves 2 solids).
    body = body.union(
        cq.Workplane("XY").workplane(offset=0.005).ellipse(rx, ry).extrude(bt - 0.005 + 0.004)
    )
    # Crimped dome above body_top: loft ellipse -> round cup rim. Start the loft
    # well inside the wall top (0.006 overlap) so the boolean union fuses into a
    # single solid.
    # Penultimate shoulder ellipse kept strictly larger than the round cup rim
    # so the final ellipse->circle transition never degenerates (when ry-0.006
    # equals the 0.014 cup radius the loft self-intersects and the tessellator
    # hangs). cup_r is also clamped below the smaller shoulder semi-axis.
    sh_rx = rx - 0.006
    sh_ry = max(ry - 0.006, 0.010)
    cup_r = min(0.013, sh_rx - 0.003, sh_ry - 0.003)
    dome = (
        cq.Workplane("XY")
        .workplane(offset=bt - 0.006)
        .ellipse(rx, ry)
        .workplane(offset=0.011)
        .ellipse(rx - 0.001, ry - 0.001)
        .workplane(offset=0.004)
        .ellipse(sh_rx, sh_ry)
        .workplane(offset=(dt - bt) - 0.009)
        .circle(cup_r)
        .loft(ruled=False)
    )
    body = body.union(dome)
    stem = (
        cq.Workplane("XY")
        .workplane(offset=dt - 0.004)
        .circle(0.006)
        .extrude(vt - dt + 0.004)
    )
    return body.union(stem)


def _emit_body(body, r: ResolvedContainerPaintSprayConfig, *, metal_mat, label_mat) -> None:
    if r.body_section == "straight_cylinder":
        solid = _straight_body_solid(r)
    elif r.body_section == "waisted_body":
        solid = _waisted_body_solid(r)
    else:
        solid = _oval_body_solid(r)
    body.visual(mesh_from_cadquery(solid, "can_body"), material=metal_mat, name="can_body", material_class_id="metal.aluminum_bare")

    # Splatter label band sleeve on the straight wall.
    if r.body_section == "oval_section":
        band = (
            cq.Workplane("XY")
            .workplane(offset=0.012)
            .ellipse(r.can_rx + 0.0004, r.can_ry + 0.0004)
            .extrude(r.label_h)
        )
        body.visual(mesh_from_cadquery(band, "label_band"), material=label_mat, name="label_band", material_class_id="paper.cardboard")
    else:
        band_r = r.can_r + 0.0004
        label_band = CylinderGeometry(band_r, r.label_h, radial_segments=64)
        label_band.translate(0.0, 0.0, 0.012 + r.label_h / 2.0)
        body.visual(
            mesh_from_geometry(label_band, "label_band"), material=label_mat, name="label_band", material_class_id="paper.cardboard"
        )

    body.inertial = Inertial.from_geometry(
        Cylinder(max(r.can_r, r.can_rx), r.dome_top),
        mass=0.30,
        origin=Origin(xyz=(0.0, 0.0, r.dome_top / 2.0)),
    )


# ===========================================================================
# Slot B — actuator solids
# ===========================================================================
def _nozzle_solid() -> cq.Workplane:
    """Press-down spray button with a front spray hole (parent ``_nozzle_solid``)."""
    btn = (
        cq.Workplane("XY")
        .box(0.018, 0.016, 0.014, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.003)
    )
    hole = (
        cq.Workplane("YZ")
        .workplane(offset=0.009)
        .center(0.0, 0.008)
        .circle(0.0014)
        .extrude(-0.010)
    )
    return btn.cut(hole)


def _trigger_housing_solid() -> cq.Workplane:
    """Fixed cap housing on the dome top with a top-front pivot ear (trigger src)."""
    hw, hd, hh = 0.020, 0.024, 0.024
    body = (
        cq.Workplane("XY")
        .box(hw, hd, hh, centered=(True, True, False))
        .edges("|Z").fillet(0.004)
        .edges(">Z").fillet(0.002)
    )
    ear = (
        cq.Workplane("XY")
        .workplane(offset=hh - 0.008)
        .center(0.008, 0)
        .box(0.008, hd + 0.002, 0.010, centered=(True, True, False))
        .edges(">Z").fillet(0.002)
    )
    return body.union(ear)


def _trigger_lever_solid() -> cq.Workplane:
    """Montana finger lever, origin at the pivot (trigger src)."""
    profile = (
        cq.Workplane("XZ")
        .moveTo(0.000, 0.000)
        .lineTo(0.006, 0.000)
        .lineTo(0.018, -0.014)
        .lineTo(0.020, -0.018)
        .lineTo(0.020, -0.020)
        .lineTo(0.010, -0.020)
        .lineTo(0.008, -0.018)
        .lineTo(0.004, -0.004)
        .close()
    )
    lever = profile.extrude(0.018).translate((0, 0.009, 0))
    bushing = (
        cq.Workplane("XZ")
        .center(0.0, 0.0)
        .circle(0.005)
        .extrude(0.022)
        .translate((0, 0.011, 0))
    )
    lever = lever.union(bushing)
    for i in range(3):
        z_off = -0.017 - i * 0.001
        ridge = (
            cq.Workplane("XZ")
            .center(0.019, z_off)
            .rect(0.004, 0.001)
            .extrude(0.016)
            .translate((0, 0.008, 0))
        )
        lever = lever.union(ridge)
    return lever


def _fan_cap_stem_solid() -> cq.Workplane:
    """Short sleeve with a top collar — the prismatic press member (fan src)."""
    stem = cq.Workplane("XY").circle(0.008).extrude(0.007)
    bore = cq.Workplane("XY").workplane(offset=-0.001).circle(0.0062).extrude(0.006)
    stem = stem.cut(bore)
    collar = cq.Workplane("XY").workplane(offset=0.006).circle(0.012).extrude(0.004)
    return stem.union(collar)


def _fan_cap_head_solid() -> cq.Workplane:
    """Broad oval fan cap head with a top spray slot (fan src)."""
    head_h = 0.014
    cap = cq.Workplane("XY").ellipse(0.020, 0.013).extrude(head_h)
    cap = cap.edges(">Z").fillet(0.003)
    channel = cq.Workplane("XY").circle(0.005).extrude(0.011)
    cap = cap.cut(channel)
    slot = (
        cq.Workplane("XY")
        .workplane(offset=head_h + 0.001)
        .rect(0.028, 0.003)
        .extrude(-0.006)
    )
    return cap.cut(slot)


# pistol-grip geometry constants (grip-local frame, origin at clamp center)
def _pistol_constants(r: ResolvedContainerPaintSprayConfig) -> dict:
    grip_clamp_h = 0.034
    grip_half_h = grip_clamp_h / 2.0
    grip_inner_r = r.clamp_inner_r
    grip_outer_r = grip_inner_r + 0.005
    # plunger reaches up to the dome top over the valve.
    arm_h = max(r.dome_top - (r.grip_center_z + grip_half_h), 0.012)
    handle_cx = -(grip_outer_r + 0.012) - 0.030
    handle_top_z = -grip_half_h - 0.034 + 0.003
    return {
        "clamp_h": grip_clamp_h,
        "half_h": grip_half_h,
        "inner_r": grip_inner_r,
        "outer_r": grip_outer_r,
        "arm_h": arm_h,
        # Pivot kept well outboard of the can wall so the forward-curling
        # trigger blade clears the can body across its full swing.
        "pivot_x": -(grip_outer_r + 0.030),
        "pivot_z": -grip_half_h - 0.008,
        "handle_cx": handle_cx,
        "handle_top_z": handle_top_z,
        "rake_deg": 13.0,
    }


def _pistol_grip_solid(r: ResolvedContainerPaintSprayConfig, c: dict) -> cq.Workplane:
    """Clip-on pistol grip adapter (pistol src). Origin at clamp center, +Z up,
    C-opening on +X, handle raked back, linkage arm + bridge + plunger on -X."""
    half_h = c["half_h"]
    outer_r = c["outer_r"]
    inner_r = c["inner_r"]
    clamp_h = c["clamp_h"]
    rake_deg = c["rake_deg"]
    rake_sin = math.sin(math.radians(rake_deg))
    handle_cx = c["handle_cx"]
    handle_top_z = c["handle_top_z"]
    handle_w, handle_d, handle_h = 0.024, 0.044, 0.072

    def _rake(solid):
        return solid.rotate(
            (handle_cx, -1.0, handle_top_z),
            (handle_cx, 1.0, handle_top_z),
            rake_deg,
        )

    collar = (
        cq.Workplane("XY").workplane(offset=-half_h).circle(outer_r).extrude(clamp_h)
    )
    collar = collar.cut(
        cq.Workplane("XY")
        .workplane(offset=-half_h - 0.001)
        .circle(inner_r)
        .extrude(clamp_h + 0.002)
    )
    collar = collar.cut(
        cq.Workplane("XY")
        .workplane(offset=-half_h - 0.001)
        .center(outer_r * 0.55, 0)
        .rect(outer_r * 1.2, outer_r * 0.90)
        .extrude(clamp_h + 0.002)
    )

    back_plate_x = -outer_r + 0.004
    back_plate_w = 0.010
    back_plate_h = 0.034
    back_plate = (
        cq.Workplane("XY")
        .workplane(offset=-half_h - back_plate_h + 0.001)
        .center(back_plate_x - back_plate_w / 2.0, 0)
        .box(back_plate_w, 0.030, back_plate_h + half_h + 0.002, centered=(True, True, False))
    )

    handle = (
        cq.Workplane("XY")
        .workplane(offset=-half_h - back_plate_h - handle_h + 0.001)
        .center(handle_cx, 0)
        .box(handle_w, handle_d, handle_h + 0.002, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.007)
    )
    handle = _rake(handle)

    web_front_x = back_plate_x - back_plate_w
    web_back_x = handle_cx + handle_w / 2.0 + 0.006
    web_span = abs(web_front_x - web_back_x) + 0.002
    web_cx = (web_front_x + web_back_x) / 2.0
    web_z = -half_h - back_plate_h - 0.004
    side_web_plus = (
        cq.Workplane("XY")
        .workplane(offset=web_z)
        .center(web_cx, 0.014)
        .box(web_span, 0.006, 0.010, centered=(True, True, False))
    )
    side_web_minus = (
        cq.Workplane("XY")
        .workplane(offset=web_z)
        .center(web_cx, -0.014)
        .box(web_span, 0.006, 0.010, centered=(True, True, False))
    )

    guard_x = -outer_r - 0.004
    guard_front = (
        cq.Workplane("XY")
        .workplane(offset=-half_h - back_plate_h - 0.038)
        .center(guard_x, 0)
        .box(0.006, 0.026, 0.038, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.002)
    )
    guard_z = -half_h - back_plate_h - 0.038
    handle_x_at_guard = handle_cx - (handle_top_z - guard_z) * rake_sin
    guard_bridge = (
        cq.Workplane("XY")
        .workplane(offset=guard_z)
        .center((handle_x_at_guard + guard_x) / 2.0, 0)
        .box(abs(guard_x - handle_x_at_guard) + 0.008, 0.026, 0.005, centered=(True, True, False))
    )

    arm_x = -(outer_r + 0.002)
    arm_h = c["arm_h"]
    linkage_arm = (
        cq.Workplane("XY")
        .workplane(offset=-0.005)
        .center(arm_x, 0)
        .box(0.012, 0.014, half_h + arm_h + 0.005, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.002)
    )
    bridge_z = half_h + arm_h - 0.006
    bridge_len = abs(arm_x) + 0.006
    bridge = (
        cq.Workplane("XY")
        .workplane(offset=bridge_z)
        .center(arm_x / 2.0 + 0.002, 0)
        .box(bridge_len, 0.012, 0.005, centered=(True, True, False))
    )
    plunger = cq.Workplane("XY").workplane(offset=bridge_z).circle(0.006).extrude(0.008)

    pivot_x = c["pivot_x"]
    pivot_z = c["pivot_z"]
    ear_w, ear_t, ear_gap, ear_depth = 0.014, 0.008, 0.005, 0.014
    ear_z_top = pivot_z + 0.005
    ear_plus = (
        cq.Workplane("XY")
        .workplane(offset=ear_z_top - ear_depth)
        .center(pivot_x, ear_gap + ear_t / 2.0)
        .box(ear_w, ear_t, ear_depth, centered=(True, True, False))
    )
    ear_minus = (
        cq.Workplane("XY")
        .workplane(offset=ear_z_top - ear_depth)
        .center(pivot_x, -(ear_gap + ear_t / 2.0))
        .box(ear_w, ear_t, ear_depth, centered=(True, True, False))
    )
    # Ear support strut: bridges the pivot ears back to the guard/back-plate
    # region so the outboard ears are never a disconnected island when the pivot
    # is pushed out to clear the trigger blade.
    strut_back_x = -outer_r + 0.003  # bite into the collar wall for a solid join
    strut_span = abs(strut_back_x - pivot_x) + ear_w
    strut_cx = (strut_back_x + pivot_x) / 2.0
    ear_strut = (
        cq.Workplane("XY")
        .workplane(offset=ear_z_top - ear_depth)
        .center(strut_cx, 0)
        .box(strut_span, 0.016, ear_depth * 0.8, centered=(True, True, False))
    )

    # Mount lug: a thin solid web on the -X side bridging from the collar inner
    # wall toward the can axis at clamp height. It gives the grip real geometry
    # near the grip-local origin so the FIXED grip_mount origin (placed on the
    # -X can wall) lies on solid grip material, not in the hollow C-bore.
    mount_lug = (
        cq.Workplane("XY")
        .workplane(offset=-half_h * 0.6)
        .center(-inner_r * 0.5, 0)
        .box(inner_r, 0.012, half_h * 1.2, centered=(True, True, False))
    )

    grip = collar.union(back_plate).union(handle)
    grip = grip.union(side_web_plus).union(side_web_minus)
    grip = grip.union(guard_front).union(guard_bridge)
    grip = grip.union(linkage_arm).union(bridge).union(plunger)
    grip = grip.union(ear_plus).union(ear_minus).union(ear_strut).union(mount_lug)
    return grip


def _grip_rib_solid(c: dict, z_offset: float) -> cq.Workplane:
    """Split handle grip rib (pistol src), raked with the handle."""
    handle_cx = c["handle_cx"]
    handle_top_z = c["handle_top_z"]
    rake_deg = c["rake_deg"]
    handle_w = 0.024
    rib_x = handle_cx - handle_w / 2.0 - 0.002
    total_y, slot_y = 0.044, 0.026
    side_y = (total_y - slot_y) / 2.0
    offset_y = slot_y / 2.0 + side_y / 2.0
    rib_plus = (
        cq.Workplane("XY")
        .workplane(offset=z_offset)
        .center(rib_x, offset_y)
        .box(0.004, side_y, 0.004, centered=(True, True, False))
        .edges(">Z").fillet(0.001)
    )
    rib_minus = (
        cq.Workplane("XY")
        .workplane(offset=z_offset)
        .center(rib_x, -offset_y)
        .box(0.004, side_y, 0.004, centered=(True, True, False))
        .edges(">Z").fillet(0.001)
    )
    combined = rib_plus.union(rib_minus)
    return combined.rotate(
        (handle_cx, -1.0, handle_top_z),
        (handle_cx, 1.0, handle_top_z),
        rake_deg,
    )


def _trigger_solid() -> cq.Workplane:
    """Curved trigger blade, origin at the pivot (pistol src)."""
    blade = (
        cq.Workplane("XY")
        .workplane(offset=0.004)
        .rect(0.007, 0.016)
        .workplane(offset=-0.024)
        .rect(0.007, 0.018)
        .workplane(offset=-0.020)
        .center(0.001, 0)
        .rect(0.008, 0.020)
        .workplane(offset=-0.018)
        .center(0.003, 0)
        .rect(0.010, 0.022)
        .loft(ruled=False)
    )
    boss = cq.Workplane("XZ").workplane(offset=-0.010).circle(0.005).extrude(0.020)
    return blade.union(boss)


# ===========================================================================
# Slot A — closure cap solids
# ===========================================================================
def _dust_cap_solid(r: ResolvedContainerPaintSprayConfig, *, cap_h: float) -> cq.Workplane:
    """Hollow dust cap shell with a closed domed top (parent ``_dust_cap_solid``).

    For the oval body the rim follows the ellipse (oval source pattern)."""
    if r.body_section == "oval_section":
        # Bore set with a hair of interference (inner skirt wall just inside the
        # body wall) so the cap is in real contact and never support-isolated.
        cap_rx = r.can_rx - 0.0004
        cap_ry = r.can_ry - 0.0004
        outer_rx = cap_rx + 0.0012
        outer_ry = cap_ry + 0.0012
        outer = cq.Workplane("XY").ellipse(outer_rx, outer_ry).extrude(cap_h - 0.010)
        top = (
            cq.Workplane("XY")
            .workplane(offset=cap_h - 0.011)
            .ellipse(outer_rx, outer_ry)
            .workplane(offset=0.007)
            .ellipse(max(outer_rx - 0.0075, 0.004), max(outer_ry - 0.0075, 0.004))
            .workplane(offset=0.004)
            .circle(0.010)
            .loft(ruled=False)
        )
        cap = outer.union(top)
        bore = (
            cq.Workplane("XY")
            .workplane(offset=-0.001)
            .ellipse(cap_rx, cap_ry)
            .extrude(cap_h - 0.014)
        )
        return cap.cut(bore)

    outer_r = r.cap_bore_r + 0.0006  # thin wall over the bore
    outer = cq.Workplane("XY").circle(outer_r).extrude(cap_h - 0.010)
    top = (
        cq.Workplane("XY")
        .workplane(offset=cap_h - 0.011)
        .circle(outer_r)
        .workplane(offset=0.007)
        .circle(max(outer_r - 0.0075, 0.004))
        .workplane(offset=0.004)
        .circle(0.010)
        .loft(ruled=False)
    )
    cap = outer.union(top)
    bore = (
        cq.Workplane("XY")
        .workplane(offset=-0.001)
        .circle(r.cap_bore_r - 0.0006)
        .extrude(cap_h - 0.014)
    )
    return cap.cut(bore)


def _flip_cap_solid(r: ResolvedContainerPaintSprayConfig, *, cap_h: float, hinge_y: float) -> cq.Workplane:
    """One-piece flip-top cap, origin at the hinge pin center (flip src).

    cap_center_y = -hinge_y places the can center in the cap local frame. The
    outer shell is a SINGLE extrude of a combined 2D footprint (the cap disc
    hulled with a rear hinge tab reaching the hinge axis), so it tessellates as
    one connected mesh — a boolean-union neck on a finished solid splits into a
    disconnected facet island in the mesh export."""
    cy = -hinge_y
    cap_skirt = 0.003
    cap_wall = 0.003
    # Build the outer shell, UNION the rear hinge mount block while the shell is
    # still solid (so the bore cut never severs the mount<->shell link), THEN
    # cut the bore. The bore is OPEN at the underside (starts below z=0) so the
    # cap is a real open-bottomed cup that sleeves over the can; a blind internal
    # cavity would export as a second disconnected shell (the island bug).
    bore_start = -cap_skirt - 0.002
    bore_top = cap_h - 0.004
    # A round flip cap (radius covers the body footprint) is used for every
    # section. For the oval body the cap radius covers the wider X axis so the
    # mouth is fully capped; the round cup is robust to tessellate (a section-
    # specific oval cup split into 2 mesh shells / left the hinge mount severed).
    cap_r = r.cap_bore_r + 0.0006
    outer = (
        cq.Workplane("XY")
        .workplane(offset=-cap_skirt)
        .center(0, cy)
        .circle(cap_r)
        .extrude(cap_h + cap_skirt)
    )
    outer = outer.edges(">Z").fillet(0.003)
    bore = (
        cq.Workplane("XY")
        .workplane(offset=bore_start)
        .center(0, cy)
        .circle(cap_r - cap_wall)
        .extrude(bore_top - bore_start)
    )
    outer = outer.cut(bore)
    # Hinge mount added AFTER the bore so it solidly bridges the hinge axis to
    # the (now hollow) cup wall without being severed by the bore.
    mount = (
        cq.Workplane("XY")
        .workplane(offset=-cap_skirt)
        .center(0, cy / 2.0)
        .box(0.018, cy + cap_r, 0.012, centered=(True, True, False))
    )
    return outer.union(mount)


def _hinge_ear_solid(*, depth: float = 0.014) -> cq.Workplane:
    """Hinge ear tab, origin at base center, extends +Z (flip src). The Y depth
    is deep enough to embed into the can wall so the ear contacts the body."""
    ear = cq.Workplane("XY").box(0.005, depth, 0.012, centered=(True, True, False))
    return ear.edges(">Z").fillet(0.0018)


def _collar_solid(r: ResolvedContainerPaintSprayConfig, *, collar_h: float) -> cq.Workplane:
    """Threaded collar ring on the shoulder, origin at its base (screw src)."""
    collar_outer_r = 0.0225
    collar_inner_r = 0.0130
    n_ridges = 4
    ridge_h = 0.0014
    ridge_d = 0.0010
    collar = (
        cq.Workplane("XY").circle(collar_outer_r).circle(collar_inner_r).extrude(collar_h)
    )
    pitch = collar_h / (n_ridges + 1)
    for i in range(n_ridges):
        z = pitch * (i + 1)
        ridge = (
            cq.Workplane("XY")
            .workplane(offset=z - ridge_h / 2)
            .circle(collar_outer_r + ridge_d)
            .circle(collar_outer_r - 0.0003)
            .extrude(ridge_h)
        )
        collar = collar.union(ridge)
    return collar


def _screw_cap_solid(r: ResolvedContainerPaintSprayConfig, *, cap_h: float) -> cq.Workplane:
    """Knurled threaded screw cap with a domed top + collar-clearance bore (screw src)."""
    cap_outer_r = 0.0305
    cap_bore_r = 0.0225 + 0.0010 - 0.0002  # clears collar + thread ridges
    outer = cq.Workplane("XY").circle(cap_outer_r).extrude(cap_h - 0.010)
    dome = (
        cq.Workplane("XY")
        .workplane(offset=cap_h - 0.011)
        .circle(cap_outer_r)
        .workplane(offset=0.006)
        .circle(cap_outer_r - 0.004)
        .workplane(offset=0.004)
        .circle(0.012)
        .loft(ruled=False)
    )
    cap = outer.union(dome)
    bore = (
        cq.Workplane("XY")
        .workplane(offset=-0.001)
        .circle(cap_bore_r)
        .extrude(cap_h - 0.012)
    )
    cap = cap.cut(bore)
    rib_count = 14
    for i in range(rib_count):
        ang = 360.0 * i / rib_count
        rib = (
            cq.Workplane("XY")
            .workplane(offset=0.008)
            .center(cap_outer_r + 0.0007, 0)
            .box(0.0018, 0.0045, cap_h - 0.020, centered=(True, True, False))
            .edges("|Z")
            .fillet(0.0005)
        )
        rib = rib.rotate((0, 0, 0), (0, 0, 1), ang)
        cap = cap.union(rib)
    return cap


def _collar_ring_solid(*, collar_inner_r: float, collar_outer_r: float, collar_h: float, tab_w: float) -> cq.Workplane:
    """Low retaining collar annulus + a +Y slider guide block (no_cap src)."""
    ring = (
        cq.Workplane("XY").circle(collar_outer_r).circle(collar_inner_r).extrude(collar_h)
    )
    guide = (
        cq.Workplane("XY")
        .center(0, collar_outer_r + 0.003)
        .box(tab_w + 0.005, 0.012, collar_h, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.001)
    )
    return ring.union(guide)


def _grip_ridge_solid(collar_h: float) -> cq.Workplane:
    return cq.Workplane("XY").box(0.003, 0.002, collar_h * 0.85, centered=(True, True, False))


def _place_grip_ridge(index: int, total: int, *, collar_outer_r: float, base_z: float) -> cq.Workplane:
    angle = 2.0 * math.pi * index / total
    r_center = collar_outer_r + 0.0005
    gx = r_center * math.cos(angle)
    gy = r_center * math.sin(angle)
    ridge = _grip_ridge_solid(0.0055)
    ridge = ridge.rotate((0, 0, 0), (0, 0, 1), math.degrees(angle))
    return ridge.translate((gx, gy, base_z))


def _lock_tab_solid(*, tab_w: float, tab_l: float, tab_h: float) -> cq.Workplane:
    """Sliding lock tab: low shelf + outside thumb nub + capture tongue (no_cap src)."""
    tab = (
        cq.Workplane("XY")
        .box(tab_w, tab_l, tab_h, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.001)
    )
    nub = (
        cq.Workplane("XY")
        .workplane(offset=tab_h - 0.0003)
        .center(0, tab_l * 0.30)
        .box(tab_w * 0.65, tab_l * 0.28, 0.002, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.0008)
    )
    tab = tab.union(nub)
    tongue = (
        cq.Workplane("XY")
        .workplane(offset=-0.0025)
        .center(0, -tab_l * 0.18)
        .box(tab_w * 0.55, tab_l * 0.55, 0.0025, centered=(True, True, False))
    )
    return tab.union(tongue)


# ===========================================================================
# Actuator builders (parent directly to can_body, parallel children)
# ===========================================================================
def _build_press_button(model, body, r, *, accent_mat) -> None:
    nozzle = model.part("spray_nozzle")
    nozzle.visual(
        mesh_from_cadquery(_nozzle_solid(), "spray_nozzle"), material=accent_mat, name="spray_nozzle", material_class_id="plastic.opaque_glossy_molded"
    )
    nozzle.inertial = Inertial.from_geometry(
        Box((0.018, 0.016, 0.014)), mass=0.004, origin=Origin(xyz=(0.0, 0.0, 0.007))
    )
    model.articulation(
        "nozzle_press",
        ArticulationType.PRISMATIC,
        parent=body,
        child=nozzle,
        origin=Origin(xyz=(0.0, 0.0, r.seat_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.05, lower=0.0, upper=r.press_travel),
    )


def _build_trigger_lever(model, body, r, *, accent_mat, housing_mat) -> None:
    # Fixed housing visual on the dome top.
    body.visual(
        mesh_from_cadquery(_trigger_housing_solid(), "trigger_housing"),
        material=housing_mat,
        origin=Origin(xyz=(0.0, 0.0, r.dome_top)),
        name="trigger_housing", material_class_id="plastic.opaque_glossy_molded",
    )
    trigger = model.part("trigger_lever")
    trigger.visual(
        mesh_from_cadquery(_trigger_lever_solid(), "trigger_lever"),
        material=accent_mat,
        name="trigger_lever", material_class_id="plastic.opaque_glossy_molded",
    )
    trigger.inertial = Inertial.from_geometry(
        Box((0.018, 0.018, 0.032)), mass=0.006, origin=Origin(xyz=(0.008, 0.0, -0.016))
    )
    pivot_z = r.dome_top + 0.024  # housing top
    model.articulation(
        "trigger_squeeze",
        ArticulationType.REVOLUTE,
        parent=body,
        child=trigger,
        origin=Origin(xyz=(0.002, 0.0, pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=5.0, velocity=2.0, lower=0.0, upper=0.45 * r.actuator_press_scale
        ),
    )


def _build_pistol_grip(model, body, r, *, grip_mat, accent_mat) -> None:
    c = _pistol_constants(r)
    # FIXED clamp mount onto the can wall. Justified: the grip is a separate
    # rigid kinematic sub-assembly (it carries its own REVOLUTE trigger child),
    # so it needs an independent reference frame. The joint origin must sit on
    # real geometry on BOTH sides within 15 mm, so it is placed on the -X can
    # wall (NOT on the axis, which is 32 mm from the can wall). The grip mesh is
    # therefore authored about the clamp center then shifted by +anchor so the
    # clamp re-centers on the can axis after the off-axis origin is applied; the
    # grip mount lug passes through grip-local x=0 so child geometry sits at the
    # origin too.
    anchor = max(r.can_r, r.can_rx) - 0.002  # -X can-wall offset
    grip = model.part("pistol_grip")
    grip_solid = _pistol_grip_solid(r, c).translate((anchor, 0.0, 0.0))
    grip.visual(
        mesh_from_cadquery(grip_solid, "pistol_grip_body"),
        material=grip_mat,
        name="pistol_grip_body", material_class_id="plastic.opaque_glossy_molded",
    )
    rib_z_offsets = [-0.058 - i * 0.014 for i in range(4)]
    for i, z_off in enumerate(rib_z_offsets):
        rib_solid = _grip_rib_solid(c, z_off).translate((anchor, 0.0, 0.0))
        grip.visual(
            mesh_from_cadquery(rib_solid, f"grip_rib_{i}"),
            material=grip_mat,
            name=f"grip_rib_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    grip.inertial = Inertial.from_geometry(
        Box((0.060, 0.030, 0.120)), mass=0.080, origin=Origin(xyz=(anchor - 0.020, 0.0, -0.030))
    )
    model.articulation(
        "grip_mount",
        ArticulationType.FIXED,
        parent=body,
        child=grip,
        origin=Origin(xyz=(-anchor, 0.0, r.grip_center_z)),
    )

    trigger = model.part("trigger")
    # The trigger is its OWN part whose frame sits at the joint origin (its
    # pivot). Author it about trigger-local (0,0,0) = pivot WITHOUT the grip's
    # +anchor shift, so its pivot boss lands on the child-frame origin. The
    # joint origin in grip-local coords is the (shifted) grip pivot ears.
    trigger.visual(
        mesh_from_cadquery(_trigger_solid(), "trigger_lever"),
        material=accent_mat,
        name="trigger_lever", material_class_id="plastic.opaque_glossy_molded",
    )
    trigger.inertial = Inertial.from_geometry(
        Box((0.012, 0.022, 0.062)), mass=0.008, origin=Origin(xyz=(0.002, 0.0, -0.027))
    )
    model.articulation(
        "trigger_pull",
        ArticulationType.REVOLUTE,
        parent=grip,
        child=trigger,
        origin=Origin(xyz=(c["pivot_x"] + anchor, 0.0, c["pivot_z"])),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=5.0, velocity=2.0, lower=0.0, upper=0.26 * r.actuator_press_scale
        ),
    )


def _build_fan_spin_cap(model, body, r, *, accent_mat, fan_mat) -> None:
    stem_height = 0.010
    stem = model.part("fan_cap_stem")
    stem.visual(
        mesh_from_cadquery(_fan_cap_stem_solid(), "fan_cap_stem"),
        material=accent_mat,
        name="fan_cap_stem", material_class_id="plastic.opaque_glossy_molded",
    )
    stem.inertial = Inertial.from_geometry(
        Cylinder(0.012, stem_height), mass=0.003, origin=Origin(xyz=(0.0, 0.0, stem_height / 2.0))
    )
    model.articulation(
        "fan_cap_press",
        ArticulationType.PRISMATIC,
        parent=body,
        child=stem,
        origin=Origin(xyz=(0.0, 0.0, r.seat_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.05, lower=0.0, upper=r.press_travel),
    )

    head = model.part("fan_cap")
    head.visual(
        mesh_from_cadquery(_fan_cap_head_solid(), "fan_cap"), material=fan_mat, name="fan_cap", material_class_id="plastic.opaque_glossy_molded"
    )
    head.inertial = Inertial.from_geometry(
        Box((0.040, 0.026, 0.014)), mass=0.005, origin=Origin(xyz=(0.0, 0.0, 0.007))
    )
    model.articulation(
        "fan_cap_twist",
        ArticulationType.REVOLUTE,
        parent=stem,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, stem_height)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=1.5708),
    )


# ===========================================================================
# Closure-cap builders (parent directly to can_body, parallel children)
# ===========================================================================
def _build_lift_off_cap(model, body, r, *, cap_mat) -> None:
    cap_h = (r.actuator_top_z - r.cap_seat_z + 0.020) * r.cap_height_scale
    # Anchor the +Z prismatic origin on the cap-seat WALL (radius cap_seat_r) so
    # the origin sits on real glass on the parent side; offset the cap mesh by
    # -anchor so the cap stays centered on +Z. The cap skirt wall passes through
    # local x=0 because of the shift, so child geometry sits at the origin too.
    anchor = r.cap_seat_r
    cap = model.part("dust_cap")
    cap_solid = _dust_cap_solid(r, cap_h=cap_h).translate((-anchor, 0.0, 0.0))
    cap.visual(mesh_from_cadquery(cap_solid, "dust_cap"), material=cap_mat, name="dust_cap", material_class_id="plastic.opaque_glossy_molded")
    cap.inertial = Inertial.from_geometry(
        Cylinder(r.cap_bore_r + 0.0006, cap_h),
        mass=0.015,
        origin=Origin(xyz=(-anchor, 0.0, cap_h / 2.0)),
    )
    model.articulation(
        "cap_lift",
        ArticulationType.PRISMATIC,
        parent=body,
        child=cap,
        origin=Origin(xyz=(anchor, 0.0, r.cap_seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.2, lower=0.0, upper=r.cap_lift_travel),
    )


def _build_flip_top_cap(model, body, r, *, cap_mat, hinge_mat) -> None:
    cap_h = (r.actuator_top_z - r.cap_seat_z + 0.018) * r.cap_height_scale
    # Hinge on the rear (-Y) rim. It must sit on the actual -Y wall radius: for
    # the oval body that is the NARROW can_ry (not the wide cap_seat_r=can_rx),
    # else the ears float off the rear wall. The round cap (radius covers the
    # wide axis) still caps the mouth when centered on this hinge.
    hinge_offset = 0.005
    if r.body_section == "oval_section":
        hinge_wall_r = r.can_ry
    else:
        hinge_wall_r = r.cap_seat_r
    hinge_y = -(hinge_wall_r + hinge_offset)
    hinge_z = r.cap_seat_z
    # Two fixed hinge ear visuals on the body rear rim. Deep, and shifted so the
    # inner half embeds into the can wall (real contact even at the off-center x
    # positions where the round wall curves forward).
    ear_spacing = min(0.022, r.cap_seat_r * 1.2)
    ear_depth = 0.020
    # Place the ear so its inner face reaches ~3 mm past the wall radius.
    ear_center_y = hinge_y + (ear_depth / 2.0) - 0.008
    for i in range(2):
        x_off = -ear_spacing / 2.0 + i * ear_spacing
        body.visual(
            mesh_from_cadquery(_hinge_ear_solid(depth=ear_depth), f"hinge_ear_{i}"),
            material=hinge_mat,
            origin=Origin(xyz=(x_off, ear_center_y, hinge_z)),
            name=f"hinge_ear_{i}", material_class_id="metal.paint_coated",
        )
    cap = model.part("flip_cap")
    cap.visual(
        mesh_from_cadquery(_flip_cap_solid(r, cap_h=cap_h, hinge_y=hinge_y), "flip_cap"),
        material=cap_mat,
        name="flip_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(r.cap_bore_r + 0.0006, cap_h),
        mass=0.015,
        origin=Origin(xyz=(0.0, -hinge_y, cap_h / 2.0)),
    )
    model.articulation(
        "cap_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=cap,
        origin=Origin(xyz=(0.0, hinge_y, hinge_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=2.6),
    )


def _build_screw_cap(model, body, r, *, cap_mat, collar_mat) -> None:
    collar_h = 0.024
    # Seat the collar base BELOW the dome top so its lower ring embeds into the
    # crimped dome / valve cup (real contact), not floating above it.
    collar_bottom = r.dome_top - 0.006
    # Fixed threaded collar visual on the shoulder.
    body.visual(
        mesh_from_cadquery(_collar_solid(r, collar_h=collar_h), "threaded_collar"),
        material=collar_mat,
        origin=Origin(xyz=(0.0, 0.0, collar_bottom)),
        name="threaded_collar", material_class_id="metal.paint_coated",
    )
    cap_h = (r.actuator_top_z - r.cap_seat_z + 0.030) * r.cap_height_scale
    # massless carrier link decouples rotate -> lift.
    carrier = model.part("cap_carrier")
    carrier.inertial = Inertial.from_geometry(Box((0.006, 0.006, 0.006)), mass=1e-4)

    cap = model.part("screw_cap")
    cap.visual(
        mesh_from_cadquery(_screw_cap_solid(r, cap_h=cap_h), "screw_cap"),
        material=cap_mat,
        name="screw_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(0.0305, cap_h), mass=0.018, origin=Origin(xyz=(0.0, 0.0, cap_h / 2.0))
    )
    model.articulation(
        "cap_unscrew",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=carrier,
        origin=Origin(xyz=(0.0, 0.0, r.cap_seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0),
    )
    model.articulation(
        "cap_lift",
        ArticulationType.PRISMATIC,
        parent=carrier,
        child=cap,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=5.0, velocity=0.20, lower=0.0, upper=r.cap_lift_travel
        ),
    )


def _build_no_cap_collar(model, body, r, *, collar_mat, tab_mat) -> None:
    collar_inner_r = 0.0145
    collar_outer_r = 0.0190
    collar_h = 0.0055
    collar_base_z = r.dome_top - 0.0090
    tab_w, tab_l, tab_h = 0.011, 0.014, 0.0023
    tab_slide = 0.0165

    # Fixed collar ring visual.
    collar_ring = _collar_solid_no_cap(
        collar_inner_r=collar_inner_r,
        collar_outer_r=collar_outer_r,
        collar_h=collar_h,
        tab_w=tab_w,
    ).translate((0, 0, collar_base_z))
    body.visual(
        mesh_from_cadquery(collar_ring, "collar_ring"), material=collar_mat, name="collar_ring", material_class_id="metal.paint_coated"
    )
    # 6 grip ridges.
    n_grips = 6
    for i in range(n_grips):
        ridge = _place_grip_ridge(
            i, n_grips, collar_outer_r=collar_outer_r, base_z=collar_base_z
        )
        body.visual(
            mesh_from_cadquery(ridge, f"grip_ridge_{i}"), material=collar_mat, name=f"grip_ridge_{i}", material_class_id="metal.paint_coated"
        )

    tab_top_z = r.seat_z - 0.0005
    tab_base_z = tab_top_z - tab_h
    tab_origin_y = collar_outer_r + tab_l / 2.0 + 0.002
    lock_tab = model.part("lock_tab")
    lock_tab.visual(
        mesh_from_cadquery(
            _lock_tab_solid(tab_w=tab_w, tab_l=tab_l, tab_h=tab_h), "lock_tab"
        ),
        material=tab_mat,
        name="lock_tab", material_class_id="plastic.opaque_glossy_molded",
    )
    lock_tab.inertial = Inertial.from_geometry(
        Box((tab_w, tab_l, tab_h + 0.002)),
        mass=0.002,
        origin=Origin(xyz=(0.0, 0.0, (tab_h + 0.002) / 2.0)),
    )
    model.articulation(
        "tab_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=lock_tab,
        origin=Origin(xyz=(0.0, tab_origin_y, tab_base_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=0.05, lower=0.0, upper=tab_slide),
    )


def _collar_solid_no_cap(*, collar_inner_r, collar_outer_r, collar_h, tab_w) -> cq.Workplane:
    return _collar_ring_solid(
        collar_inner_r=collar_inner_r,
        collar_outer_r=collar_outer_r,
        collar_h=collar_h,
        tab_w=tab_w,
    )


# ===========================================================================
# Build entry point
# ===========================================================================
def build_container_paint_spray(
    config: ContainerPaintSprayConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    metal_mat = model.material(f"cps_metal_{r.palette_style}", rgba=pal.metal)
    label_mat = model.material(f"cps_label_{r.palette_style}", rgba=pal.label)
    cap_mat = model.material(f"cps_cap_{r.palette_style}", rgba=pal.cap)
    accent_mat = model.material(f"cps_accent_{r.palette_style}", rgba=pal.accent)

    # --- ROOT: can body --------------------------------------------------
    body = model.part("can_body")
    _emit_body(body, r, metal_mat=metal_mat, label_mat=label_mat)

    # --- actuator (parallel child) ---------------------------------------
    if r.actuator == "press_button":
        _build_press_button(model, body, r, accent_mat=accent_mat)
    elif r.actuator == "trigger_lever":
        _build_trigger_lever(model, body, r, accent_mat=accent_mat, housing_mat=cap_mat)
    elif r.actuator == "pistol_grip":
        _build_pistol_grip(model, body, r, grip_mat=cap_mat, accent_mat=accent_mat)
    elif r.actuator == "fan_spin_cap":
        _build_fan_spin_cap(model, body, r, accent_mat=accent_mat, fan_mat=cap_mat)

    # --- closure cap (parallel child) ------------------------------------
    if r.closure_cap == "lift_off_cap":
        _build_lift_off_cap(model, body, r, cap_mat=cap_mat)
    elif r.closure_cap == "flip_top_cap":
        _build_flip_top_cap(model, body, r, cap_mat=cap_mat, hinge_mat=accent_mat)
    elif r.closure_cap == "screw_cap":
        _build_screw_cap(model, body, r, cap_mat=cap_mat, collar_mat=accent_mat)
    elif r.closure_cap == "no_cap_collar":
        _build_no_cap_collar(model, body, r, collar_mat=cap_mat, tab_mat=accent_mat)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_paint_spray(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_paint_spray(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests / QC. Captured-fit overlaps (nozzle on valve, cap skirt over shoulder,
# clamp on wall, tab in collar, hinge ear through cap, lever in housing, dust
# cap over the mechanism) are declared element-scoped so the sweep's
# island/overlap checks pass; each mechanism's motion is exercised.
# ===========================================================================
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_paint_spray_tests(
    object_model: ArticulatedObject,
    config: ContainerPaintSprayConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("can_body")

    # ---- can body is a tall slim cylinder, base near z=0 ----
    bmn, bmx = ctx.part_world_aabb(body)
    height = bmx[2] - bmn[2]
    dia_x = bmx[0] - bmn[0]
    dia_y = bmx[1] - bmn[1]
    ctx.check(
        "can body rests on the ground (base near z=0)",
        abs(bmn[2]) < 0.012,
        details=f"body min z={bmn[2]:.4f}",
    )
    ctx.check(
        "can body is a tall slim can (height>0.16, slim, height>dia*1.8)",
        height > 0.16
        and 0.045 < dia_x < 0.10
        and 0.035 < dia_y < 0.10
        and height > max(dia_x, dia_y) * 1.8,
        details=f"height={height:.3f}, dia_x={dia_x:.3f}, dia_y={dia_y:.3f}",
    )

    # ---- actuator: action + captured-fit ----
    if r.actuator == "press_button":
        nozzle = object_model.get_part("spray_nozzle")
        nozzle_press = object_model.get_articulation("nozzle_press")
        ctx.allow_overlap(
            nozzle, body, elem_a="spray_nozzle", elem_b="can_body",
            reason="The spray button is intentionally seated over the central valve stem.",
        )
        ctx.check(
            "nozzle_press is PRISMATIC -Z",
            nozzle_press.articulation_type == ArticulationType.PRISMATIC
            and nozzle_press.axis[2] < -0.99,
            details=f"axis={nozzle_press.axis}, type={nozzle_press.articulation_type}",
        )
        nz_rest = ctx.part_world_position(nozzle)[2]
        with ctx.pose({nozzle_press: r.press_travel}):
            nz_down = ctx.part_world_position(nozzle)[2]
        ctx.check(
            "nozzle button presses straight down",
            nz_down < nz_rest - r.press_travel * 0.7,
            details=f"rest_z={nz_rest:.4f}, pressed_z={nz_down:.4f}",
        )

    elif r.actuator == "trigger_lever":
        trigger = object_model.get_part("trigger_lever")
        squeeze = object_model.get_articulation("trigger_squeeze")
        ctx.allow_overlap(
            trigger, body, elem_a="trigger_lever", elem_b="trigger_housing",
            reason="Trigger lever pivot bushing is nested in the housing ear boss.",
        )
        ctx.allow_overlap(
            trigger, body, elem_a="trigger_lever", elem_b="can_body",
            reason="Trigger lever swings near the valve stem at the dome.",
        )
        ctx.check(
            "trigger_squeeze is REVOLUTE +Y",
            squeeze.articulation_type == ArticulationType.REVOLUTE
            and abs(squeeze.axis[1]) > 0.9,
            details=f"axis={squeeze.axis}, type={squeeze.articulation_type}",
        )
        ctx.check(
            "trigger housing visual exists on the can body",
            body.get_visual("trigger_housing") is not None,
            details="trigger_housing visual not found",
        )
        rest_mn, rest_mx = ctx.part_world_aabb(trigger)
        with ctx.pose({squeeze: 0.40 * r.actuator_press_scale}):
            sq_mn, sq_mx = ctx.part_world_aabb(trigger)
        ctx.check(
            "trigger squeeze swings the lever in and down",
            sq_mn[0] < rest_mn[0] - 0.002 and sq_mn[2] < rest_mn[2] - 0.002,
            details=f"rest=({rest_mn[0]:.4f},{rest_mn[2]:.4f}), sq=({sq_mn[0]:.4f},{sq_mn[2]:.4f})",
        )

    elif r.actuator == "pistol_grip":
        grip = object_model.get_part("pistol_grip")
        trigger = object_model.get_part("trigger")
        grip_mount = object_model.get_articulation("grip_mount")
        trigger_pull = object_model.get_articulation("trigger_pull")
        ctx.allow_overlap(
            grip, body, elem_a="pistol_grip_body", elem_b="can_body",
            reason="The grip C-clamp collar wraps around the can body wall.",
        )
        ctx.allow_overlap(
            grip, body, elem_a="pistol_grip_body", elem_b="label_band",
            reason="The grip C-clamp collar sleeves over the label band region.",
        )
        ctx.allow_overlap(
            grip, trigger, elem_a="pistol_grip_body", elem_b="trigger_lever",
            reason="Trigger pivot boss is seated between the grip pivot ears (bearing fit).",
        )
        # The grip's linkage bridge / plunger reaches over the valve at the dome,
        # where a screw threaded_collar or no_cap collar_ring sits (captured fit).
        _body_visual_names = {v.name for v in body.visuals}
        for _collar_elem in ("threaded_collar", "collar_ring"):
            if _collar_elem in _body_visual_names:
                ctx.allow_overlap(
                    grip, body, elem_a="pistol_grip_body", elem_b=_collar_elem,
                    reason="The grip plunger/linkage nests over the valve collar at the dome.",
                )
        ctx.check(
            "grip_mount is FIXED, trigger_pull is REVOLUTE +Y off the grip (2-link chain)",
            grip_mount.articulation_type == ArticulationType.FIXED
            and trigger_pull.articulation_type == ArticulationType.REVOLUTE
            and abs(trigger_pull.axis[1]) > 0.9
            and trigger_pull.parent == "pistol_grip",
            details=f"grip_mount={grip_mount.articulation_type}, "
            f"trigger_pull={trigger_pull.articulation_type}/{trigger_pull.axis}, "
            f"trigger parent={trigger_pull.parent}",
        )
        rest_mn, rest_mx = ctx.part_world_aabb(trigger)
        with ctx.pose({trigger_pull: 0.26 * r.actuator_press_scale}):
            pull_mn, pull_mx = ctx.part_world_aabb(trigger)
        ctx.check(
            "trigger swings when pulled",
            abs(pull_mn[0] - rest_mn[0]) > 0.006,
            details=f"rest_min_x={rest_mn[0]:.4f}, pulled_min_x={pull_mn[0]:.4f}",
        )

    elif r.actuator == "fan_spin_cap":
        stem = object_model.get_part("fan_cap_stem")
        head = object_model.get_part("fan_cap")
        fan_press = object_model.get_articulation("fan_cap_press")
        fan_twist = object_model.get_articulation("fan_cap_twist")
        ctx.allow_overlap(
            stem, body, elem_a="fan_cap_stem", elem_b="can_body",
            reason="The fan-cap stem sleeve is seated over the central valve stem.",
        )
        ctx.check(
            "fan_cap_press PRISMATIC -Z + fan_cap_twist REVOLUTE +Z off the stem (2-link)",
            fan_press.articulation_type == ArticulationType.PRISMATIC
            and fan_press.axis[2] < -0.99
            and fan_twist.articulation_type == ArticulationType.REVOLUTE
            and abs(fan_twist.axis[2]) > 0.99
            and fan_twist.parent == "fan_cap_stem",
            details=f"press={fan_press.axis}, twist={fan_twist.axis}, "
            f"twist parent={fan_twist.parent}",
        )
        head_rest_z = ctx.part_world_position(head)[2]
        with ctx.pose({fan_press: r.press_travel}):
            head_down_z = ctx.part_world_position(head)[2]
        ctx.check(
            "fan head presses down with the stem",
            head_rest_z - head_down_z > r.press_travel * 0.6,
            details=f"rest={head_rest_z:.4f}, pressed={head_down_z:.4f}",
        )
        mn0, mx0 = ctx.part_world_aabb(head)
        with ctx.pose({fan_twist: 1.5708}):
            mn90, mx90 = ctx.part_world_aabb(head)
        ctx.check(
            "fan twist rotates the oval (wider X at rest, wider Y at 90deg)",
            (mx0[0] - mn0[0]) > (mx0[1] - mn0[1])
            and (mx90[1] - mn90[1]) > (mx90[0] - mn90[0]),
            details=f"rest dx/dy={mx0[0]-mn0[0]:.4f}/{mx0[1]-mn0[1]:.4f}, "
            f"90 dx/dy={mx90[0]-mn90[0]:.4f}/{mx90[1]-mn90[1]:.4f}",
        )

    # ---- closure cap: action + captured-fit ----
    if r.closure_cap == "lift_off_cap":
        cap = object_model.get_part("dust_cap")
        cap_lift = object_model.get_articulation("cap_lift")
        ctx.allow_isolated_part(
            cap,
            reason="dust cap lifts off the can top and loses body contact",
        )
        _allow_cap_over_actuator(ctx, object_model, r, cap, "dust_cap", body)
        ctx.check(
            "cap_lift is PRISMATIC +Z",
            cap_lift.articulation_type == ArticulationType.PRISMATIC
            and cap_lift.axis[2] > 0.99,
            details=f"axis={cap_lift.axis}, type={cap_lift.articulation_type}",
        )
        actuator_top = _actuator_top_world(ctx, object_model, r)
        # Use AABB center for the lift/lateral checks (the cap link frame is
        # intentionally off-axis on the seat wall, so part_world_position is not
        # on the can axis).
        rest_mn, rest_mx = ctx.part_world_aabb(cap)
        rest_cx = (rest_mn[0] + rest_mx[0]) / 2.0
        rest_cy = (rest_mn[1] + rest_mx[1]) / 2.0
        rest_cz = (rest_mn[2] + rest_mx[2]) / 2.0
        with ctx.pose({cap_lift: r.cap_lift_travel}):
            up_mn, up_mx = ctx.part_world_aabb(cap)
        up_cx = (up_mn[0] + up_mx[0]) / 2.0
        up_cy = (up_mn[1] + up_mx[1]) / 2.0
        up_cz = (up_mn[2] + up_mx[2]) / 2.0
        ctx.check(
            "dust cap lifts straight up, clearing the actuator",
            up_cz - rest_cz > r.cap_lift_travel * 0.7
            and up_mn[2] > actuator_top - 0.002
            and abs(up_cx - rest_cx) < 0.003
            and abs(up_cy - rest_cy) < 0.003,
            details=f"rest_cz={rest_cz:.4f}, up_cz={up_cz:.4f}, "
            f"up_min_z={up_mn[2]:.4f}, actuator_top={actuator_top:.4f}, "
            f"drift=({up_cx-rest_cx:.4f},{up_cy-rest_cy:.4f})",
        )

    elif r.closure_cap == "flip_top_cap":
        cap = object_model.get_part("flip_cap")
        hinge = object_model.get_articulation("cap_hinge")
        ctx.allow_overlap(
            cap, body, elem_a="flip_cap", elem_b="can_body",
            reason="Flip-top cap skirt sleeves over the can shoulder when closed.",
        )
        for i in range(2):
            ctx.allow_overlap(
                body, cap, elem_a=f"hinge_ear_{i}", elem_b="flip_cap",
                reason=f"Hinge ear {i} passes through the cap skirt as a pivot post.",
            )
        _allow_cap_over_actuator(ctx, object_model, r, cap, "flip_cap", body)
        ctx.check(
            "cap_hinge is REVOLUTE +X",
            hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[0]) > 0.9,
            details=f"axis={hinge.axis}, type={hinge.articulation_type}",
        )
        ctx.check(
            "two hinge ear visuals exist on the body",
            len([v for v in body.visuals if v.name.startswith("hinge_ear_")]) >= 2,
            details="hinge ears missing",
        )
        # A tall cap pivoting at the rear rim swings its body up and BACK (-Y),
        # uncovering the mouth. The AABB centroid moving rearward (and the front
        # +Y mouth edge retracting toward the hinge) are the reliable "opening"
        # signals (a very tall cap's AABB max_z barely changes).
        rmn, rmx = ctx.part_world_aabb(cap)
        rest_cy = (rmn[1] + rmx[1]) / 2.0
        rest_front_y = rmx[1]
        with ctx.pose({hinge: 1.6}):
            omn, omx = ctx.part_world_aabb(cap)
        open_cy = (omn[1] + omx[1]) / 2.0
        open_front_y = omx[1]
        ctx.check(
            "flip cap opens (swings rearward, mouth edge retracts off the can top)",
            open_cy < rest_cy - 0.010 and open_front_y < rest_front_y - 0.010,
            details=f"rest_cy={rest_cy:.4f}->open_cy={open_cy:.4f}, "
            f"rest_front_y={rest_front_y:.4f}->open_front_y={open_front_y:.4f}",
        )

    elif r.closure_cap == "screw_cap":
        carrier = object_model.get_part("cap_carrier")
        cap = object_model.get_part("screw_cap")
        unscrew = object_model.get_articulation("cap_unscrew")
        cap_lift = object_model.get_articulation("cap_lift")
        ctx.allow_isolated_part(
            cap,
            reason="screw cap unscrews off the can and loses body contact",
        )
        ctx.allow_overlap(
            cap, body, elem_a="screw_cap", elem_b="threaded_collar",
            reason="Screw cap bore engages the collar thread ridges (threaded fit).",
        )
        # The threaded collar wraps the central valve cup; the actuator seated on
        # the same valve passes through / nests in the collar bore (captured fit).
        _collar_actuator_overlaps = {
            "press_button": [("spray_nozzle", "spray_nozzle")],
            "trigger_lever": [("trigger_lever", "trigger_lever")],
            "pistol_grip": [("pistol_grip", "pistol_grip_body")],
            "fan_spin_cap": [("fan_cap_stem", "fan_cap_stem"), ("fan_cap", "fan_cap")],
        }[r.actuator]
        for pname, elem in _collar_actuator_overlaps:
            try:
                other = object_model.get_part(pname)
            except Exception:
                continue
            ctx.allow_overlap(
                body, other, elem_a="threaded_collar", elem_b=elem,
                reason="The actuator seated on the valve nests in the threaded collar bore.",
            )
        _allow_cap_over_actuator(ctx, object_model, r, cap, "screw_cap", body)
        ctx.check(
            "cap carrier is massless (no visuals)",
            len(carrier.visuals) == 0,
            details=f"carrier visuals={len(carrier.visuals)}",
        )
        ctx.check(
            "threaded collar visual exists on the body",
            body.get_visual("threaded_collar") is not None,
            details="threaded_collar visual missing",
        )
        ctx.check(
            "cap_unscrew CONTINUOUS +Z, cap_lift PRISMATIC +Z via carrier",
            unscrew.articulation_type == ArticulationType.CONTINUOUS
            and abs(unscrew.axis[2]) > 0.99
            and cap_lift.articulation_type == ArticulationType.PRISMATIC
            and cap_lift.axis[2] > 0.99
            and cap_lift.parent == "cap_carrier",
            details=f"unscrew={unscrew.articulation_type}/{unscrew.axis}, "
            f"lift={cap_lift.articulation_type}/{cap_lift.axis}, "
            f"lift parent={cap_lift.parent}",
        )
        rest = ctx.part_world_position(cap)
        with ctx.pose({unscrew: math.pi}):
            half = ctx.part_world_position(cap)
        ctx.check(
            "half-turn preserves cap center before lift",
            abs(half[0] - rest[0]) < 0.005 and abs(half[2] - rest[2]) < 0.005,
            details=f"rest={rest}, half={half}",
        )
        with ctx.pose({unscrew: math.pi, cap_lift: r.cap_lift_travel}):
            up = ctx.part_world_position(cap)
        ctx.check(
            "screw cap lifts upward after unscrewing",
            up[2] - rest[2] > r.cap_lift_travel * 0.8,
            details=f"rest_z={rest[2]:.4f}, up_z={up[2]:.4f}",
        )

    elif r.closure_cap == "no_cap_collar":
        lock_tab = object_model.get_part("lock_tab")
        tab_slide = object_model.get_articulation("tab_slide")
        part_names = [p.name for p in object_model.parts]
        ctx.check(
            "no cap part exists (capless safety-collar design)",
            "dust_cap" not in part_names
            and "flip_cap" not in part_names
            and "screw_cap" not in part_names,
            details=f"parts={part_names}",
        )
        ctx.check(
            "collar ring + 6 grip ridges are visuals on the body",
            body.get_visual("collar_ring") is not None
            and len([v for v in body.visuals if v.name.startswith("grip_ridge_")]) == 6,
            details="collar/grip ridges missing",
        )
        ctx.allow_overlap(
            lock_tab, body, elem_a="lock_tab", elem_b="collar_ring",
            reason="Lock tab capture tongue slides inside the collar annulus groove.",
        )
        tab_rest = ctx.part_world_position(lock_tab)
        with ctx.pose({tab_slide: 0.0165}):
            tab_locked = ctx.part_world_position(lock_tab)
        ctx.check(
            "tab_slide is PRISMATIC -Y (slides laterally, not vertically)",
            tab_slide.articulation_type == ArticulationType.PRISMATIC
            and abs(tab_slide.axis[1]) > 0.9
            and abs(tab_locked[2] - tab_rest[2]) < 0.001
            and abs(tab_locked[1] - tab_rest[1]) > 0.010,
            details=f"axis={tab_slide.axis}, rest={tab_rest}, locked={tab_locked}",
        )

    # ---- at least one non-fixed joint exists ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()


def _actuator_top_world(ctx, object_model, r) -> float:
    """World z of the tallest actuator point (for cap-clearance checks)."""
    actuator_parts = {
        "press_button": ["spray_nozzle"],
        "trigger_lever": ["trigger_lever"],
        "pistol_grip": ["pistol_grip"],
        "fan_spin_cap": ["fan_cap_stem", "fan_cap"],
    }[r.actuator]
    top = 0.0
    for pname in actuator_parts:
        try:
            _, mx = ctx.part_world_aabb(object_model.get_part(pname))
            top = max(top, mx[2])
        except Exception:
            pass
    # trigger housing is a body visual, not a part; account for it.
    if r.actuator == "trigger_lever":
        try:
            _, mx = ctx.part_element_world_aabb(object_model.get_part("can_body"), elem="trigger_housing")
            top = max(top, mx[2])
        except Exception:
            pass
    return top


def _allow_cap_over_actuator(ctx, object_model, r, cap, cap_elem, body) -> None:
    """Allow the seated cap to enclose the actuator + body shoulder at rest."""
    ctx.allow_overlap(
        cap, body, elem_a=cap_elem, elem_b="can_body",
        reason="The cap sleeves down over the can top shoulder when seated.",
    )
    ctx.allow_overlap(
        cap, body, elem_a=cap_elem, elem_b="label_band",
        reason="The cap skirt sleeves down over the upper label band region when seated.",
    )
    actuator_overlaps = {
        "press_button": [("spray_nozzle", "spray_nozzle")],
        "trigger_lever": [("trigger_lever", "trigger_lever")],
        "pistol_grip": [("pistol_grip", "pistol_grip_body")],
        "fan_spin_cap": [("fan_cap_stem", "fan_cap_stem"), ("fan_cap", "fan_cap")],
    }[r.actuator]
    for pname, elem in actuator_overlaps:
        try:
            other = object_model.get_part(pname)
        except Exception:
            continue
        ctx.allow_overlap(
            cap, other, elem_a=cap_elem, elem_b=elem,
            reason="The seated cap encloses the actuator when both are at rest.",
        )
    # trigger housing is a body visual.
    if r.actuator == "trigger_lever":
        ctx.allow_overlap(
            cap, body, elem_a=cap_elem, elem_b="trigger_housing",
            reason="The seated cap sleeves over the trigger housing.",
        )
